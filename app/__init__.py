# app/__init__.py
"""
UniSearch Backend Application
University Exchange Platform API
"""

__version__ = "1.0.0"
__author__ = "UniSearch Team"

# app/database/__init__.py
"""
Database package for UniSearch backend.
"""

from .connection import DatabaseManager, db_manager, get_db_connection

__all__ = ["DatabaseManager", "db_manager", "get_db_connection"]

# app/models/__init__.py
"""
Pydantic models for UniSearch API.
"""

from .university import (
    UniversityBase,
    UniversityCreate,
    UniversityResponse,
    UniversityWithScore,
    SearchFilters,
    RecommendationRequest,
    CountryStats,
    PlatformStats,
    PaginationParams,
    SortParams,
    AccommodationType,
    YesNoType
)

__all__ = [
    "UniversityBase",
    "UniversityCreate", 
    "UniversityResponse",
    "UniversityWithScore",
    "SearchFilters",
    "RecommendationRequest",
    "CountryStats",
    "PlatformStats",
    "PaginationParams",
    "SortParams",
    "AccommodationType",
    "YesNoType"
]

# app/routes/__init__.py
"""
API routes for UniSearch backend.
"""

from . import universities, recommendations, filters, health

__all__ = ["universities", "recommendations", "filters", "health"]