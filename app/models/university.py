from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class AccommodationType(str, Enum):
    YES = "Yes"
    NO = "No"
    PARTIAL = "Partial"

class YesNoType(str, Enum):
    YES = "Yes"
    NO = "No"

class UniversityBase(BaseModel):
    """Base university model with common fields."""
    name: str = Field(..., min_length=1, max_length=200, description="University name")
    city: Optional[str] = Field(None, max_length=100, description="City where university is located")
    country: Optional[str] = Field(None, max_length=100, description="Country where university is located")

class UniversityCreate(UniversityBase):
    """Model for creating a new university."""
    qs_rank: Optional[int] = Field(None, ge=1, description="QS World University Ranking")
    overall_quality: Optional[float] = Field(None, ge=0, le=10, description="Overall quality score (0-10)")
    academic_rigor: Optional[float] = Field(None, ge=0, le=10, description="Academic rigor score (0-10)")
    openness: Optional[float] = Field(None, ge=0, le=10, description="Openness/inclusivity score (0-10)")
    cultural_diversity: Optional[float] = Field(None, ge=0, le=10, description="Cultural diversity score (0-10)")
    student_life: Optional[float] = Field(None, ge=0, le=10, description="Student life quality score (0-10)")
    campus_safety: Optional[float] = Field(None, ge=0, le=10, description="Campus safety score (0-10)")
    accommodation: Optional[AccommodationType] = Field(None, description="University accommodation availability")
    language: Optional[str] = Field(None, max_length=200, description="Languages of instruction")
    language_classes: Optional[YesNoType] = Field(None, description="Local language classes available")
    accessibility: Optional[AccommodationType] = Field(None, description="Accessibility/disability support")

class UniversityResponse(UniversityBase):
    """Model for university response data."""
    id: int
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
    response_count: int = 0
    last_updated: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UniversityWithScore(UniversityResponse):
    """University response with calculated match score."""
    match_score: Optional[float] = Field(None, description="Calculated match score for recommendations")

class SearchFilters(BaseModel):
    """Model for university search filters."""
    search: Optional[str] = Field(None, max_length=100, description="Search term for name or city")
    country: Optional[str] = Field(None, max_length=100, description="Filter by country")
    min_ranking: Optional[int] = Field(None, ge=1, description="Minimum QS ranking")
    max_ranking: Optional[int] = Field(None, ge=1, description="Maximum QS ranking")
    min_academic_rigor: Optional[float] = Field(None, ge=0, le=10, description="Minimum academic rigor score")
    min_cultural_diversity: Optional[float] = Field(None, ge=0, le=10, description="Minimum cultural diversity score")
    min_student_life: Optional[float] = Field(None, ge=0, le=10, description="Minimum student life score")
    min_campus_safety: Optional[float] = Field(None, ge=0, le=10, description="Minimum campus safety score")
    language: Optional[str] = Field(None, max_length=50, description="Filter by language of instruction")
    accommodation_required: Optional[bool] = Field(None, description="Require university accommodation")
    language_classes_required: Optional[bool] = Field(None, description="Require local language classes")
    accessibility_required: Optional[bool] = Field(None, description="Require accessibility support")

class RecommendationRequest(BaseModel):
    """Model for recommendation request."""
    academic_importance: int = Field(..., ge=1, le=5, description="Importance of academic rigor (1-5)")
    diversity_importance: int = Field(..., ge=1, le=5, description="Importance of cultural diversity (1-5)")
    student_life_importance: int = Field(..., ge=1, le=5, description="Importance of student life (1-5)")
    safety_importance: int = Field(3, ge=1, le=5, description="Importance of campus safety (1-5)")
    preferred_countries: Optional[List[str]] = Field(None, description="List of preferred countries")
    max_ranking: Optional[int] = Field(None, ge=1, description="Maximum acceptable QS ranking")
    min_overall_score: Optional[float] = Field(None, ge=0, le=10, description="Minimum overall score threshold")

    @validator('preferred_countries')
    def validate_countries(cls, v):
        if v is not None and len(v) > 10:
            raise ValueError('Maximum 10 preferred countries allowed')
        return v

class CountryStats(BaseModel):
    """Model for country statistics."""
    name: str
    university_count: int
    avg_academic_rigor: Optional[float] = None
    avg_cultural_diversity: Optional[float] = None
    avg_student_life: Optional[float] = None
    top_university: Optional[str] = None

class PlatformStats(BaseModel):
    """Model for platform-wide statistics."""
    total_universities: int
    ranked_universities: int
    total_countries: int
    universities_with_feedback: int
    average_academic_rigor: Optional[float] = None
    average_cultural_diversity: Optional[float] = None
    average_student_life: Optional[float] = None
    last_updated: datetime

class PaginationParams(BaseModel):
    """Model for pagination parameters."""
    limit: int = Field(50, ge=1, le=500, description="Number of items to return")
    offset: int = Field(0, ge=0, description="Number of items to skip")

class SortParams(BaseModel):
    """Model for sorting parameters."""
    sort_by: str = Field("qs_rank", description="Field to sort by")
    sort_order: str = Field("asc", regex="^(asc|desc)$", description="Sort order: asc or desc")

    @validator('sort_by')
    def validate_sort_field(cls, v):
        valid_fields = [
            'name', 'city', 'country', 'qs_rank', 'overall_quality',
            'academic_rigor', 'cultural_diversity', 'student_life', 'campus_safety'
        ]
        if v not in valid_fields:
            raise ValueError(f'Invalid sort field. Must be one of: {", ".join(valid_fields)}')
        return v