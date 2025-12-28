"""
Statistics endpoint.
"""
from fastapi import APIRouter

from api.models.responses import StatsResponse, ErrorResponse
from core.database import get_storage_stats
from core.exceptions import DatabaseConnectionError

router = APIRouter()


@router.get(
    "/",
    response_model=StatsResponse,
    responses={
        200: {"description": "Successful response with storage statistics"},
        503: {"model": ErrorResponse, "description": "Database connection error"}
    },
    summary="Get storage statistics",
    description="Retrieves database storage statistics including forecast counts and sizes"
)
async def get_stats():
    """Get storage statistics"""
    try:
        result = get_storage_stats()

        if result.get("status") == "error":
            raise DatabaseConnectionError(result.get("message", "Database error"))

        return {
            "status": "success",
            "statistics": {
                "total_forecasts": result["total_forecasts"],
                "total_text_bytes": result["total_text_bytes"],
                "total_audio_bytes": result["total_audio_bytes"],
                "encodings_used": result["encodings_used"],
                "languages_used": result["languages_used"],
                "city_breakdown": result["city_breakdown"]
            }
        }
    except DatabaseConnectionError:
        raise
    except Exception as e:
        raise DatabaseConnectionError(f"Unexpected error: {str(e)}")
