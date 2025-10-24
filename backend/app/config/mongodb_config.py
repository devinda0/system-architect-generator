"""
MongoDB Configuration Module

This module handles all configuration for MongoDB integration.
It manages connection pooling, environment variables, and database settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from dotenv import load_dotenv
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


class MongoDBConfig(BaseSettings):
    """
    Configuration class for MongoDB using Pydantic Settings.
    
    This class manages all MongoDB configurations including:
    - Connection URI and credentials
    - Database name
    - Connection pool settings
    - Timeout configurations
    
    All settings can be overridden via environment variables.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # MongoDB Connection Configuration
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI"
    )
    
    MONGODB_DB_NAME: str = Field(
        default="system_architect_generator",
        description="MongoDB database name"
    )
    
    MONGODB_USERNAME: Optional[str] = Field(
        default=None,
        description="MongoDB username (if authentication is required)"
    )
    
    MONGODB_PASSWORD: Optional[str] = Field(
        default=None,
        description="MongoDB password (if authentication is required)"
    )
    
    # Connection Pool Settings
    MONGODB_MIN_POOL_SIZE: int = Field(
        default=10,
        description="Minimum number of connections in the pool",
        ge=1
    )
    
    MONGODB_MAX_POOL_SIZE: int = Field(
        default=100,
        description="Maximum number of connections in the pool",
        ge=1
    )
    
    # Timeout Settings (in milliseconds)
    MONGODB_CONNECT_TIMEOUT_MS: int = Field(
        default=5000,
        description="Connection timeout in milliseconds",
        ge=1000
    )
    
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = Field(
        default=5000,
        description="Server selection timeout in milliseconds",
        ge=1000
    )
    
    MONGODB_SOCKET_TIMEOUT_MS: int = Field(
        default=10000,
        description="Socket timeout in milliseconds",
        ge=1000
    )
    
    # Retry Settings
    MONGODB_RETRY_WRITES: bool = Field(
        default=True,
        description="Enable automatic retry of write operations"
    )
    
    MONGODB_RETRY_READS: bool = Field(
        default=True,
        description="Enable automatic retry of read operations"
    )
    
    # Collection Names
    MONGODB_USERS_COLLECTION: str = Field(
        default="users",
        description="Name of the users collection"
    )
    
    MONGODB_PROJECTS_COLLECTION: str = Field(
        default="projects",
        description="Name of the projects collection"
    )
    
    MONGODB_DESIGNS_COLLECTION: str = Field(
        default="designs",
        description="Name of the designs collection"
    )
    
    MONGODB_FEEDBACK_COLLECTION: str = Field(
        default="feedback",
        description="Name of the feedback collection"
    )
    
    @field_validator("MONGODB_URL")
    @classmethod
    def validate_mongodb_url(cls, v: str) -> str:
        """Validate MongoDB URL format."""
        if not v.startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("MongoDB URL must start with 'mongodb://' or 'mongodb+srv://'")
        return v
    
    @field_validator("MONGODB_MAX_POOL_SIZE")
    @classmethod
    def validate_max_pool_size(cls, v: int, info) -> int:
        """Ensure max pool size is greater than min pool size."""
        values = info.data
        min_pool_size = values.get("MONGODB_MIN_POOL_SIZE", 10)
        if v < min_pool_size:
            raise ValueError(f"max_pool_size ({v}) must be >= min_pool_size ({min_pool_size})")
        return v
    
    def get_connection_uri(self) -> str:
        """
        Build the complete MongoDB connection URI.
        
        Returns:
            Complete MongoDB connection URI with credentials if provided
        """
        if self.MONGODB_USERNAME and self.MONGODB_PASSWORD:
            # Replace the connection string with authenticated version
            if "mongodb://" in self.MONGODB_URL:
                return self.MONGODB_URL.replace(
                    "mongodb://",
                    f"mongodb://{self.MONGODB_USERNAME}:{self.MONGODB_PASSWORD}@"
                )
            elif "mongodb+srv://" in self.MONGODB_URL:
                return self.MONGODB_URL.replace(
                    "mongodb+srv://",
                    f"mongodb+srv://{self.MONGODB_USERNAME}:{self.MONGODB_PASSWORD}@"
                )
        return self.MONGODB_URL
    
    def get_connection_options(self) -> dict:
        """
        Get connection options for MongoDB client.
        
        Returns:
            Dictionary of connection options
        """
        return {
            "minPoolSize": self.MONGODB_MIN_POOL_SIZE,
            "maxPoolSize": self.MONGODB_MAX_POOL_SIZE,
            "connectTimeoutMS": self.MONGODB_CONNECT_TIMEOUT_MS,
            "serverSelectionTimeoutMS": self.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
            "socketTimeoutMS": self.MONGODB_SOCKET_TIMEOUT_MS,
            "retryWrites": self.MONGODB_RETRY_WRITES,
            "retryReads": self.MONGODB_RETRY_READS,
        }


# Global MongoDB client and database instances
_mongodb_client: Optional[AsyncIOMotorClient] = None
_mongodb_database: Optional[AsyncIOMotorDatabase] = None
_config: Optional[MongoDBConfig] = None


