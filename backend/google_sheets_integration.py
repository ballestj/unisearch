import sqlite3
import pandas as pd
import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from thefuzz import fuzz
import re
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UniversityDataIntegrator:
    """Integrates Google Sheets feedback data with QS rankings database."""
    
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        self.service = None
        
    def authenticate_google_sheets(self):
        """Authenticate with Google Sheets API."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        
        # If there are no (valid) credentials available, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes)
                creds = flow.run_local_server(port=8080)
            
            # Save the credentials for the next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('sheets', 'v4', credentials=creds)
        logger.info("Successfully authenticated with Google Sheets API")
    
    def standardize_university_name(self, name: str) -> str:
        """Enhanced university name standardization."""
        if not name or pd.isna(name):
            return ""
            
        # Remove extra whitespace and convert to string
        name = str(name).strip()
        
        # Common variations and their standardized forms
        replacements = {
            # University variations
            r'\buniv\b\.?': 'University',
            r'\buniversity of\b': 'University of',
            r'\bu\.?\s+of\b': 'University of',
            r'\bu\.\s*$': 'University',
            r'\buniv\.\s*$': 'University',
            
            # Institute variations
            r'\binst\b\.?': 'Institute',
            r'\binstitute of\b': 'Institute of',
            
            # Technology variations
            r'\btech\b\.?': 'Technology',
            r'\btechnical\b': 'Technology',
            
            # College variations
            r'\bcoll\b\.?': 'College',
            r'\bcollege of\b': 'College of',
            
            # State variations
            r'\bstate\s+u\b\.?': 'State University',
            r'\bst\.\s+u\b\.?': 'State University',
        }
        
        # Apply replacements (case insensitive)
        for pattern, replacement in replacements.items():
            name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)
        
        # Remove common suffixes that might cause duplicates
        suffixes_to_remove = [
            r'\s*\([^)]*\)\s*$',  # Remove parenthetical content at end
            r'\s*-\s*.*$',        # Remove everything after dash
            r'\s*,\s*.*$',        # Remove everything after comma
        ]
        
        for suffix in suffixes_to_remove:
            name = re.sub(suffix, '', name)
        
        # Clean up spacing and capitalize properly
        name = ' '.join(name.split())  # Remove extra spaces
        
        # Proper title casing with exceptions
        exceptions = {'of', 'the', 'and', 'in', 'at', 'by', 'for', 'to', 'with', 'on'}
        words = name.split()
        
        for i, word in enumerate(words):
            if i == 0 or word.lower() not in exceptions:
                words[i] = word.capitalize()
            else:
                words[i] = word.lower()
        
        return ' '.join(words)
    
    def find_university_matches(self, feedback_universities: List[str], 
                              qs_universities: List[str]) -> Dict[str, str]:
        """Find matches between feedback and QS ranking universities using fuzzy matching."""
        matches = {}
        
        for feedback_uni in feedback_universities:
            if not feedback_uni:
                continue
                
            standardized_feedback = self.standardize_university_name(feedback_uni)
            best_match = None
            best_score = 0
            
            for qs_uni in qs_universities:
                standardized_qs = self.standardize_university_name(qs_uni)
                
                # Calculate similarity scores
                ratio = fuzz.ratio(standardized_feedback.lower(), standardized_qs.lower())
                partial = fuzz.partial_ratio(standardized_feedback.lower(), standardized_qs.lower())
                token_sort = fuzz.token_sort_ratio(standardized_feedback.lower(), standardized_qs.lower())
                token_set = fuzz.token_set_ratio(standardized_feedback.lower(), standardized_qs.lower())
                
                # Weighted average of different similarity measures
                combined_score = (ratio * 0.3 + partial * 0.2 + token_sort * 0.25 + token_set * 0.25)
                
                if combined_score > best_score and combined_score >= 80:  # Threshold for match
                    best_score = combined_score
                    best_match = standardized_qs
            
            if best_match:
                matches[standardized_feedback] = best_match
                logger.info(f"Matched '{feedback_uni}' -> '{best_match}' (score: {best_score:.1f})")
            else:
                logger.warning(f"No match found for '{feedback_uni}'")
        
        return matches
    
    def fetch_google_sheets_data(self, spreadsheet_id: str, range_name: str = 'Sheet1') -> pd.DataFrame:
        """Fetch data from Google Sheets."""
        if not self.service:
            self.authenticate_google_sheets()
        
        try:
            # Get the data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=range_name).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("No data found in Google Sheets")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(values[1:], columns=values[0])  # First row as headers
            logger.info(f"Fetched {len(df)} rows from Google Sheets")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Google Sheets data: {str(e)}")
            raise
    
    def process_feedback_data(self, feedback_df: pd.DataFrame) -> pd.DataFrame:
        """Process and clean the feedback data from Google Sheets."""
        if feedback_df.empty:
            return pd.DataFrame()
        
        # Standardize column names to match expected format
        column_mapping = {
            'Name of University': 'university_name',
            'City': 'city',
            'Overall Quality of Education': 'overall_quality',
            'Academic Rigor': 'academic_rigor',
            'Openness*': 'openness',
            'Cultural Diversity': 'cultural_diversity',
            'Overall Student Life': 'student_life',
            'Sense of Campus Safety/Security': 'campus_safety',
            'University Provided Accommodation': 'accommodation',
            'Language of Instruction': 'language',
            'Local Language Classes for Students': 'language_classes',
            'Accessibility/Disability Support Services Available': 'accessibility'
        }
        
        # Rename columns
        processed_df = feedback_df.rename(columns=column_mapping)
        
        # Clean and standardize university names
        processed_df['standardized_name'] = processed_df['university_name'].apply(
            self.standardize_university_name)
        
        # Convert numeric columns
        numeric_columns = ['overall_quality', 'academic_rigor', 'openness', 
                          'cultural_diversity', 'student_life', 'campus_safety']
        
        for col in numeric_columns:
            if col in processed_df.columns:
                processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')
        
        # Remove rows with missing university names
        processed_df = processed_df.dropna(subset=['standardized_name'])
        processed_df = processed_df[processed_df['standardized_name'] != '']
        
        logger.info(f"Processed {len(processed_df)} valid feedback entries")
        return processed_df
    
    def aggregate_feedback_by_university(self, feedback_df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate multiple feedback entries for the same university."""
        if feedback_df.empty:
            return pd.DataFrame()
        
        # Group by standardized name and aggregate
        numeric_columns = ['overall_quality', 'academic_rigor', 'openness', 
                          'cultural_diversity', 'student_life', 'campus_safety']
        
        # Calculate averages for numeric columns
        agg_dict = {col: 'mean' for col in numeric_columns if col in feedback_df.columns}
        
        # For categorical columns, take the most common value
        categorical_columns = ['city', 'accommodation', 'language', 'language_classes', 'accessibility']
        for col in categorical_columns:
            if col in feedback_df.columns:
                agg_dict[col] = 'first'
        
        aggregated = feedback_df.groupby('standardized_name').agg(agg_dict).round(2)
        # Add response count separately
        response_counts = feedback_df.groupby('standardized_name').size().reset_index(name='response_count')
        aggregated = aggregated.merge(response_counts, on='standardized_name', how='left')
        aggregated = aggregated.reset_index()
        
        logger.info(f"Aggregated feedback for {len(aggregated)} unique universities")
        return aggregated
    
    def load_qs_rankings_data(self, qs_csv_path: str) -> pd.DataFrame:
        """Load and process QS rankings data."""
        try:
            # Read QS rankings CSV
            qs_df = pd.read_csv(qs_csv_path, skiprows=4)
            
            # Set proper column names
            qs_df.columns = [
                'rank_2024', 'rank_2023', 'institution_name', 'location_code', 'location', 
                'size', 'focus', 'research', 'age_band', 'status', 'ar_score', 'ar_rank', 
                'er_score', 'er_rank', 'fsr_score', 'fsr_rank', 'cpf_score', 'cpf_rank', 
                'ifr_score', 'ifr_rank', 'isr_score', 'isr_rank', 'irn_score', 'irn_rank', 
                'ger_score', 'ger_rank', 'sus_score', 'sus_rank', 'overall_score'
            ]
            
            # Standardize university names
            qs_df['standardized_name'] = qs_df['institution_name'].apply(
                self.standardize_university_name)
            
            # Clean ranking data
            qs_df['clean_rank'] = qs_df['rank_2024'].apply(self.clean_qs_rank)
            
            # Use location as country directly, location_code as city
            qs_df['country'] = qs_df['location'].str.strip()
            qs_df['city'] = qs_df['location_code'].str.strip()
            
            logger.info(f"Loaded {len(qs_df)} QS ranking entries")
            return qs_df
            
        except Exception as e:
            logger.error(f"Error loading QS rankings data: {str(e)}")
            raise
    
    def clean_qs_rank(self, rank_str) -> Optional[int]:
        """Clean QS ranking values."""
        if pd.isna(rank_str):
            return None
        
        rank_str = str(rank_str).strip()
        
        # Handle different rank formats
        if rank_str.startswith('='):
            rank_str = rank_str[1:]
        
        if '-' in rank_str:
            rank_str = rank_str.split('-')[0]
        
        if '+' in rank_str:
            rank_str = rank_str.split('+')[0]
        
        try:
            return int(rank_str)
        except ValueError:
            return None
    
    def merge_data_sources(self, feedback_df: pd.DataFrame, qs_df: pd.DataFrame) -> pd.DataFrame:
        """Merge feedback data with QS rankings data."""
        if feedback_df.empty:
            logger.warning("No feedback data to merge")
            return qs_df
        
        # Find matches between feedback and QS universities
        feedback_unis = feedback_df['standardized_name'].unique().tolist()
        qs_unis = qs_df['standardized_name'].unique().tolist()
        
        matches = self.find_university_matches(feedback_unis, qs_unis)
        
        # Create mapping for merging
        feedback_df['qs_match_name'] = feedback_df['standardized_name'].map(matches)
        
        # Merge on matched names
        merged_df = qs_df.merge(
            feedback_df, 
            left_on='standardized_name', 
            right_on='qs_match_name', 
            how='left',
            suffixes=('_qs', '_feedback')
        )
        
        # For universities with feedback, use feedback data; otherwise use QS data
        for col in ['academic_rigor', 'cultural_diversity']:
            if f'{col}_feedback' in merged_df.columns:
                merged_df[col] = merged_df[f'{col}_feedback'].fillna(
                    merged_df[f'{col}_qs'] if f'{col}_qs' in merged_df.columns else 0
                )
        
        logger.info(f"Merged data: {len(merged_df)} universities total, "
                   f"{len(merged_df.dropna(subset=['qs_match_name']))} with feedback")
        
        return merged_df
    
    def update_database(self, merged_df: pd.DataFrame, db_path: str = 'universities.db'):
        """Update the SQLite database with merged data."""
        try:
            # Create database connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS universities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT,
                country TEXT,
                qs_rank INTEGER,
                overall_quality REAL,
                academic_rigor REAL,
                openness REAL,
                cultural_diversity REAL,
                student_life REAL,
                campus_safety REAL,
                accommodation TEXT,
                language TEXT,
                language_classes TEXT,
                accessibility TEXT,
                response_count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Clear existing data
            cursor.execute('DELETE FROM universities')
            
            # Insert merged data
            for _, row in merged_df.iterrows():
                cursor.execute('''
                INSERT INTO universities (
                    name, city, country, qs_rank, overall_quality, academic_rigor,
                    openness, cultural_diversity, student_life, campus_safety,
                    accommodation, language, language_classes, accessibility, response_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('standardized_name', row.get('institution_name', '')),
                    row.get('city', ''),
                    row.get('country', ''),
                    row.get('clean_rank'),
                    row.get('overall_quality'),
                    row.get('academic_rigor'),
                    row.get('openness'),
                    row.get('cultural_diversity'),
                    row.get('student_life'),
                    row.get('campus_safety'),
                    row.get('accommodation'),
                    row.get('language'),
                    row.get('language_classes'),
                    row.get('accessibility'),
                    row.get('response_count', 0)
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Successfully updated database with {len(merged_df)} universities")
            
        except Exception as e:
            logger.error(f"Error updating database: {str(e)}")
            raise
    
    def full_data_sync(self, spreadsheet_id: str, qs_csv_path: str, 
                      range_name: str = 'Sheet1'):
        """Perform a complete data synchronization."""
        logger.info("Starting full data synchronization...")
        
        try:
            # 1. Fetch Google Sheets feedback data
            logger.info("Fetching Google Sheets data...")
            feedback_df = self.fetch_google_sheets_data(spreadsheet_id, range_name)
            
            # 2. Process and aggregate feedback data
            logger.info("Processing feedback data...")
            processed_feedback = self.process_feedback_data(feedback_df)
            aggregated_feedback = self.aggregate_feedback_by_university(processed_feedback)
            
            # 3. Load QS rankings data
            logger.info("Loading QS rankings data...")
            qs_df = self.load_qs_rankings_data(qs_csv_path)
            
            # 4. Merge data sources
            logger.info("Merging data sources...")
            merged_df = self.merge_data_sources(aggregated_feedback, qs_df)
            
            # 5. Update database
            logger.info("Updating database...")
            self.update_database(merged_df)
            
            logger.info("Data synchronization completed successfully!")
            
            # Return summary statistics
            return {
                "total_universities": len(merged_df),
                "universities_with_feedback": len(merged_df.dropna(subset=['qs_match_name'])) if not aggregated_feedback.empty else 0,
                "feedback_responses": len(processed_feedback) if not processed_feedback.empty else 0,
                "unique_feedback_universities": len(aggregated_feedback) if not aggregated_feedback.empty else 0,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in data synchronization: {str(e)}")
            raise

# Additional utility functions for scheduled updates
class DataSyncScheduler:
    """Handles scheduled data synchronization."""
    
    def __init__(self, integrator: UniversityDataIntegrator):
        self.integrator = integrator
    
    def sync_if_needed(self, spreadsheet_id: str, qs_csv_path: str, 
                      force_sync: bool = False) -> bool:
        """Sync data if it hasn't been updated recently."""
        try:
            # Check last update time from database
            conn = sqlite3.connect('universities.db')
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT last_updated FROM universities 
            ORDER BY last_updated DESC LIMIT 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if force_sync or not result:
                logger.info("Performing data sync...")
                self.integrator.full_data_sync(spreadsheet_id, qs_csv_path)
                return True
            else:
                last_update = datetime.fromisoformat(result[0].replace('Z', '+00:00'))
                hours_since_update = (datetime.now() - last_update).total_seconds() / 3600
                
                if hours_since_update > 24:  # Sync daily
                    logger.info(f"Data is {hours_since_update:.1f} hours old, syncing...")
                    self.integrator.full_data_sync(spreadsheet_id, qs_csv_path)
                    return True
                else:
                    logger.info(f"Data is recent ({hours_since_update:.1f} hours old), skipping sync")
                    return False
                    
        except Exception as e:
            logger.error(f"Error checking sync status: {str(e)}")
            return False

# Example usage and configuration
if __name__ == "__main__":
    # Configuration
    SPREADSHEET_ID = "your_google_sheets_id_here"  # Replace with actual ID
    QS_CSV_PATH = "qs_rankings.csv"
    CREDENTIALS_FILE = "credentials.json"
    
    # Initialize integrator
    integrator = UniversityDataIntegrator(credentials_file=CREDENTIALS_FILE)
    
    # Perform full sync
    try:
        results = integrator.full_data_sync(SPREADSHEET_ID, QS_CSV_PATH)
        print("Sync Results:")
        for key, value in results.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Sync failed: {str(e)}")