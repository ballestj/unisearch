"""
Data Cleaning and Processing

Clean, standardize, and validate university data from multiple sources.
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple, Any
from thefuzz import fuzz, process
import logging

logger = logging.getLogger(__name__)


class UniversityDataCleaner:
    """Clean and standardize university data."""
    
    def __init__(self):
        self.country_mappings = self._load_country_mappings()
        self.university_name_cache = {}
        
    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Complete data cleaning pipeline.
        """
        logger.info(f"Starting data cleaning for {len(df)} records")
        
        # Create a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # Clean university names
        cleaned_df['name'] = cleaned_df['name'].apply(self.clean_university_name)
        
        # Clean and standardize countries
        cleaned_df['country'] = cleaned_df['country'].apply(self.clean_country_name)
        
        # Clean cities
        cleaned_df['city'] = cleaned_df['city'].apply(self.clean_city_name)
        
        # Clean rankings
        cleaned_df = self._clean_rankings(cleaned_df)
        
        # Clean scores and metrics
        cleaned_df = self._clean_scores(cleaned_df)
        
        # Handle duplicates
        cleaned_df = self._handle_duplicates(cleaned_df)
        
        # Validate data
        cleaned_df = self._validate_data(cleaned_df)
        
        logger.info(f"Data cleaning complete. {len(cleaned_df)} records remain")
        return cleaned_df
    
    def clean_university_name(self, name: str) -> str:
        """
        Clean and standardize university names.
        """
        if pd.isna(name) or not isinstance(name, str):
            return ""
        
        # Cache for performance
        if name in self.university_name_cache:
            return self.university_name_cache[name]
        
        original_name = name
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())
        
        # Common abbreviation expansions
        abbreviations = {
            r'\bUniv\b\.?': 'University',
            r'\bU\b\.?(?=\s)': 'University',
            r'\bInst\b\.?': 'Institute',
            r'\bTech\b\.?': 'Technology',
            r'\bColl\b\.?': 'College',
            r'\bSci\b\.?': 'Science',
            r'\bEng\b\.?': 'Engineering',
            r'\bMed\b\.?': 'Medical',
            r'\bBus\b\.?': 'Business',
            r'\bInt\'?l\b\.?': 'International',
            r'\bNat\'?l\b\.?': 'National',
            r'\bSt\b\.': 'Saint',
            r'\bMt\b\.': 'Mount'
        }
        
        for pattern, replacement in abbreviations.items():
            name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)
        
        # Remove common suffixes that add noise
        noise_patterns = [
            r'\s*\([^)]*\)$',  # Remove parenthetical info at end
            r'\s*-\s*[A-Z]{2,}$',  # Remove country codes like "- USA"
            r'\s*,\s*[A-Z]{2,}$',  # Remove country codes like ", UK"
        ]
        
        for pattern in noise_patterns:
            name = re.sub(pattern, '', name)
        
        # Standardize "The" prefix
        name = re.sub(r'^The\s+', '', name)
        
        # Title case with proper handling of prepositions
        name = self._title_case_university_name(name)
        
        # Cache the result
        self.university_name_cache[original_name] = name
        
        return name
    
    def clean_country_name(self, country: str) -> str:
        """
        Clean and standardize country names.
        """
        if pd.isna(country) or not isinstance(country, str):
            return ""
        
        country = country.strip()
        
        # Use mapping if available
        if country in self.country_mappings:
            return self.country_mappings[country]
        
        # Basic cleaning
        country = re.sub(r'\s+', ' ', country)
        
        # Common country name standardizations
        standardizations = {
            r'\bUSA?\b': 'United States',
            r'\bUK\b': 'United Kingdom',
            r'\bU\.?S\.?A\.?\b': 'United States',
            r'\bU\.?K\.?\b': 'United Kingdom',
        }
        
        for pattern, replacement in standardizations.items():
            country = re.sub(pattern, replacement, country, flags=re.IGNORECASE)
        
        return country.title()
    
    def clean_city_name(self, city: str) -> str:
        """
        Clean and standardize city names.
        """
        if pd.isna(city) or not isinstance(city, str):
            return ""
        
        # Remove country/state info in parentheses
        city = re.sub(r'\s*\([^)]*\)$', '', city)
        
        # Remove state/province suffixes
        city = re.sub(r',\s*[A-Z]{2,}$', '', city)
        
        # Clean whitespace
        city = re.sub(r'\s+', ' ', city.strip())
        
        return city.title()
    
    def _clean_rankings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean ranking columns."""
        ranking_columns = ['rank', 'qs_rank', 'the_rank', 'arwu_rank', 'us_news_rank']
        
        for col in ranking_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._parse_ranking)
        
        return df
    
    def _parse_ranking(self, rank_value: Any) -> Optional[int]:
        """Parse various ranking formats to integer."""
        if pd.isna(rank_value):
            return None
        
        rank_str = str(rank_value).strip()
        
        # Handle "Not ranked" or similar
        if any(word in rank_str.lower() for word in ['not', 'unranked', 'n/a', 'na']):
            return None
        
        # Remove common prefixes
        rank_str = re.sub(r'^[=#+]', '', rank_str)
        
        # Handle ranges (take the lower bound)
        if '-' in rank_str:
            rank_str = rank_str.split('-')[0]
        
        # Handle plus signs (501+ becomes 501)
        rank_str = re.sub(r'\+.*$', '', rank_str)
        
        # Extract number
        match = re.search(r'\d+', rank_str)
        if match:
            return int(match.group())
        
        return None
    
    def _clean_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean score and metric columns."""
        score_columns = [
            'score', 'qs_score', 'the_score', 'academic_rigor', 
            'student_life', 'cultural_diversity', 'campus_safety',
            'research_quality', 'overall_quality'
        ]
        
        for col in score_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._parse_score)
                # Ensure scores are in 0-10 range
                if col in ['academic_rigor', 'student_life', 'cultural_diversity', 'campus_safety']:
                    df[col] = df[col].apply(lambda x: min(10, max(0, x)) if pd.notna(x) else x)
        
        return df
    
    def _parse_score(self, score_value: Any) -> Optional[float]:
        """Parse score values to float."""
        if pd.isna(score_value):
            return None
        
        score_str = str(score_value).strip()
        
        # Handle percentages
        if '%' in score_str:
            score_str = score_str.replace('%', '')
            try:
                return float(score_str) / 10  # Convert to 0-10 scale
            except ValueError:
                return None
        
        # Extract number
        match = re.search(r'\d+\.?\d*', score_str)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        
        return None
    
    def _handle_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify and merge duplicate universities.
        """
        logger.info("Handling duplicate universities...")
        
        # Group by similar names and same country
        duplicates = []
        processed = set()
        
        for idx, row in df.iterrows():
            if idx in processed:
                continue
            
            name = row['name']
            country = row['country']
            
            # Find similar universities
            similar_indices = []
            for other_idx, other_row in df.iterrows():
                if other_idx in processed or other_idx == idx:
                    continue
                
                # Check if same country and similar name
                if (other_row['country'] == country and 
                    fuzz.ratio(name.lower(), other_row['name'].lower()) > 85):
                    similar_indices.append(other_idx)
            
            if similar_indices:
                group = [idx] + similar_indices
                duplicates.append(group)
                processed.update(group)
            else:
                processed.add(idx)
        
        # Merge duplicates
        for duplicate_group in duplicates:
            merged_row = self._merge_duplicate_rows(df.loc[duplicate_group])
            # Keep the first row, update it with merged data
            first_idx = duplicate_group[0]
            for col in merged_row.index:
                df.at[first_idx, col] = merged_row[col]
            
            # Drop other rows
            df = df.drop(duplicate_group[1:])
        
        logger.info(f"Merged {len(duplicates)} duplicate groups")
        return df.reset_index(drop=True)
    
    def _merge_duplicate_rows(self, rows: pd.DataFrame) -> pd.Series:
        """
        Merge multiple rows of the same university.
        """
        merged = rows.iloc[0].copy()
        
        # For text fields, use the longest/most complete value
        text_fields = ['name', 'city', 'country', 'website_url']
        for field in text_fields:
            if field in rows.columns:
                non_null_values = rows[field].dropna()
                if not non_null_values.empty:
                    # Use the longest value
                    merged[field] = max(non_null_values, key=len)
        
        # For numeric fields, use the average of non-null values
        numeric_fields = [
            'academic_rigor', 'student_life', 'cultural_diversity', 
            'campus_safety', 'research_quality', 'overall_quality'
        ]
        for field in numeric_fields:
            if field in rows.columns:
                non_null_values = rows[field].dropna()
                if not non_null_values.empty:
                    merged[field] = non_null_values.mean()
        
        # For rankings, use the best (lowest) rank
        ranking_fields = ['qs_rank', 'the_rank', 'arwu_rank']
        for field in ranking_fields:
            if field in rows.columns:
                non_null_values = rows[field].dropna()
                if not non_null_values.empty:
                    merged[field] = non_null_values.min()
        
        # For scores, use the average
        score_fields = ['qs_score', 'the_score']
        for field in score_fields:
            if field in rows.columns:
                non_null_values = rows[field].dropna()
                if not non_null_values.empty:
                    merged[field] = non_null_values.mean()
        
        return merged
    
    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate data quality and remove invalid records.
        """
        logger.info("Validating data quality...")
        
        initial_count = len(df)
        
        # Remove rows with missing essential data
        df = df.dropna(subset=['name', 'country'])
        
        # Remove rows with invalid rankings (negative or zero)
        ranking_columns = ['qs_rank', 'the_rank', 'arwu_rank']
        for col in ranking_columns:
            if col in df.columns:
                df = df[~((df[col] <= 0) & df[col].notna())]
        
        # Remove rows with invalid scores (outside 0-10 range for our metrics)
        metric_columns = ['academic_rigor', 'student_life', 'cultural_diversity', 'campus_safety']
        for col in metric_columns:
            if col in df.columns:
                df = df[~((df[col] < 0) | (df[col] > 10)) | df[col].isna()]
        
        # Remove obviously invalid names
        df = df[~df['name'].str.len() < 3]
        df = df[~df['name'].str.contains(r'^\d+$', na=False)]  # Pure numbers
        
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} invalid records during validation")
        
        return df
    
    def _title_case_university_name(self, name: str) -> str:
        """Apply proper title case to university names."""
        # Words that should stay lowercase (except at beginning)
        lowercase_words = {
            'of', 'the', 'and', 'in', 'at', 'by', 'for', 'to', 'into', 
            'with', 'from', 'up', 'on', 'off', 'over', 'under'
        }
        
        words = name.split()
        if not words:
            return name
        
        # First word is always capitalized
        result = [words[0].capitalize()]
        
        for word in words[1:]:
            if word.lower() in lowercase_words:
                result.append(word.lower())
            else:
                result.append(word.capitalize())
        
        return ' '.join(result)
    
    def _load_country_mappings(self) -> Dict[str, str]:
        """Load country name mappings for standardization."""
        return {
            'US': 'United States',
            'USA': 'United States',
            'United States of America': 'United States',
            'UK': 'United Kingdom',
            'Great Britain': 'United Kingdom',
            'England': 'United Kingdom',
            'Scotland': 'United Kingdom',
            'Wales': 'United Kingdom',
            'Northern Ireland': 'United Kingdom',
            'Russia': 'Russian Federation',
            'South Korea': 'Republic of Korea',
            'North Korea': 'Democratic People\'s Republic of Korea',
            'Iran': 'Islamic Republic of Iran',
            'Vietnam': 'Viet Nam',
            'Czech Republic': 'Czechia',
            'Macedonia': 'North Macedonia',
            'Myanmar': 'Myanmar (Burma)',
            'Congo': 'Democratic Republic of the Congo',
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Load sample data
    try:
        df = pd.read_csv('scraped_university_data.csv')
        cleaner = UniversityDataCleaner()
        cleaned_df = cleaner.clean_dataset(df)
        
        # Save cleaned data
        cleaned_df.to_csv('cleaned_university_data.csv', index=False)
        print(f"Cleaned data saved. Records: {len(cleaned_df)}")
        
    except FileNotFoundError:
        print("No input data file found. Run the scraper first.")
        