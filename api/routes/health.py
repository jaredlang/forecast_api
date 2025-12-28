"""
Health check endpoint.
"""
from fastapi import APIRouter
from datetime import datetime

from api.models.responses import HealthResponse
from core.database import test_db_connection
from config import settings

router = APIRouter()


@router.get(
    "/",
    response_model=HealthResponse,
    responses={
        200: {"description": "Service is healthy"},
        503: {"description": "Service is unhealthy"}
    },
    summary="Health check",
    description="Verifies API and database connectivity status"
)
async def health_check():
    """Health check endpoint"""
    db_status = test_db_connection()

    is_healthy = db_status.get("connected", False)

    response = {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "database": {
            "connected": db_status.get("connected", False),
            "instance": db_status.get("instance"),
            "database": db_status.get("database"),
            "version": db_status.get("version"),
            "forecasts_table_exists": db_status.get("forecasts_table_exists"),
            "error": db_status.get("error")
        },
        "api_version": settings.API_VERSION
    }

    return response
