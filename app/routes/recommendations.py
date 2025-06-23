"""
Recommendations API Routes

Personalized university recommendations based on user preferences.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from pydantic import BaseModel, Field

from ..database.connection import get_db
from ..models.university import University, UniversityRecommendation

router = APIRouter()


class UserProfile(BaseModel):
    """User profile for generating recommendations."""
    # Academic preferences
    field_of_study: Optional[str] = Field(None, description="Primary academic field")
    academic_importance: int = Field(3, ge=1, le=5, description="Importance of academic rigor (1-5)")
    research_importance: int = Field(3, ge=1, le=5, description="Importance of research opportunities")
    
    # Experience preferences  
    cultural_diversity_importance: int = Field(3, ge=1, le=5, description="Importance of cultural diversity")
    student_life_importance: int = Field(3, ge=1, le=5, description="Importance of student life quality")
    campus_safety_importance: int = Field(4, ge=1, le=5, description="Importance of campus safety")
    
    # Practical constraints
    max_tuition_budget: Optional[float] = Field(None, ge=0, description="Maximum tuition budget")
    cost_importance: int = Field(3, ge=1, le=5, description="Importance of low costs (1=not important, 5=very important)")
    
    # Location preferences
    preferred_countries: Optional[List[str]] = Field(default=[], description="Preferred countries")
    preferred_climate: Optional[str] = Field(None, description="Preferred climate type")
    language_requirements: Optional[List[str]] = Field(default=[], description="Required languages")
    
    # Program requirements
    accommodation_required: Optional[bool] = Field(None, description="University accommodation required")
    exchange_program_types: Optional[List[str]] = Field(default=[], description="Preferred program types")
    
    # Ranking preferences
    ranking_importance: int = Field(3, ge=1, le=5, description="Importance of university rankings")
    min_acceptable_rank: Optional[int] = Field(None, description="Minimum acceptable QS rank")


class RecommendationEngine:
    """Core recommendation logic."""
    
    @staticmethod
    def calculate_match_score(university: University, profile: UserProfile) -> tuple[float, List[str]]:
        """
        Calculate match score between university and user profile.
        
        Returns:
            Tuple of (score, reasons) where score is 0-100
        """
        score = 0.0
        reasons = []
        max_possible_score = 0.0
        
        # Academic fit (25% weight)
        if university.academic_rigor is not None:
            academic_weight = profile.academic_importance / 5.0 * 25
            academic_score = (university.academic_rigor / 10.0) * academic_weight
            score += academic_score
            max_possible_score += academic_weight
            
            if university.academic_rigor >= 8.0 and profile.academic_importance >= 4:
                reasons.append("Excellent academic rigor match")
            elif university.academic_rigor >= 6.0:
                reasons.append("Good academic standards")
        
        # Research quality (15% weight)
        if university.research_quality is not None:
            research_weight = profile.research_importance / 5.0 * 15
            research_score = (university.research_quality / 10.0) * research_weight
            score += research_score
            max_possible_score += research_weight
            
            if university.research_quality >= 8.0 and profile.research_importance >= 4:
                reasons.append("Strong research opportunities")
        
        # Cultural diversity (15% weight)
        if university.cultural_diversity is not None:
            diversity_weight = profile.cultural_diversity_importance / 5.0 * 15
            diversity_score = (university.cultural_diversity / 10.0) * diversity_weight
            score += diversity_score
            max_possible_score += diversity_weight
            
            if university.cultural_diversity >= 8.0 and profile.cultural_diversity_importance >= 4:
                reasons.append("Highly diverse international environment")
        
        # Student life (15% weight)
        if university.student_life is not None:
            life_weight = profile.student_life_importance / 5.0 * 15
            life_score = (university.student_life / 10.0) * life_weight
            score += life_score
            max_possible_score += life_weight
            
            if university.student_life >= 8.0 and profile.student_life_importance >= 4:
                reasons.append("Excellent student life and activities")
        
        # Campus safety (10% weight)
        if university.campus_safety is not None:
            safety_weight = profile.campus_safety_importance / 5.0 * 10
            safety_score = (university.campus_safety / 10.0) * safety_weight
            score += safety_score
            max_possible_score += safety_weight
            
            if university.campus_safety >= 8.0:
                reasons.append("Very safe campus environment")
        
        # Cost considerations (10% weight)
        if university.tuition_international is not None and profile.max_tuition_budget:
            cost_weight = profile.cost_importance / 5.0 * 10
            if university.tuition_international <= profile.max_tuition_budget:
                cost_score = cost_weight  # Full points if within budget
                score += cost_score
                reasons.append("Within your budget")
            else:
                # Partial points based on how close it is to budget
                ratio = profile.max_tuition_budget / university.tuition_international
                cost_score = cost_weight * max(0, ratio)
                score += cost_score
            max_possible_score += cost_weight
        
        # Ranking bonus (5% weight)
        if university.qs_rank is not None:
            ranking_weight = profile.ranking_importance / 5.0 * 5
            if profile.min_acceptable_rank and university.qs_rank <= profile.min_acceptable_rank:
                ranking_score = ranking_weight
                score += ranking_score
                if university.qs_rank <= 100:
                    reasons.append("Top 100 global ranking")
                elif university.qs_rank <= 500:
                    reasons.append("Highly ranked university")
            max_possible_score += ranking_weight
        
        # Location preferences (5% weight)
        location_weight = 5
        if profile.preferred_countries and university.country in profile.preferred_countries:
            score += location_weight
            reasons.append(f"Located in preferred country: {university.country}")
        max_possible_score += location_weight
        
        # Language match (5% weight)
        language_weight = 5
        if (profile.language_requirements and university.languages_of_instruction and
            any(lang in university.languages_of_instruction for lang in profile.language_requirements)):
            score += language_weight
            reasons.append("Offers programs in your preferred language")
        max_possible_score += language_weight
        
        # Climate match (5% weight)
        if profile.preferred_climate and university.climate_type == profile.preferred_climate:
            score += 5
            reasons.append(f"Perfect climate match: {profile.preferred_climate}")
            max_possible_score += 5
        
        # Accommodation availability (5% weight)
        if profile.accommodation_required and university.accommodation_available:
            score += 5
            reasons.append("University accommodation available")
            max_possible_score += 5
        
        # Convert to percentage
        if max_possible_score > 0:
            final_score = (score / max_possible_score) * 100
        else:
            final_score = 0
        
        return min(final_score, 100), reasons


@router.post("/", response_model=List[UniversityRecommendation])
def get_recommendations(
    profile: UserProfile,
    limit: int = Field(10, ge=1, le=50, description="Number of recommendations"),
    db: Session = Depends(get_db)
):
    """
    Get personalized university recommendations based on user profile.
    """
    # Start with base query
    query = db.query(University)
    
    # Apply hard constraints
    if profile.max_tuition_budget:
        query = query.filter(
            and_(
                University.tuition_international.isnot(None),
                University.tuition_international <= profile.max_tuition_budget * 1.2  # 20% buffer
            )
        )
    
    if profile.preferred_countries:
        query = query.filter(University.country.in_(profile.preferred_countries))
    
    if profile.min_acceptable_rank:
        query = query.filter(
            and_(
                University.qs_rank.isnot(None),
                University.qs_rank <= profile.min_acceptable_rank
            )
        )
    
    if profile.accommodation_required:
        query = query.filter(University.accommodation_available == True)
    
    # Get universities
    universities = query.all()
    
    if not universities:
        raise HTTPException(
            status_code=404, 
            detail="No universities found matching your requirements"
        )
    
    # Calculate scores for all universities
    recommendations = []
    engine = RecommendationEngine()
    
    for university in universities:
        score, reasons = engine.calculate_match_score(university, profile)
        
        if score > 20:  # Only include universities with decent match
            recommendations.append(UniversityRecommendation(
                university=university,
                match_score=round(score, 1),
                match_reasons=reasons,
                confidence=min(0.95, score / 100 + 0.1)  # Confidence based on score
            ))
    
    # Sort by score and return top results
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    
    return recommendations[:limit]


@router.get("/quick/{university_id}")
def quick_recommendation(
    university_id: int,
    limit: int = Field(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Get quick recommendations similar to a specific university.
    """
    base_university = db.query(University).filter(University.id == university_id).first()
    if not base_university:
        raise HTTPException(status_code=404, detail="University not found")
    
    # Find similar universities based on key metrics
    similar_universities = db.query(University).filter(
        and_(
            University.id != university_id,
            University.country == base_university.country,  # Same country first
            University.qs_rank.between(
                (base_university.qs_rank or 1000) - 200,
                (base_university.qs_rank or 1000) + 200
            ) if base_university.qs_rank else True
        )
    ).limit(limit).all()
    
    return {
        "base_university": base_university,
        "similar_universities": similar_universities,
        "criteria": "Same country and similar ranking"
    }


@router.get("/trending")
def get_trending_destinations(
    limit: int = Field(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Get trending university destinations based on various factors.
    """
    # Get universities with high scores across multiple metrics
    trending = db.query(University).filter(
        and_(
            University.student_life >= 7.0,
            University.cultural_diversity >= 7.0,
            University.academic_rigor >= 6.0
        )
    ).order_by(
        University.qs_rank.asc().nullslast(),
        University.student_life.desc()
    ).limit(limit).all()
    
    return {
        "trending_universities": trending,
        "criteria": "High student life, cultural diversity, and academic standards"
    }