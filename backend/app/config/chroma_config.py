"""
ChromaDB Configuration

This module provides configuration for the ChromaDB vector database
used for RAG (Retrieval-Augmented Generation) in the knowledge base.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class ChromaDBConfig(BaseSettings):
    """ChromaDB configuration settings."""
    
    # ChromaDB settings
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION_NAME: str = "architecture_knowledge"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # Embedding settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Sentence transformers model
    EMBEDDING_DIMENSION: int = 384
    
    # Retrieval settings
    DEFAULT_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Client mode: 'persistent' or 'http'
    CHROMA_CLIENT_MODE: str = "persistent"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


@lru_cache()
def get_chroma_config() -> ChromaDBConfig:
    """
    Get cached ChromaDB configuration.
    
    Returns:
        ChromaDBConfig instance
    """
    return ChromaDBConfig()
