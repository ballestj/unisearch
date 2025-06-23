from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging
from ..database.connection import get_db_connection
from ..models.university import CountryStats, PlatformStats

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/countries", response_model=List[CountryStats])
async def get_countries():
    """
    Get list of all countries with university statistics.
    """
    try:
        query = """
        SELECT 
            country,
            COUNT(*) as university_count,
            ROUND(AVG(academic_rigor), 2) as avg_academic_rigor,
            ROUND(AVG(cultural_diversity), 2) as avg_cultural_diversity,
            ROUND(AVG(student_life), 2) as avg_student_life,
            (SELECT name FROM universities u2 
             WHERE u2.country = u1.country AND u2.qs_rank IS NOT NULL 
             ORDER BY u2.qs_rank ASC LIMIT 1) as top_university
        FROM universities u1
        WHERE country IS NOT NULL AND country != ''
        GROUP BY country
        HAVING university_count > 0
        ORDER BY university_count DESC, country ASC
        """
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            countries = cursor.fetchall()
        
        results = []
        for country in countries:
            country_dict = dict(country)
            results.append(CountryStats(
                name=country_dict['country'],
                university_count=country_dict['university_count'],
                avg_academic_rigor=country_dict['avg_academic_rigor'],
                avg_cultural_diversity=country_dict['avg_cultural_diversity'],
                avg_student_life=country_dict['avg_student_life'],
                top_university=country_dict['top_university']
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Error fetching countries: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/languages")
async def get_languages():
    """
    Get list of all languages of instruction.
    """
    try:
        query = """
        SELECT DISTINCT language, COUNT(*) as count
        FROM universities
        WHERE language IS NOT NULL AND language != ''
        GROUP BY language
        ORDER BY count DESC
        """
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            languages = cursor.fetchall()
        
        # Parse languages (some entries may have multiple languages)
        language_counts = {}
        
        for row in languages:
            lang_str = row['language']
            count = row['count']
            
            # Split by common separators
            langs = [lang.strip() for lang in lang_str.replace(',', ';').split(';')]
            
            for lang in langs:
                if lang:
                    if lang in language_counts:
                        language_counts[lang] += count
                    else:
                        language_counts[lang] = count
        
        # Convert to list and sort
        result = [
            {"language": lang, "count": count}
            for lang, count in sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching languages: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats", response_model=PlatformStats)
async def get_platform_stats():
    """
    Get comprehensive platform statistics.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Total universities
            cursor.execute("SELECT COUNT(*) as total FROM universities")
            total_universities = cursor.fetchone()['total']
            
            # Universities with QS ranking
            cursor.execute("SELECT COUNT(*) as ranked FROM universities WHERE qs_rank IS NOT NULL")
            ranked_universities = cursor.fetchone()['ranked']
            
            # Total countries
            cursor.execute("""
                SELECT COUNT(DISTINCT country) as countries 
                FROM universities 
                WHERE country IS NOT NULL AND country != ''
            """)
            total_countries = cursor.fetchone()['countries']
            
            # Universities with feedback
            cursor.execute("SELECT COUNT(*) as with_feedback FROM universities WHERE response_count > 0")
            universities_with_feedback = cursor.fetchone()['with_feedback']
            
            # Average scores
            cursor.execute("""
                SELECT 
                    ROUND(AVG(academic_rigor), 2) as avg_academic,
                    ROUND(AVG(cultural_diversity), 2) as avg_diversity,
                    ROUND(AVG(student_life), 2) as avg_student_life
                FROM universities 
                WHERE academic_rigor IS NOT NULL 
                  AND cultural_diversity IS NOT NULL 
                  AND student_life IS NOT NULL
            """)
            averages = cursor.fetchone()
        
        from datetime import datetime
        
        return PlatformStats(
            total_universities=total_universities,
            ranked_universities=ranked_universities,
            total_countries=total_countries,
            universities_with_feedback=universities_with_feedback,
            average_academic_rigor=averages['avg_academic'],
            average_cultural_diversity=averages['avg_diversity'],
            average_student_life=averages['avg_student_life'],
            last_updated=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error fetching platform stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/ranking-ranges")
async def get_ranking_ranges():
    """
    Get QS ranking distribution ranges for filtering.
    """
    try:
        query = """
        SELECT 
            MIN(qs_rank) as min_rank,
            MAX(qs_rank) as max_rank,
            COUNT(*) as total_ranked,
            COUNT(CASE WHEN qs_rank <= 50 THEN 1 END) as top_50,
            COUNT(CASE WHEN qs_rank <= 100 THEN 1 END) as top_100,
            COUNT(CASE WHEN qs_rank <= 200 THEN 1 END) as top_200,
            COUNT(CASE WHEN qs_rank <= 500 THEN 1 END) as top_500
        FROM universities
        WHERE qs_rank IS NOT NULL
        """
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
        
        return {
            "min_ranking": result['min_rank'],
            "max_ranking": result['max_rank'],
            "total_ranked_universities": result['total_ranked'],
            "distribution": {
                "top_50": result['top_50'],
                "top_100": result['top_100'],
                "top_200": result['top_200'],
                "top_500": result['top_500']
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching ranking ranges: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/score-ranges")
async def get_score_ranges():
    """
    Get score distribution ranges for all criteria.
    """
    try:
        query = """
        SELECT 
            MIN(academic_rigor) as min_academic, MAX(academic_rigor) as max_academic,
            MIN(cultural_diversity) as min_diversity, MAX(cultural_diversity) as max_diversity,
            MIN(student_life) as min_student_life, MAX(student_life) as max_student_life,
            MIN(campus_safety) as min_safety, MAX(campus_safety) as max_safety,
            MIN(overall_quality) as min_overall, MAX(overall_quality) as max_overall
        FROM universities
        WHERE academic_rigor IS NOT NULL 
          AND cultural_diversity IS NOT NULL 
          AND student_life IS NOT NULL
        """
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
        
        return {
            "academic_rigor": {
                "min": result['min_academic'],
                "max": result['max_academic']
            },
            "cultural_diversity": {
                "min": result['min_diversity'],
                "max": result['max_diversity']
            },
            "student_life": {
                "min": result['min_student_life'],
                "max": result['max_student_life']
            },
            "campus_safety": {
                "min": result['min_safety'],
                "max": result['max_safety']
            },
            "overall_quality": {
                "min": result['min_overall'],
                "max": result['max_overall']
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching score ranges: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/facilities")
async def get_facility_stats():
    """
    Get statistics about university facilities.
    """
    try:
        query = """
        SELECT 
            accommodation,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM universities), 1) as percentage
        FROM universities
        WHERE accommodation IS NOT NULL
        GROUP BY accommodation
        
        UNION ALL
        
        SELECT 
            CONCAT('Language Classes: ', language_classes) as accommodation,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM universities), 1) as percentage
        FROM universities
        WHERE language_classes IS NOT NULL
        GROUP BY language_classes
        
        UNION ALL
        
        SELECT 
            CONCAT('Accessibility: ', accessibility) as accommodation,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM universities), 1) as percentage
        FROM universities
        WHERE accessibility IS NOT NULL
        GROUP BY accessibility
        """
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            facilities = cursor.fetchall()
        
        return [dict(facility) for facility in facilities]
        
    except Exception as e:
        logger.error(f"Error fetching facility stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")