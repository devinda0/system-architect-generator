"""
Google Gemini API Configuration Module

This module handles all configuration for Google Gemini API integration with LangChain.
It manages environment variables, API credentials, and model configurations.
"""

import os
from typing import Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


class GeminiConfig:
    """
    Configuration class for Google Gemini API.
    
    This class manages all Gemini API configurations including:
    - API key management
    - Model selection
    - Temperature and other parameters
    - Retry and timeout settings
    """
    
    # API Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Available Models
    GEMINI_PRO_MODEL = "gemini-pro"
    GEMINI_FLASH_MODEL = "gemini-1.5-flash"
    GEMINI_PRO_VISION_MODEL = "gemini-pro-vision"
    
    # Default Model
    DEFAULT_MODEL: str = GEMINI_FLASH_MODEL
    
    # Model Temperatures (controls randomness)
    TEMPERATURE_DEFAULT: float = 0.7
    TEMPERATURE_DETERMINISTIC: float = 0.0
    TEMPERATURE_CREATIVE: float = 1.0
    
    # Model Parameters
    MAX_TOKENS_DEFAULT: int = 2048
    MAX_TOKENS_MAX: int = 4096
    
    # Retry Configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: float = 1.0
    RETRY_BACKOFF_FACTOR: float = 2.0
    RETRY_MAX_WAIT_SECONDS: float = 60.0
    
    # Timeout Configuration
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    # Rate Limiting
    REQUESTS_PER_MINUTE: int = 60
    
    @classmethod
    def validate_api_key(cls) -> bool:
        """
        Validate that the API key is configured.
        
        Returns:
            bool: True if API key is configured, False otherwise
        """
        if not cls.GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY environment variable is not set")
            return False
        if len(cls.GOOGLE_API_KEY) < 20:
            logger.warning("GOOGLE_API_KEY appears to be invalid (too short)")
            return False
        return True
    
    @classmethod
    def get_api_key(cls) -> str:
        """
        Get the API key with validation.
        
        Returns:
            str: The API key
            
        Raises:
            ValueError: If API key is not configured
        """
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY environment variable is not set. "
                "Please add it to your .env file."
            )
        return cls.GOOGLE_API_KEY
    
    @classmethod
    def set_api_key(cls, api_key: str) -> None:
        """
        Set the API key programmatically.
        
        Args:
            api_key (str): The Google Gemini API key
            
        Raises:
            ValueError: If the API key format is invalid
        """
        if not api_key or len(api_key) < 20:
            raise ValueError("Invalid API key format")
        cls.GOOGLE_API_KEY = api_key
        os.environ["GOOGLE_API_KEY"] = api_key
        logger.info("API key updated successfully")
    
    @classmethod
    def get_model_config(
        cls,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> dict:
        """
        Get a complete model configuration.
        
        Args:
            model (str, optional): Model name. Defaults to DEFAULT_MODEL.
            temperature (float, optional): Temperature value. Defaults to TEMPERATURE_DEFAULT.
            max_tokens (int, optional): Max tokens. Defaults to MAX_TOKENS_DEFAULT.
            
        Returns:
            dict: Configuration dictionary for the model
        """
        return {
            "model": model or cls.DEFAULT_MODEL,
            "temperature": temperature if temperature is not None else cls.TEMPERATURE_DEFAULT,
            "max_tokens": max_tokens or cls.MAX_TOKENS_DEFAULT,
            "request_timeout": cls.REQUEST_TIMEOUT_SECONDS,
        }
    
    @classmethod
    def get_retry_config(cls) -> dict:
        """
        Get retry configuration.
        
        Returns:
            dict: Retry configuration parameters
        """
        return {
            "max_retries": cls.MAX_RETRIES,
            "retry_delay": cls.RETRY_DELAY_SECONDS,
            "backoff_factor": cls.RETRY_BACKOFF_FACTOR,
            "max_wait": cls.RETRY_MAX_WAIT_SECONDS,
        }
    
    @classmethod
    def is_flash_model(cls, model: str) -> bool:
        """
        Check if the specified model is Flash.
        
        Args:
            model (str): Model name
            
        Returns:
            bool: True if model is Flash variant
        """
        return "flash" in model.lower()
    
    @classmethod
    def is_pro_model(cls, model: str) -> bool:
        """
        Check if the specified model is Pro.
        
        Args:
            model (str): Model name
            
        Returns:
            bool: True if model is Pro variant
        """
        return "pro" in model.lower() and "flash" not in model.lower()


# Singleton instance
gemini_config = GeminiConfig()
