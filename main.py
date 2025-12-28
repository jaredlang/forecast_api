"""
FastAPI application entry point for Weather Forecast API.
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api.routes import weather, stats, health
from core.database import test_db_connection, cleanup_db_connection

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Weather Forecast API")
    conn_status = test_db_connection()
    if conn_status["connected"]:
        logger.info(f"Database connected: {conn_status['instance']}")
    else:
        logger.error(f"Database connection failed: {conn_status.get('error')}")

    yield

    # Shutdown
    logger.info("Shutting down Weather Forecast API")
    cleanup_db_connection()


# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include routers
app.include_router(weather.router, prefix="/weather", tags=["Weather"])
app.include_router(stats.router, prefix="/stats", tags=["Statistics"])
app.include_router(health.router, prefix="/health", tags=["Health"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.RELOAD
    )
