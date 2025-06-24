from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import sqlite3
from typing import List, Optional
from pydantic import BaseModel, Field
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="UniSearch API",
    description="University Exchange Platform API - Find your perfect study abroad destination",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
frontend_urls = os.getenv("FRONTEND_URLS")
if not frontend_urls:
    raise RuntimeError("FRONTEND_URLS is not set in the environment variables!")

print("🌐 Allowed Frontend URLs:", frontend_urls)
allow_origins = [url.strip() for url in frontend_urls.split(",")]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UniversityResponse(BaseModel):
    id: int
    name: str
    city: Optional[str] = None
    country: Optional[str] = None
    qs_rank: Optional[int] = None
    overall_quality: Optional[float] = None
    academic_rigor: Optional[float] = None
    openness: Optional[float] = None
    cultural_diversity: Optional[float] = None
    student_life: Optional[float] = None
    campus_safety: Optional[float] = None
    accommodation: Optional[str] = None
    language: Optional[str] = None
    language_classes: Optional[str] = None
    accessibility: Optional[str] = None
    response_count: Optional[int] = 0

class SearchFilters(BaseModel):
    search: Optional[str] = None
    country: Optional[str] = None
    min_ranking: Optional[int] = None
    max_ranking: Optional[int] = None
    min_academic_rigor: Optional[float] = None
    min_cultural_diversity: Optional[float] = None
    min_student_life: Optional[float] = None
    language: Optional[str] = None
    accommodation_required: Optional[bool] = None

class RecommendationRequest(BaseModel):
    academic_importance: int = Field(..., ge=1, le=5)
    diversity_importance: int = Field(..., ge=1, le=5)
    student_life_importance: int = Field(..., ge=1, le=5)
    preferred_countries: Optional[List[str]] = None
    max_ranking: Optional[int] = None

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('universities.db')
    conn.row_factory = sqlite3.Row
    return conn

# Root and health
@app.get("/")
async def root():
    return {
        "message": "UniSearch API is running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }

@app.get("/api/ping")
def ping():
    return {"pong": True, "timestamp": datetime.now().isoformat()}

@app.get("/api/health")
async def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM universities")
        count = cursor.fetchone()['count']
        conn.close()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "universities_count": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/api/universities", response_model=List[UniversityResponse])
async def get_universities(limit: int = 50, offset: int = 0, search: Optional[str] = None, country: Optional[str] = None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        where_clauses = []
        params = []
        if search:
            where_clauses.append("(name LIKE ? OR city LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        if country:
            where_clauses.append("country = ?")
            params.append(country)
        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        query = f"""
        SELECT *, COALESCE(response_count, 0) as response_count FROM universities
        {where_sql}
        ORDER BY qs_rank ASC NULLS LAST
        LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        cursor.execute(query, params)
        universities = cursor.fetchall()
        conn.close()
        return [UniversityResponse(**dict(uni)) for uni in universities]
    except Exception as e:
        logger.error(f"Error fetching universities: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/universities/{university_id}", response_model=UniversityResponse)
async def get_university(university_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT *, COALESCE(response_count, 0) as response_count FROM universities WHERE id = ?", (university_id,))
        university = cursor.fetchone()
        conn.close()
        if not university:
            raise HTTPException(status_code=404, detail="University not found")
        return UniversityResponse(**dict(university))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching university {university_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/universities/search", response_model=List[UniversityResponse])
async def search_universities(filters: SearchFilters):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        where_clauses = []
        params = []
        if filters.search:
            where_clauses.append("(name LIKE ? OR city LIKE ?)")
            params.extend([f"%{filters.search}%", f"%{filters.search}%"])
        if filters.country:
            where_clauses.append("country = ?")
            params.append(filters.country)
        if filters.min_ranking and filters.max_ranking:
            where_clauses.append("qs_rank BETWEEN ? AND ?")
            params.extend([filters.min_ranking, filters.max_ranking])
        elif filters.max_ranking:
            where_clauses.append("qs_rank <= ?")
            params.append(filters.max_ranking)
        if filters.min_academic_rigor:
            where_clauses.append("academic_rigor >= ?")
            params.append(filters.min_academic_rigor)
        if filters.min_cultural_diversity:
            where_clauses.append("cultural_diversity >= ?")
            params.append(filters.min_cultural_diversity)
        if filters.min_student_life:
            where_clauses.append("student_life >= ?")
            params.append(filters.min_student_life)
        if filters.language:
            where_clauses.append("language LIKE ?")
            params.append(f"%{filters.language}%")
        if filters.accommodation_required:
            where_clauses.append("accommodation = 'Yes'")
        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        query = f"""
        SELECT *, COALESCE(response_count, 0) as response_count FROM universities
        {where_sql}
        ORDER BY qs_rank ASC NULLS LAST
        LIMIT 100
        """
        cursor.execute(query, params)
        universities = cursor.fetchall()
        conn.close()
        return [UniversityResponse(**dict(uni)) for uni in universities]
    except Exception as e:
        logger.error(f"Error in university search: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/recommendations", response_model=List[UniversityResponse])
async def get_recommendations(request: RecommendationRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        academic_weight = request.academic_importance / 5.0
        diversity_weight = request.diversity_importance / 5.0
        student_life_weight = request.student_life_importance / 5.0
        where_clauses = []
        params = [academic_weight, diversity_weight, student_life_weight]
        if request.preferred_countries:
            placeholders = ",".join(["?" for _ in request.preferred_countries])
            where_clauses.append(f"country IN ({placeholders})")
            params.extend(request.preferred_countries)
        if request.max_ranking:
            where_clauses.append("qs_rank <= ?")
            params.append(request.max_ranking)
        where_clauses.extend([
            "academic_rigor IS NOT NULL",
            "cultural_diversity IS NOT NULL", 
            "student_life IS NOT NULL"
        ])
        where_sql = " WHERE " + " AND ".join(where_clauses)
        query = f"""
        SELECT *,
               COALESCE(response_count, 0) as response_count,
               ROUND((academic_rigor * ? + cultural_diversity * ? + student_life * ?) / 3.0, 2) as match_score
        FROM universities
        {where_sql}
        ORDER BY match_score DESC, qs_rank ASC
        LIMIT 20
        """
        cursor.execute(query, params)
        universities = cursor.fetchall()
        conn.close()
        return [UniversityResponse(**dict(uni)) for uni in universities]
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/countries")
async def get_countries():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT DISTINCT country, COUNT(*) as university_count
        FROM universities
        WHERE country IS NOT NULL AND country != ''
        GROUP BY country
        ORDER BY university_count DESC
        """)
        countries = cursor.fetchall()
        conn.close()
        return [{"name": row["country"], "count": row["university_count"]} for row in countries]
    except Exception as e:
        logger.error(f"Error fetching countries: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/stats")
async def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total from universities")
        total = cursor.fetchone()["total"]
        cursor.execute("SELECT COUNT(*) as ranked from universities WHERE qs_rank IS NOT NULL")
        ranked = cursor.fetchone()["ranked"]
        cursor.execute("SELECT COUNT(DISTINCT country) as countries from universities WHERE country IS NOT NULL AND country != ''")
        countries = cursor.fetchone()["countries"]
        conn.close()
        return {
            "total_universities": total,
            "ranked_universities": ranked,
            "total_countries": countries,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

print("🚦 Allowed CORS origins:", allow_origins)
