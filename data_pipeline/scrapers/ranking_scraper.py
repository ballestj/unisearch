"""
University Ranking Scrapers

Multi-source web scrapers for university ranking data.
"""

import os
import time
import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

logger = logging.getLogger(__name__)


class BaseRankingScraper:
    """Base class for ranking scrapers."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': os.getenv('USER_AGENT', 'UniSearch/1.0 Educational Research')
        })
        self.delay = float(os.getenv('SCRAPING_DELAY', '1'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
    
    def make_request(self, url: str, retries: int = 0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic."""
        try:
            time.sleep(self.delay)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if retries < self.max_retries:
                logger.warning(f"Request failed, retrying {retries + 1}/{self.max_retries}: {e}")
                time.sleep(self.delay * (retries + 1))
                return self.make_request(url, retries + 1)
            logger.error(f"Request failed after {self.max_retries} retries: {e}")
            return None


class QSRankingScraper(BaseRankingScraper):
    """Scraper for QS World University Rankings."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.topuniversities.com"
    
    def scrape_rankings(self, year: int = 2024) -> List[Dict[str, Any]]:
        """
        Scrape QS rankings for a specific year.
        
        Note: This is a simplified example. In production, you'd need to handle
        JavaScript-heavy sites with Selenium and respect robots.txt
        """
        url = f"{self.base_url}/world-university-rankings/{year}"
        response = self.make_request(url)
        
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        universities = []
        
        # This is pseudocode - actual selectors would need to be determined
        # by inspecting the QS website structure
        ranking_items = soup.find_all('div', class_='ranking-item')
        
        for item in ranking_items:
            try:
                university_data = {
                    'name': item.find('h3', class_='university-name').text.strip(),
                    'rank': self._parse_rank(item.find('span', class_='rank').text),
                    'score': float(item.find('span', class_='score').text),
                    'country': item.find('span', class_='country').text.strip(),
                    'location': item.find('span', class_='location').text.strip(),
                    'source': 'QS',
                    'year': year
                }
                universities.append(university_data)
            except Exception as e:
                logger.warning(f"Error parsing QS ranking item: {e}")
                continue
        
        logger.info(f"Scraped {len(universities)} universities from QS rankings")
        return universities
    
    def _parse_rank(self, rank_text: str) -> Optional[int]:
        """Parse ranking text to integer."""
        try:
            # Handle formats like "1", "=15", "51-100"
            rank_text = rank_text.strip().replace('=', '')
            if '-' in rank_text:
                return int(rank_text.split('-')[0])
            return int(rank_text)
        except ValueError:
            return None


class THERankingScraper(BaseRankingScraper):
    """Scraper for Times Higher Education Rankings."""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.timeshighereducation.com"
    
    def scrape_rankings(self, year: int = 2024) -> List[Dict[str, Any]]:
        """Scrape THE world university rankings."""
        # THE often requires JavaScript rendering
        return self._scrape_with_selenium(year)
    
    def _scrape_with_selenium(self, year: int) -> List[Dict[str, Any]]:
        """Use Selenium for JavaScript-heavy sites."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        universities = []
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            url = f"{self.base_url}/world-university-rankings/{year}/world-ranking"
            driver.get(url)
            
            # Wait for rankings to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ranking-item')))
            
            # Scroll to load more results (if infinite scroll)
            self._scroll_to_load_all(driver)
            
            # Extract university data
            ranking_elements = driver.find_elements(By.CLASS_NAME, 'ranking-item')
            
            for element in ranking_elements:
                try:
                    university_data = {
                        'name': element.find_element(By.CLASS_NAME, 'university-name').text,
                        'rank': self._parse_rank(element.find_element(By.CLASS_NAME, 'rank').text),
                        'score': float(element.find_element(By.CLASS_NAME, 'score').text),
                        'country': element.find_element(By.CLASS_NAME, 'country').text,
                        'source': 'THE',
                        'year': year
                    }
                    universities.append(university_data)
                except Exception as e:
                    logger.warning(f"Error parsing THE ranking item: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping THE rankings: {e}")
        finally:
            if 'driver' in locals():
                driver.quit()
        
        logger.info(f"Scraped {len(universities)} universities from THE rankings")
        return universities
    
    def _scroll_to_load_all(self, driver):
        """Scroll page to trigger infinite scroll loading."""
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height