def get_mongodb_config() -> MongoDBConfig:
    """
    Get the MongoDB configuration instance (singleton pattern).
    
    Returns:
        MongoDBConfig instance
    """
    global _config
    if _config is None:
        _config = MongoDBConfig()
    return _config


async def connect_to_mongodb() -> AsyncIOMotorDatabase:
    """
    Establish connection to MongoDB with connection pooling.
    
    Returns:
        AsyncIOMotorDatabase instance
        
    Raises:
        ConnectionFailure: If unable to connect to MongoDB
        ServerSelectionTimeoutError: If MongoDB server is unavailable
    """
    global _mongodb_client, _mongodb_database
    
    if _mongodb_database is not None:
        return _mongodb_database
    
    try:
        config = get_mongodb_config()
        connection_uri = config.get_connection_uri()
        connection_options = config.get_connection_options()
        
        logger.info("Connecting to MongoDB...")
        logger.debug(f"MongoDB URI: {connection_uri.split('@')[-1] if '@' in connection_uri else connection_uri}")
        logger.debug(f"Database: {config.MONGODB_DB_NAME}")
        logger.debug(f"Connection pool: {config.MONGODB_MIN_POOL_SIZE}-{config.MONGODB_MAX_POOL_SIZE}")
        
        # Create MongoDB client with connection pooling
        _mongodb_client = AsyncIOMotorClient(
            connection_uri,
            **connection_options
        )
        
        # Test the connection
        await _mongodb_client.admin.command('ping')
        logger.info("✓ Successfully connected to MongoDB")
        
        # Get database
        _mongodb_database = _mongodb_client[config.MONGODB_DB_NAME]
        
        # Create indexes for collections
        await _create_indexes()
        
        return _mongodb_database
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"✗ Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"✗ Unexpected error connecting to MongoDB: {e}")
        raise


async def close_mongodb_connection():
    """
    Close MongoDB connection and cleanup resources.
    """
    global _mongodb_client, _mongodb_database
    
    if _mongodb_client is not None:
        logger.info("Closing MongoDB connection...")
        _mongodb_client.close()
        _mongodb_client = None
        _mongodb_database = None
        logger.info("✓ MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """
    Get the current MongoDB database instance.
    
    Returns:
        AsyncIOMotorDatabase instance
        
    Raises:
        RuntimeError: If database connection is not established
    """
    if _mongodb_database is None:
        raise RuntimeError(
            "MongoDB database is not connected. "
            "Call connect_to_mongodb() first in your application startup."
        )
    return _mongodb_database


async def _create_indexes():
    """
    Create indexes for all collections to improve query performance.
    """
    try:
        config = get_mongodb_config()
        db = _mongodb_database
        
        # Users collection indexes
        await db[config.MONGODB_USERS_COLLECTION].create_index("email", unique=True)
        await db[config.MONGODB_USERS_COLLECTION].create_index("username", unique=True)
        await db[config.MONGODB_USERS_COLLECTION].create_index("created_at")
        
        # Projects collection indexes
        await db[config.MONGODB_PROJECTS_COLLECTION].create_index("user_id")
        await db[config.MONGODB_PROJECTS_COLLECTION].create_index("created_at")
        await db[config.MONGODB_PROJECTS_COLLECTION].create_index("updated_at")
        await db[config.MONGODB_PROJECTS_COLLECTION].create_index([("user_id", 1), ("created_at", -1)])
        
        # Designs collection indexes
        await db[config.MONGODB_DESIGNS_COLLECTION].create_index("project_id")
        await db[config.MONGODB_DESIGNS_COLLECTION].create_index("user_id")
        await db[config.MONGODB_DESIGNS_COLLECTION].create_index("created_at")
        await db[config.MONGODB_DESIGNS_COLLECTION].create_index([("project_id", 1), ("version", -1)])
        
        # Feedback collection indexes
        await db[config.MONGODB_FEEDBACK_COLLECTION].create_index("design_id")
        await db[config.MONGODB_FEEDBACK_COLLECTION].create_index("user_id")
        await db[config.MONGODB_FEEDBACK_COLLECTION].create_index("created_at")
        await db[config.MONGODB_FEEDBACK_COLLECTION].create_index([("design_id", 1), ("created_at", -1)])
        
        logger.info("✓ MongoDB indexes created successfully")
        
    except Exception as e:
        logger.warning(f"⚠ Failed to create some indexes: {e}")


async def check_mongodb_health() -> dict:
    """
    Check MongoDB connection health and return status information.
    
    Returns:
        Dictionary with health status information
    """
    try:
        if _mongodb_client is None:
            return {
                "status": "disconnected",
                "message": "MongoDB client is not initialized"
            }
        
        # Ping the database
        await _mongodb_client.admin.command('ping')
        
        # Get server info
        server_info = await _mongodb_client.server_info()
        
        config = get_mongodb_config()
        
        return {
            "status": "connected",
            "database": config.MONGODB_DB_NAME,
            "mongodb_version": server_info.get("version", "unknown"),
            "connection_pool": {
                "min_size": config.MONGODB_MIN_POOL_SIZE,
                "max_size": config.MONGODB_MAX_POOL_SIZE
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
