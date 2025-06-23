"""
API Routes Package

FastAPI router modules for all endpoints.
"""

from . import universities, recommendations, filters, health

__all__ = [
    "universities",
    "recommendations", 
    "filters",
    "health"
]