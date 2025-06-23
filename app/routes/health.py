from fastapi import APIRouter, HTTPException
from datetime import datetime
import os
import logging
from ..database.connection import get_db_connection

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "UniSearch API",
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check including database connectivity and data status.
    """
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "UniSearch API",
        "version": "1.0.0",
        "checks": {}
    }
    
    # Check database connectivity
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM universities")
            result = cursor.fetchone()
            
            health_data["checks"]["database"] = {
                "status": "healthy",
                "universities_count": result['count'],
                "message": "Database connection successful"
            }
    except Exception as e:
        health_data["status"] = "unhealthy"
        health_data["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
            "message": "Database connection failed"
        }
    
    # Check if required files exist
    required_files = ["../google_sheets_integration.py", "../startup.py"]
    files_status = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            files_status.append({"file": file_path, "status": "exists"})
        else:
            files_status.append({"file": file_path, "status": "missing"})
    
    health_data["checks"]["files"] = {
        "status": "healthy" if all(f["status"] == "exists" for f in files_status) else "warning",
        "files": files_status
    }
    
    # Check data freshness
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    MAX(last_updated) as last_update,
                    COUNT(*) as total_universities,
                    COUNT(CASE WHEN qs_rank IS NOT NULL THEN 1 END) as ranked_universities,
                    COUNT(CASE WHEN response_count > 0 THEN 1 END) as universities_with_feedback
                FROM universities
            """)
            data_stats = cursor.fetchone()
            
            health_data["checks"]["data"] = {
                "status": "healthy",
                "last_updated": data_stats['last_update'],
                "total_universities": data_stats['total_universities'],
                "ranked_universities": data_stats['ranked_universities'],
                "universities_with_feedback": data_stats['universities_with_feedback']
            }
    except Exception as e:
        health_data["status"] = "unhealthy"
        health_data["checks"]["data"] = {
            "status": "unhealthy",
            "error": str(e),
            "message": "Data check failed"
        }
    
    return health_data

@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for load balancers.
    """
    return {"message": "pong"}

@router.get("/version")
async def get_version():
    """
    Get API version information.
    """
    return {
        "service": "UniSearch API",
        "version": "1.0.0",
        "description": "University Exchange Platform API",
        "python_version": os.sys.version,
        "environment": os.getenv("ENVIRONMENT", "production")
    }