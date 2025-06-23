"""
Database Connection

SQLAlchemy database connection setup with PostgreSQL support
and SQLite fallback for development.
"""

import os
import logging
from typing import Generator, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to development SQLite
    DATABASE_URL = os.getenv("DATABASE_URL_DEV", "sqlite:///./unisearch_dev.db")
    logger.warning("Using SQLite database for development")

# Create engine with appropriate settings
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL settings
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
    logger.info("Connected to PostgreSQL database")
elif DATABASE_URL.startswith("sqlite"):
    # SQLite settings
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
    logger.info("Connected to SQLite database")
else:
    raise ValueError(f"Unsupported database URL: {DATABASE_URL}")

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def get_database_health() -> Dict[str, Any]:
    """
    Check database health and connectivity.
    
    Returns:
        Dict containing health status information
    """
    try:
        db = SessionLocal()
        # Simple query to test connectivity
        result = db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "database_type": "postgresql" if DATABASE_URL.startswith("postgresql") else "sqlite",
            "connection": "active"
        }
    except SQLAlchemyError as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database_type": "postgresql" if DATABASE_URL.startswith("postgresql") else "sqlite",
            "connection": "failed"
        }
    except Exception as e:
        logger.error(f"Unexpected error in health check: {e}")
        return {
            "status": "unhealthy",
            "error": "Unexpected error",
            "connection": "unknown"
        }


def create_tables():
    """
    Create all database tables.
    Should be called during application startup or migration.
    """
    try:
        from ..models.university import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """
    Drop all database tables.
    WARNING: This will delete all data!
    """
    try:
        from ..models.university import Base
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


class DatabaseManager:
    """
    Database management utilities.
    """
    
    @staticmethod
    def reset_database():
        """Reset database by dropping and recreating all tables."""
        logger.warning("Resetting database - all data will be lost!")
        drop_tables()
        create_tables()
        logger.info("Database reset completed")
    
    @staticmethod
    def get_table_info() -> Dict[str, Any]:
        """Get information about database tables."""
        try:
            from ..models.university import Base
            tables = Base.metadata.tables.keys()
            return {
                "tables": list(tables),
                "table_count": len(tables)
            }
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return {"error": str(e)}