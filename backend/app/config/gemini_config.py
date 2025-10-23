"""
Google Gemini API Configuration Module

This module handles all configuration for Google Gemini API integration with LangChain.
It manages environment variables, API credentials, and model configurations.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


class GeminiConfig(BaseSettings):
    """
    Configuration class for Google Gemini API using Pydantic Settings.
    
    This class manages all Gemini API configurations including:
    - API key management
    - Model selection
    - Temperature and other parameters
    - Retry and timeout settings
    
    All settings can be overridden via environment variables.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # API Configuration
    GOOGLE_API_KEY: str = Field(
        default="",
        description="Google Gemini API Key"
    )
    
    # Available Models (as class constants)
    GEMINI_PRO_MODEL: str = "gemini-pro"
    GEMINI_FLASH_MODEL: str = "gemini-1.5-flash"
    GEMINI_PRO_VISION_MODEL: str = "gemini-pro-vision"
    
    # Default Model
    DEFAULT_MODEL: str = Field(
        default="gemini-1.5-flash",
        description="Default Gemini model to use"
    )
    
    # Model Temperatures (controls randomness)
    TEMPERATURE_DEFAULT: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Default temperature for model output"
    )
    TEMPERATURE_DETERMINISTIC: float = 0.0
    TEMPERATURE_CREATIVE: float = 1.0
    
    # Model Parameters
    MAX_TOKENS_DEFAULT: int = Field(
        default=2048,
        gt=0,
        description="Default maximum tokens for output"
    )
    MAX_TOKENS_MAX: int = Field(
        default=4096,
        gt=0,
        description="Maximum allowed tokens"
    )
    
    # Retry Configuration
    MAX_RETRIES: int = Field(
        default=3,
        ge=0,
        description="Maximum number of retry attempts"
    )
    RETRY_DELAY_SECONDS: float = Field(
        default=1.0,
        gt=0,
        description="Initial retry delay in seconds"
    )
    RETRY_BACKOFF_FACTOR: float = Field(
        default=2.0,
        gt=1.0,
        description="Exponential backoff factor"
    )
    RETRY_MAX_WAIT_SECONDS: float = Field(
        default=60.0,
        gt=0,
        description="Maximum wait time between retries"
    )
    
    # Timeout Configuration
    REQUEST_TIMEOUT_SECONDS: int = Field(
        default=30,
        gt=0,
        description="Request timeout in seconds"
    )
    
    # Rate Limiting
    REQUESTS_PER_MINUTE: int = Field(
        default=60,
        gt=0,
        description="Maximum requests per minute"
    )
    
    @field_validator("GOOGLE_API_KEY")
    @classmethod
    def validate_api_key_format(cls, v: str) -> str:
        """Validate API key format if provided."""
        if v and len(v) < 20:
            logger.warning("GOOGLE_API_KEY appears to be invalid (too short)")
        return v
    
    def validate_api_key(self) -> bool:
        """
        Validate that the API key is configured.
        
        Returns:
            bool: True if API key is configured, False otherwise
        """
        if not self.GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY environment variable is not set")
            return False
        if len(self.GOOGLE_API_KEY) < 20:
            logger.warning("GOOGLE_API_KEY appears to be invalid (too short)")
            return False
        return True
    
    def get_api_key(self) -> str:
        """
        Get the API key with validation.
        
        Returns:
            str: The API key
            
        Raises:
            ValueError: If API key is not configured
        """
        if not self.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY environment variable is not set. "
                "Please add it to your .env file."
            )
        return self.GOOGLE_API_KEY
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key programmatically.
        
        Args:
            api_key (str): The Google Gemini API key
            
        Raises:
            ValueError: If the API key format is invalid
        """
        if not api_key or len(api_key) < 20:
            raise ValueError("Invalid API key format")
        self.GOOGLE_API_KEY = api_key
        os.environ["GOOGLE_API_KEY"] = api_key
        logger.info("API key updated successfully")
    
    def get_model_config(
        self,
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
            "model": model or self.DEFAULT_MODEL,
            "temperature": temperature if temperature is not None else self.TEMPERATURE_DEFAULT,
            "max_tokens": max_tokens or self.MAX_TOKENS_DEFAULT,
            "request_timeout": self.REQUEST_TIMEOUT_SECONDS,
        }
    
    def get_retry_config(self) -> dict:
        """
        Get retry configuration.
        
        Returns:
            dict: Retry configuration parameters
        """
        return {
            "max_retries": self.MAX_RETRIES,
            "retry_delay": self.RETRY_DELAY_SECONDS,
            "backoff_factor": self.RETRY_BACKOFF_FACTOR,
            "max_wait": self.RETRY_MAX_WAIT_SECONDS,
        }
    
    @staticmethod
    def is_flash_model(model: str) -> bool:
        """
        Check if the specified model is Flash.
        
        Args:
            model (str): Model name
            
        Returns:
            bool: True if model is Flash variant
        """
        return "flash" in model.lower()
    
    @staticmethod
    def is_pro_model(model: str) -> bool:
        """
        Check if the specified model is Pro.
        
        Args:
            model (str): Model name
            
        Returns:
            bool: True if model is Pro variant
        """
        return "pro" in model.lower() and "flash" not in model.lower()


# Singleton instance for easy access
def get_config() -> GeminiConfig:
    """Get or create the Gemini configuration singleton."""
    if not hasattr(get_config, "_instance"):
        get_config._instance = GeminiConfig()
    return get_config._instance