class CostDataScraper(BaseRankingScraper):
    """Scraper for university cost data from multiple sources."""
    
    def scrape_numbeo_costs(self, cities: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Scrape cost of living data from Numbeo API.
        
        Note: Requires API key from Numbeo
        """
        api_key = os.getenv('NUMBEO_API_KEY')
        if not api_key:
            logger.warning("Numbeo API key not found")
            return {}
        
        cost_data = {}
        
        for city in cities:
            try:
                url = f"https://www.numbeo.com/api/city_prices"
                params = {
                    'api_key': api_key,
                    'query': city,
                    'format': 'json'
                }
                
                response = self.make_request(url)
                if response:
                    data = response.json()
                    cost_data[city] = {
                        'rent_1br_center': data.get('rent_1br_center', 0),
                        'meal_inexpensive': data.get('meal_inexpensive', 0),
                        'public_transport': data.get('public_transport', 0),
                        'utilities': data.get('utilities', 0)
                    }
                
            except Exception as e:
                logger.warning(f"Error fetching cost data for {city}: {e}")
                continue
        
        return cost_data
    
    def scrape_university_tuition(self, university_urls: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Scrape tuition information from university websites.
        
        This is highly site-specific and would need custom parsers
        for each university website.
        """
        tuition_data = {}
        
        for url in university_urls:
            try:
                response = self.make_request(url)
                if not response:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Generic patterns to look for tuition information
                tuition_keywords = ['tuition', 'fees', 'cost', 'price', 'international students']
                currency_patterns = ['$', '€', '£', 'USD', 'EUR', 'GBP']
                
                # This would need sophisticated parsing logic
                # for each university's specific format
                tuition_info = self._extract_tuition_info(soup, tuition_keywords, currency_patterns)
                
                if tuition_info:
                    tuition_data[url] = tuition_info
                
            except Exception as e:
                logger.warning(f"Error scraping tuition from {url}: {e}")
                continue
        
        return tuition_data
    
    def _extract_tuition_info(self, soup: BeautifulSoup, keywords: List[str], currencies: List[str]) -> Dict[str, Any]:
        """Extract tuition information from HTML."""
        # Simplified extraction logic
        # In production, this would be much more sophisticated
        tuition_info = {}
        
        text = soup.get_text().lower()
        
        # Look for price patterns
        import re
        price_pattern = r'[€$£]\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        prices = re.findall(price_pattern, text)
        
        if prices:
            tuition_info['prices_found'] = prices
            tuition_info['estimated_tuition'] = prices[0]  # Take first price found
        
        return tuition_info


class UniversityDataAggregator:
    """Aggregate data from multiple scraping sources."""
    
    def __init__(self):
        self.qs_scraper = QSRankingScraper()
        self.the_scraper = THERankingScraper()
        self.cost_scraper = CostDataScraper()
    
    def aggregate_all_data(self, year: int = 2024) -> pd.DataFrame:
        """
        Aggregate university data from all sources.
        """
        logger.info("Starting comprehensive data aggregation...")
        
        # Scrape ranking data
        qs_data = self.qs_scraper.scrape_rankings(year)
        the_data = self.the_scraper.scrape_rankings(year)
        
        # Convert to DataFrames
        qs_df = pd.DataFrame(qs_data)
        the_df = pd.DataFrame(the_data)
        
        # Merge ranking data
        merged_df = self._merge_ranking_data(qs_df, the_df)
        
        # Add cost data
        if not merged_df.empty:
            cities = merged_df['location'].unique().tolist()
            cost_data = self.cost_scraper.scrape_numbeo_costs(cities)
            merged_df = self._add_cost_data(merged_df, cost_data)
        
        logger.info(f"Aggregation complete. Final dataset: {len(merged_df)} universities")
        return merged_df
    
    def _merge_ranking_data(self, qs_df: pd.DataFrame, the_df: pd.DataFrame) -> pd.DataFrame:
        """Merge QS and THE ranking data."""
        if qs_df.empty and the_df.empty:
            return pd.DataFrame()
        
        if qs_df.empty:
            return the_df
        
        if the_df.empty:
            return qs_df
        
        # Merge on university name (fuzzy matching would be better)
        merged = pd.merge(
            qs_df, the_df,
            on=['name', 'country'],
            how='outer',
            suffixes=('_qs', '_the')
        )
        
        return merged
    
    def _add_cost_data(self, df: pd.DataFrame, cost_data: Dict[str, Dict[str, float]]) -> pd.DataFrame:
        """Add cost of living data to university dataframe."""
        # Map cities to cost data
        df['monthly_cost_estimate'] = df['location'].map(
            lambda city: sum(cost_data.get(city, {}).values()) if city in cost_data else None
        )
        
        return df


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    aggregator = UniversityDataAggregator()
    university_data = aggregator.aggregate_all_data(2024)
    
    # Save to CSV
    output_file = "scraped_university_data.csv"
    university_data.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")