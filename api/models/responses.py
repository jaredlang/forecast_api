"""
Pydantic response models for API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# Weather Endpoint Models
class ForecastMetadata(BaseModel):
    encoding: str
    language: Optional[str] = None
    locale: Optional[str] = None
    sizes: Dict[str, int]


class ForecastData(BaseModel):
    text: str = Field(..., description="Forecast text content")
    audio_base64: str = Field(..., description="Base64-encoded audio WAV data")
    forecast_at: str = Field(..., description="When forecast was made (ISO 8601)")
    expires_at: str = Field(..., description="When forecast expires (ISO 8601)")
    age_seconds: int = Field(..., description="Age of forecast in seconds")
    metadata: ForecastMetadata


class WeatherResponse(BaseModel):
    status: str = "success"
    city: str
    forecast: ForecastData


class WeatherNotFoundResponse(BaseModel):
    status: str = "error"
    message: str


# History Endpoint Models
class HistoricalForecast(BaseModel):
    forecast_id: str
    forecast_at: str
    expires_at: str
    expired: bool
    encoding: str
    language: Optional[str] = None
    locale: Optional[str] = None
    sizes: Dict[str, int]
    created_at: str


class HistoryResponse(BaseModel):
    status: str = "success"
    city: str
    count: int
    forecasts: List[HistoricalForecast]


# Stats Endpoint Models
class CityStatistics(BaseModel):
    city: str
    forecast_count: int
    total_text_bytes: int
    total_audio_bytes: int
    latest_forecast: Optional[str] = None


class StorageStatistics(BaseModel):
    total_forecasts: int
    total_text_bytes: int
    total_audio_bytes: int
    encodings_used: Dict[str, int]
    languages_used: Dict[str, int]
    city_breakdown: List[CityStatistics]


class StatsResponse(BaseModel):
    status: str = "success"
    statistics: StorageStatistics


# Health Endpoint Models
class DatabaseHealth(BaseModel):
    connected: bool
    instance: Optional[str] = None
    database: Optional[str] = None
    version: Optional[str] = None
    forecasts_table_exists: Optional[bool] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database: DatabaseHealth
    api_version: str


# Generic Error Response
class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    detail: Optional[Dict[str, Any]] = None
