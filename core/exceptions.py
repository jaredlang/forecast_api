"""
Custom exceptions for API error handling.
"""
from fastapi import HTTPException, status


class ForecastNotFoundError(HTTPException):
    def __init__(self, city: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No valid forecast found for city: {city}"
        )


class DatabaseConnectionError(HTTPException):
    def __init__(self, message: str = "Database connection failed"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=message
        )


class InvalidParameterError(HTTPException):
    def __init__(self, parameter: str, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter '{parameter}': {message}"
        )
