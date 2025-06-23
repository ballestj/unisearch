#!/usr/bin/env python3
"""
UniSearch Backend Startup Script - Flat Structure Version
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UniSearchBackend:
    """Main backend application controller."""
    
    def __init__(self):
        self.integrator = None
        self.scheduler = None
        
        # Configuration from environment variables
        self.config = {
            'spreadsheet_id': os.getenv('GOOGLE_SHEETS_ID'),
            'qs_csv_path': os.getenv('QS_CSV_PATH', 'qs_rankings.csv'),
            'credentials_file': os.getenv('GOOGLE_CREDENTIALS', 'credentials.json'),
            'database_path': os.getenv('DATABASE_PATH', 'universities.db'),
            'host': os.getenv('HOST', '0.0.0.0'),
            'port': int(os.getenv('PORT', 8000)),
            'reload': os.getenv('ENVIRONMENT', 'production') == 'development'
        }
    
    def initialize_integrator(self):
        """Initialize the data integrator."""
        try:
            from google_sheets_integration import UniversityDataIntegrator, DataSyncScheduler
            self.integrator = UniversityDataIntegrator(
                credentials_file=self.config['credentials_file']
            )
            self.scheduler = DataSyncScheduler(self.integrator)
            logger.info("Data integrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize integrator: {str(e)}")
            logger.info("This is normal if you haven't set up Google Sheets integration yet")
    
    def check_requirements(self) -> bool:
        """Check if all required files and configurations are present."""
        required_files = [
            self.config['qs_csv_path']
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.warning(f"Missing files: {missing_files}")
            logger.info("Some features may not work without these files")
        
        return True  # Don't fail if some files are missing
    
    def sync_data(self, force: bool = False) -> bool:
        """Synchronize data from Google Sheets and QS rankings."""
        try:
            if not self.integrator:
                self.initialize_integrator()
            
            if not self.integrator:
                logger.warning("Cannot sync data: Google Sheets integrator not available")
                return False
            
            logger.info("Starting data synchronization...")
            
            if force:
                results = self.integrator.full_data_sync(
                    self.config['spreadsheet_id'],
                    self.config['qs_csv_path']
                )
                logger.info(f"Sync completed: {results}")
                return True
            else:
                return self.scheduler.sync_if_needed(
                    self.config['spreadsheet_id'],
                    self.config['qs_csv_path']
                )
                
        except Exception as e:
            logger.error(f"Data synchronization failed: {str(e)}")
            return False
    
    def start_server(self, sync_on_startup: bool = True):
        """Start the FastAPI server."""
        try:
            # Perform data sync if requested and possible
            if sync_on_startup:
                logger.info("Attempting startup data sync...")
                self.sync_data(force=False)
            
            # Start the server
            logger.info(f"Starting UniSearch API server on {self.config['host']}:{self.config['port']}")
            
            import uvicorn
            uvicorn.run(
                "main:app",  # Import path to FastAPI app
                host=self.config['host'],
                port=self.config['port'],
                reload=self.config['reload'],
                log_level="info"
            )
            
        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}")
            raise

def create_env_file():
    """Create a sample .env file with configuration options."""
    env_content = """# UniSearch Backend Configuration

# Google Sheets Integration (REQUIRED for data sync)
GOOGLE_SHEETS_ID=your_google_sheets_id_here
GOOGLE_CREDENTIALS=credentials.json

# Data Sources
QS_CSV_PATH=qs_rankings.csv
DATABASE_PATH=universities.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with sample configuration")
    print("\n📝 Next steps:")
    print("1. Update GOOGLE_SHEETS_ID in .env file with your actual Google Sheets ID")
    print("2. Copy credentials.json to this directory")
    print("3. Copy qs_rankings.csv to this directory") 
    print("4. Run: python startup.py sync --force-sync")
    print("5. Run: python startup.py start")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='UniSearch Backend')
    parser.add_argument('command', choices=['start', 'sync', 'setup'], 
                       help='Command to execute')
    parser.add_argument('--force-sync', action='store_true',
                       help='Force data synchronization')
    parser.add_argument('--no-startup-sync', action='store_true',
                       help='Skip data sync on server startup')
    
    args = parser.parse_args()
    
    backend = UniSearchBackend()
    
    if args.command == 'setup':
        print("🚀 Setting up UniSearch backend...")
        create_env_file()
        return
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenv not installed. Using environment variables only.")
    
    # Update config with environment variables
    backend.config.update({
        'spreadsheet_id': os.getenv('GOOGLE_SHEETS_ID'),
        'qs_csv_path': os.getenv('QS_CSV_PATH', 'qs_rankings.csv'),
        'credentials_file': os.getenv('GOOGLE_CREDENTIALS', 'credentials.json'),
        'database_path': os.getenv('DATABASE_PATH', 'universities.db'),
        'host': os.getenv('HOST', '0.0.0.0'),
        'port': int(os.getenv('PORT', 8000)),
        'reload': os.getenv('ENVIRONMENT', 'production') == 'development'
    })
    
    # Check requirements
    if not backend.check_requirements():
        print("⚠️  Some requirements missing. Some features may not work.")
    
    if args.command == 'sync':
        success = backend.sync_data(force=args.force_sync)
        if success:
            print("✅ Data synchronization completed successfully")
        else:
            print("❌ Data synchronization failed")
            sys.exit(1)
    
    elif args.command == 'start':
        try:
            backend.start_server(sync_on_startup=not args.no_startup_sync)
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server failed: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()