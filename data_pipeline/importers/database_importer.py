"""
Database Importer

Import cleaned university data into the PostgreSQL database.
"""

import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

# Add the backend path to import our models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.database.connection import SessionLocal, engine
from app.models.university import University, Base

logger = logging.getLogger(__name__)


class DatabaseImporter:
    """Import university data into the database."""
    
    def __init__(self):
        self.session = SessionLocal()
        self.stats = {
            'total_processed': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
    
    def import_from_csv(self, csv_file: str, update_existing: bool = True) -> Dict[str, int]:
        """
        Import university data from CSV file.
        
        Args:
            csv_file: Path to the CSV file
            update_existing: Whether to update existing universities
            
        Returns:
            Dictionary with import statistics
        """
        logger.info(f"Starting import from {csv_file}")
        
        try:
            # Read CSV data
            df = pd.read_csv(csv_file)
            logger.info(f"Loaded {len(df)} records from CSV")
            
            # Import each row
            for index, row in df.iterrows():
                try:
                    self._import_university_row(row, update_existing)
                except Exception as e:
                    logger.error(f"Error importing row {index}: {e}")
                    self.stats['errors'] += 1
                    continue
            
            # Commit all changes
            self.session.commit()
            logger.info("Import completed successfully")
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            self.session.rollback()
            raise
        
        return self.stats
    
    def import_from_dataframe(self, df: pd.DataFrame, update_existing: bool = True) -> Dict[str, int]:
        """
        Import university data from pandas DataFrame.
        """
        logger.info(f"Starting import from DataFrame with {len(df)} records")
        
        try:
            for index, row in df.iterrows():
                try:
                    self._import_university_row(row, update_existing)
                except Exception as e:
                    logger.error(f"Error importing row {index}: {e}")
                    self.stats['errors'] += 1
                    continue
            
            self.session.commit()
            logger.info("DataFrame import completed successfully")
            
        except Exception as e:
            logger.error(f"DataFrame import failed: {e}")
            self.session.rollback()
            raise
        
        return self.stats
    
    def _import_university_row(self, row: pd.Series, update_existing: bool):
        """Import a single university row."""
        self.stats['total_processed'] += 1
        
        # Check if university already exists
        existing = self._find_existing_university(row)
        
        if existing:
            if update_existing:
                self._update_university(existing, row)
                self.stats['updated'] += 1
            else:
                logger.debug(f"Skipping existing university: {row.get('name', 'Unknown')}")
                self.stats['skipped'] += 1
        else:
            self._create_university(row)
            self.stats['created'] += 1
    
    def _find_existing_university(self, row: pd.Series) -> Optional[University]:
        """Find existing university by name and location."""
        name = str(row.get('name', '')).strip()
        city = str(row.get('city', '')).strip()
        country = str(row.get('country', '')).strip()
        
        if not name or not country:
            return None
        
        # Try exact match first
        existing = self.session.query(University).filter(
            and_(
                University.name == name,
                University.country == country
            )
        ).first()
        
        if existing:
            return existing
        
        # Try fuzzy matching on name within same country
        universities_in_country = self.session.query(University).filter(
            University.country == country
        ).all()
        
        from thefuzz import fuzz
        
        for uni in universities_in_country:
            if fuzz.ratio(name.lower(), uni.name.lower()) > 90:
                logger.info(f"Found fuzzy match: '{name}' -> '{uni.name}'")
                return uni
        
        return None
    
    def _create_university(self, row: pd.Series):
        """Create a new university record."""
        university_data = self._prepare_university_data(row)
        
        university = University(**university_data)
        self.session.add(university)
        
        logger.debug(f"Created university: {university_data.get('name', 'Unknown')}")
    
    def _update_university(self, existing: University, row: pd.Series):
        """Update an existing university record."""
        university_data = self._prepare_university_data(row)
        
        # Update fields
        for key, value in university_data.items():
            if key != 'id' and value is not None:
                # Only update if new value is better (non-null and more recent)
                current_value = getattr(existing, key, None)
                if current_value is None or self._should_update_field(key, current_value, value):
                    setattr(existing, key, value)
        
        # Always update the last_updated timestamp
        existing.last_updated = datetime.utcnow()
        
        logger.debug(f"Updated university: {existing.name}")
    
    def _prepare_university_data(self, row: pd.Series) -> Dict[str, Any]:
        """Prepare university data dictionary from row."""
        # Map CSV columns to database fields
        field_mapping = {
            'name': 'name',
            'city': 'city',
            'country': 'country',
            'website_url': 'website_url',
            'founded_year': 'founded_year',
            'student_population': 'student_population',
            'international_students_percentage': 'international_students_percentage',
            
            # Rankings
            'qs_rank': 'qs_rank',
            'qs_score': 'qs_score',
            'the_rank': 'the_rank',
            'the_score': 'the_score',
            'arwu_rank': 'arwu_rank',
            'us_news_rank': 'us_news_rank',
            
            # Academic metrics
            'academic_rigor': 'academic_rigor',
            'research_quality': 'research_quality',
            'faculty_student_ratio': 'faculty_student_ratio',
            'citation_impact': 'citation_impact',
            'industry_connections': 'industry_connections',
            
            # Student experience
            'overall_quality': 'overall_quality',
            'student_satisfaction': 'student_satisfaction',
            'cultural_diversity': 'cultural_diversity',
            'student_life': 'student_life',
            'campus_safety': 'campus_safety',
            'openness': 'openness',
            
            # Costs
            'tuition_local': 'tuition_local',
            'tuition_international': 'tuition_international',
            'cost_of_living': 'cost_of_living',
            'currency': 'currency',
            
            # Programs
            'languages_of_instruction': 'languages_of_instruction',
            'exchange_programs': 'exchange_programs',
            'semester_system': 'semester_system',
            
            # Facilities
            'accommodation_available': 'accommodation_available',
            'language_classes': 'language_classes',
            'accessibility_support': 'accessibility_support',
            'career_services': 'career_services',
            
            # Location
            'climate_type': 'climate_type',
            'latitude': 'latitude',
            'longitude': 'longitude',
        }
        
        university_data = {}
        
        for csv_col, db_field in field_mapping.items():
            if csv_col in row.index:
                value = row[csv_col]
                
                # Handle different data types
                if pd.isna(value):
                    value = None
                elif db_field in ['languages_of_instruction', 'exchange_programs', 'tags', 'strengths']:
                    # Handle JSON fields
                    value = self._parse_json_field(value)
                elif db_field in ['accommodation_available', 'language_classes', 'accessibility_support', 'career_services']:
                    # Handle boolean fields
                    value = self._parse_boolean_field(value)
                elif db_field in ['founded_year', 'student_population', 'qs_rank', 'the_rank', 'arwu_rank', 'us_news_rank']:
                    # Handle integer fields
                    value = self._parse_integer_field(value)
                elif db_field in ['qs_score', 'the_score', 'academic_rigor', 'research_quality', 'student_life', 
                                'cultural_diversity', 'campus_safety', 'tuition_local', 'tuition_international', 
                                'cost_of_living', 'latitude', 'longitude']:
                    # Handle float fields
                    value = self._parse_float_field(value)
                
                university_data[db_field] = value
        
        # Set metadata
        university_data['last_updated'] = datetime.utcnow()
        university_data['data_sources'] = ['import_script']
        university_data['data_quality_score'] = self._calculate_data_quality_score(university_data)
        
        return university_data
    
    def _parse_json_field(self, value: Any) -> Optional[List[str]]:
        """Parse JSON field values."""
        if pd.isna(value) or value == '':
            return None
        
        if isinstance(value, list):
            return value
        
        if isinstance(value, str):
            # Try to parse as JSON
            import json
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            
            # Try comma-separated values
            if ',' in value:
                return [item.strip() for item in value.split(',') if item.strip()]
            
            # Single value
            return [value.strip()]
        
        return None
    
    def _parse_boolean_field(self, value: Any) -> Optional[bool]:
        """Parse boolean field values."""
        if pd.isna(value):
            return None
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ['true', 'yes', 'y', '1', 'on']:
                return True
            elif value in ['false', 'no', 'n', '0', 'off']:
                return False
        
        if isinstance(value, (int, float)):
            return bool(value)
        
        return None
    
    def _parse_integer_field(self, value: Any) -> Optional[int]:
        """Parse integer field values."""
        if pd.isna(value):
            return None
        
        try:
            if isinstance(value, str):
                # Remove commas and other formatting
                value = value.replace(',', '').replace(' ', '')
                
            return int(float(value))  # Convert via float to handle "123.0"
        except (ValueError, TypeError):
            return None
    
    def _parse_float_field(self, value: Any) -> Optional[float]:
        """Parse float field values."""
        if pd.isna(value):
            return None
        
        try:
            if isinstance(value, str):
                # Remove formatting
                value = value.replace(',', '').replace(' ', '').replace('%', '')
                
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _should_update_field(self, field_name: str, current_value: Any, new_value: Any) -> bool:
        """Determine if a field should be updated."""
        # Always update if current value is None
        if current_value is None:
            return True
        
        # For rankings, prefer lower (better) values
        if 'rank' in field_name:
            return new_value < current_value
        
        # For scores, prefer higher values
        if 'score' in field_name or field_name in ['academic_rigor', 'student_life', 'cultural_diversity']:
            return new_value > current_value
        
        # For other fields, prefer non-null values
        return new_value is not None
    
    def _calculate_data_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate data quality score (0-1) based on completeness."""
        important_fields = [
            'name', 'country', 'qs_rank', 'academic_rigor', 
            'student_life', 'tuition_international', 'cost_of_living'
        ]
        
        filled_fields = sum(1 for field in important_fields if data.get(field) is not None)
        return filled_fields / len(important_fields)
    
    def create_tables(self):
        """Create database tables if they don't exist."""
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    
    def get_import_stats(self) -> Dict[str, int]:
        """Get import statistics."""
        return self.stats.copy()


def main():
    """Main import function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import university data into database')
    parser.add_argument('csv_file', help='Path to CSV file to import')
    parser.add_argument('--update', action='store_true', help='Update existing records')
    parser.add_argument('--create-tables', action='store_true', help='Create database tables')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    with DatabaseImporter() as importer:
        if args.create_tables:
            importer.create_tables()
        
        if os.path.exists(args.csv_file):
            stats = importer.import_from_csv(args.csv_file, args.update)
            
            print("\nImport Statistics:")
            print(f"Total processed: {stats['total_processed']}")
            print(f"Created: {stats['created']}")
            print(f"Updated: {stats['updated']}")
            print(f"Skipped: {stats['skipped']}")
            print(f"Errors: {stats['errors']}")
        else:
            print(f"Error: CSV file '{args.csv_file}' not found")


if __name__ == "__main__":
    main()