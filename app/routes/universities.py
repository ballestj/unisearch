from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging
from ..database.connection import get_db_connection
from ..models.university import (
    UniversityResponse, SearchFilters, PaginationParams, SortParams
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/universities", response_model=List[UniversityResponse])
async def get_universities(
    limit: int = Query(50, ge=1, le=500, description="Number of universities to return"),
    offset: int = Query(0, ge=0, description="Number of universities to skip"),
    search: Optional[str] = Query(None, description="Search university names or cities"),
    country: Optional[str] = Query(None, description="Filter by country"),
    sort_by: str = Query("qs_rank", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order: asc or desc")
):
    """
    Get a list of universities with optional filtering, searching, and pagination.
    
    - **limit**: Number of results to return (1-500)
    - **offset**: Number of results to skip for pagination
    - **search**: Search in university names and cities
    - **country**: Filter by specific country
    - **sort_by**: Field to sort by (name, city, qs_rank, academic_rigor, etc.)
    - **sort_order**: asc (ascending) or desc (descending)
    """
    try:
        # Validate sort parameters
        valid_sort_fields = [
            "name", "city", "country", "qs_rank", "overall_quality",
            "academic_rigor", "cultural_diversity", "student_life", "campus_safety"
        ]
        if sort_by not in valid_sort_fields:
            sort_by = "qs_rank"
        
        sort_order = "ASC" if sort_order.lower() == "asc" else "DESC"
        
        # Build query
        where_clauses = []
        params = []
        
        if search:
            where_clauses.append("(name LIKE ? OR city LIKE ?)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
        if country:
            where_clauses.append("country = ?")
            params.append(country)
        
        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
        SELECT * FROM universities
        {where_sql}
        ORDER BY {sort_by} {sort_order} NULLS LAST
        LIMIT ? OFFSET ?
        """
        
        params.extend([limit, offset])
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            universities = cursor.fetchall()
        
        return [UniversityResponse(**dict(uni)) for uni in universities]
        
    except Exception as e:
        logger.error(f"Error fetching universities: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/universities/{university_id}", response_model=UniversityResponse)
async def get_university(university_id: int):
    """
    Get detailed information about a specific university by ID.
    """
    try:
        query = "SELECT * FROM universities WHERE id = ?"
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (university_id,))
            university = cursor.fetchone()
        
        if not university:
            raise HTTPException(status_code=404, detail="University not found")
        
        return UniversityResponse(**dict(university))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching university {university_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/universities/search", response_model=List[UniversityResponse])
async def search_universities(filters: SearchFilters):
    """
    Advanced university search with multiple filters.
    
    Allows filtering by:
    - Country
    - QS ranking range
    - Minimum scores for various criteria
    - Language requirements
    - Facility requirements (accommodation, language classes, accessibility)
    """
    try:
        # Build dynamic query based on filters
        where_clauses = []
        params = []
        
        if filters.search:
            where_clauses.append("(name LIKE ? OR city LIKE ?)")
            search_term = f"%{filters.search}%"
            params.extend([search_term, search_term])
        
        if filters.country:
            where_clauses.append("country = ?")
            params.append(filters.country)
        
        if filters.min_ranking and filters.max_ranking:
            where_clauses.append("qs_rank BETWEEN ? AND ?")
            params.extend([filters.min_ranking, filters.max_ranking])
        elif filters.min_ranking:
            where_clauses.append("qs_rank >= ?")
            params.append(filters.min_ranking)
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
        
        if filters.min_campus_safety:
            where_clauses.append("campus_safety >= ?")
            params.append(filters.min_campus_safety)
        
        if filters.language:
            where_clauses.append("language LIKE ?")
            params.append(f"%{filters.language}%")
        
        if filters.accommodation_required:
            where_clauses.append("accommodation = 'Yes'")
        
        if filters.language_classes_required:
            where_clauses.append("language_classes = 'Yes'")
        
        if filters.accessibility_required:
            where_clauses.append("accessibility = 'Yes'")
        
        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
        SELECT * FROM universities
        {where_sql}
        ORDER BY qs_rank ASC NULLS LAST
        LIMIT 200
        """
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            universities = cursor.fetchall()
        
        return [UniversityResponse(**dict(uni)) for uni in universities]
        
    except Exception as e:
        logger.error(f"Error in university search: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/universities/by-country/{country_name}", response_model=List[UniversityResponse])
async def get_universities_by_country(
    country_name: str,
    limit: int = Query(50, ge=1, le=200)
):
    """
    Get universities in a specific country.
    """
    try:
        query = """
        SELECT * FROM universities 
        WHERE country = ? 
        ORDER BY qs_rank ASC NULLS LAST 
        LIMIT ?
        """
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (country_name, limit))
            universities = cursor.fetchall()
        
        return [UniversityResponse(**dict(uni)) for uni in universities]
        
    except Exception as e:
        logger.error(f"Error fetching universities for country {country_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/universities/top/{criteria}", response_model=List[UniversityResponse])
async def get_top_universities_by_criteria(
    criteria: str,
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get top universities by specific criteria.
    
    - **criteria**: academic_rigor, cultural_diversity, student_life, campus_safety, or qs_rank
    - **limit**: Number of top universities to return
    """
    try:
        valid_criteria = [
            "academic_rigor", "cultural_diversity", "student_life", 
            "campus_safety", "qs_rank", "overall_quality"
        ]
        
        if criteria not in valid_criteria:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid criteria. Must be one of: {', '.join(valid_criteria)}"
            )
        
        # For QS rank, we want ascending order (lower rank = better)
        order = "ASC" if criteria == "qs_rank" else "DESC"
        
        query = f"""
        SELECT * FROM universities 
        WHERE {criteria} IS NOT NULL 
        ORDER BY {criteria} {order} 
        LIMIT ?
        """
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            universities = cursor.fetchall()
        
        return [UniversityResponse(**dict(uni)) for uni in universities]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching top universities by {criteria}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")