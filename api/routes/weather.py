"""
Weather forecast endpoints.
"""
from fastapi import APIRouter, Query, Path
from typing import Optional
import asyncio
import httpx

from api.models.responses import (
    WeatherResponse,
    WeatherNotFoundResponse,
    HistoryResponse,
    ErrorResponse
)
from core.database import get_cached_forecast, list_forecasts
from core.exceptions import ForecastNotFoundError, DatabaseConnectionError
from datetime import datetime
from config import settings

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

def trigger_forecast_preparation(city: str, language: Optional[str] = None):
    """
    Trigger async forecast preparation using Weather Agent API.

    Args:
        city: City name to prepare forecast for
        language: Optional language code for the forecast
    """
    if not settings.WEATHER_AGENT_URL:
        logger.warning("WEATHER_AGENT_URL not configured, skipping forecast preparation")
        return

    try:
        # Create session and send message synchronously (fire and forget)
        import threading

        def make_api_calls():
            try:
                # Generate unique session ID
                session_id = f"forecast_api_{city}_{language or 'default'}"
                user_id = "forecast_api"

                # Create prompt for forecast generation
                language_spec = f" in {language}" if language else ""
                prompt = f"What is the current weather condition in {city}{language_spec}"

                with httpx.Client(timeout=30.0) as client:
                    # Step 1: Create a session
                    session_url = f"{settings.WEATHER_AGENT_URL}/apps/weather_agent/users/{user_id}/sessions/{session_id}"
                    session_response = client.post(
                        session_url,
                        headers={"Content-Type": "application/json"},
                        json={}
                    )
                    session_response.raise_for_status()
                    logger.info(f"Created session {session_id} for {city}")

                    # Step 2: Send a message
                    message_url = f"{settings.WEATHER_AGENT_URL}/run_sse"
                    message_payload = {
                        "appName": "weather_agent",
                        "userId": user_id,
                        "sessionId": session_id,
                        "newMessage": {
                            "role": "user",
                            "parts": [{"text": prompt}]
                        },
                        "streaming": False
                    }

                    message_response = client.post(
                        message_url,
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "text/event-stream"
                        },
                        json=message_payload
                    )
                    message_response.raise_for_status()
                    logger.info(f"Sent forecast request for {city}")

            except Exception as e:
                logger.warning(f"Failed to trigger forecast for {city}: {str(e)}")

        # Run in background thread (fire and forget)
        thread = threading.Thread(target=make_api_calls, daemon=True)
        thread.start()

    except Exception as e:
        # Log error but don't fail the request
        logger.warning(f"Failed to start forecast preparation for {city}: {str(e)}")


@router.get(
    "/{city}",
    response_model=WeatherResponse,
    responses={
        200: {"description": "Successful response with forecast data"},
        404: {"model": WeatherNotFoundResponse, "description": "Forecast not found"},
        503: {"model": ErrorResponse, "description": "Database connection error"}
    },
    summary="Get latest forecast for a city",
    description="Retrieves the most recent valid (non-expired) forecast for the specified city"
)
async def get_latest_forecast(
    city: str = Path(..., description="City name (case-insensitive)"),
    language: Optional[str] = Query(None, description="ISO 639-1 language code filter")
):
    """Get the latest forecast for a city"""
    try:
        result = get_cached_forecast(city, language)

        if result.get("status") == "error":
            raise DatabaseConnectionError(result.get("message", "Database error"))

        if not result.get("cached"):
            raise ForecastNotFoundError(city)

        return {
            "status": "success",
            "city": city.lower(),
            "forecast": {
                "text": result["forecast_text"],
                "audio_base64": result["audio_data"],
                "forecast_at": result["forecast_at"],
                "expires_at": result["expires_at"],
                "age_seconds": result["age_seconds"],
                "metadata": {
                    "encoding": result["encoding"],
                    "language": result.get("language"),
                    "locale": result.get("locale"),
                    "sizes": result["sizes"]
                }
            }
        }
    except ForecastNotFoundError as e:
        # Trigger async forecast preparation when forecast not found (non-blocking)
        logger.warning(f"triggering forecast preparation for {city}: {str(e)}")
        trigger_forecast_preparation(city, language)

        # Still raise the original error
        raise
    except DatabaseConnectionError:
        raise
    except Exception as e:
        # Log unexpected errors but don't mask their type
        logger.error(f"Unexpected error in get_latest_forecast: {str(e)}", exc_info=True)
        raise


@router.get(
    "/{city}/history",
    response_model=HistoryResponse,
    responses={
        200: {"description": "Successful response with forecast history"},
        503: {"model": ErrorResponse, "description": "Database connection error"}
    },
    summary="Get forecast history for a city",
    description="Retrieves historical forecasts for a city with optional filtering"
)
async def get_forecast_history(
    city: str = Path(..., description="City name"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    include_expired: bool = Query(False, description="Include expired forecasts")
):
    """Get forecast history for a city"""
    try:
        result = list_forecasts(city=city, limit=limit)

        if result.get("status") == "error":
            raise DatabaseConnectionError(result.get("message", "Database error"))

        forecasts = result.get("forecasts", [])

        # Filter expired if requested
        if not include_expired:
            forecasts = [f for f in forecasts if not f.get("expired", False)]

        return {
            "status": "success",
            "city": city.lower(),
            "count": len(forecasts),
            "forecasts": forecasts
        }
    except DatabaseConnectionError:
        raise
    except Exception as e:
        raise DatabaseConnectionError(f"Unexpected error: {str(e)}")
