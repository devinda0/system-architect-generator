from typing import Optional, Dict, Any
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.health import router as health_router
from app.api.user import router as user_router
from app.api.gemini import router as gemini_router
from app.config.logging_config import setup_logging
from app.config.gemini_config import get_config
from app.config.mongodb_config import (
    connect_to_mongodb,
    close_mongodb_connection,
    check_mongodb_health
)

# Setup logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="System Architect Generator - API",
    version="0.1.0",
    description="FastAPI application for System Architect Generator with Google Gemini integration",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(gemini_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting System Architect Generator API...")
    
    # Validate Gemini configuration
    try:
        config = get_config()
        if config.validate_api_key():
            logger.info("✓ Google Gemini API key configured successfully")
        else:
            logger.warning("⚠ Google Gemini API key not configured. Some features may not work.")
    except Exception as e:
        logger.error(f"✗ Configuration error: {e}")
    
    # Connect to MongoDB
    try:
        await connect_to_mongodb()
        logger.info("✓ MongoDB connected successfully")
    except Exception as e:
        logger.error(f"✗ MongoDB connection error: {e}")
        logger.warning("⚠ Application will continue without database. Some features may not work.")
    
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down System Architect Generator API...")
    
    # Close MongoDB connection
    try:
        await close_mongodb_connection()
        logger.info("✓ MongoDB connection closed")
    except Exception as e:
        logger.error(f"✗ Error closing MongoDB connection: {e}")
    
    logger.info("Application shutdown complete")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "System Architect Generator API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    # Run with: python -m app.main
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

