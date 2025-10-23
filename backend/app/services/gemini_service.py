"""
Google Gemini Service Module

This module provides a comprehensive wrapper around Google Gemini API
with LangChain integration, supporting both Pro and Flash models.
"""

import logging
from typing import Optional, List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from app.config.gemini_config import GeminiConfig, get_config
from app.utils.api_key_manager import GoogleAPIKeyManager
from app.utils.retry_handler import RetryHandler, RetryConfig, RetryableError
from app.exceptions.gemini_exceptions import (
    GeminiError,
    GeminiConfigError,
    GeminiAPIError,
    GeminiRateLimitError,
    GeminiTimeoutError,
    GeminiAuthenticationError,
)

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Service for interacting with Google Gemini models via LangChain.
    
    Features:
    - Support for Gemini Pro and Flash models
    - Automatic retry logic with exponential backoff
    - Streaming and non-streaming responses
    - Temperature and token customization
    - Error handling and validation
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Gemini service.
        
        Args:
            model: Model name (default: GEMINI_FLASH_MODEL)
            temperature: Temperature for randomness (0.0-1.0)
            max_tokens: Maximum output tokens
            api_key: Google API key (uses env var if not provided)
            
        Raises:
            GeminiError: If initialization fails
        """
        self.config = get_config()
        
        # Initialize API key manager
        if not api_key:
            if not GoogleAPIKeyManager.init_from_env():
                raise GeminiConfigError(
                    "Failed to initialize Google API key. "
                    "Please set GOOGLE_API_KEY environment variable."
                )
            api_key = GoogleAPIKeyManager.get_gemini_key()
        
        self.api_key = api_key
        
        # Get model configuration
        self.model = model or self.config.DEFAULT_MODEL
        self.temperature = temperature if temperature is not None else self.config.TEMPERATURE_DEFAULT
        self.max_tokens = max_tokens or self.config.MAX_TOKENS_DEFAULT
        
        # Validate model
        if not self._is_valid_model(self.model):
            logger.warning(f"Unknown model: {self.model}. Using default.")
            self.model = self.config.DEFAULT_MODEL
        
        # Initialize retry handler
        retry_config = RetryConfig(
            max_retries=self.config.MAX_RETRIES,
            initial_delay=self.config.RETRY_DELAY_SECONDS,
            backoff_factor=self.config.RETRY_BACKOFF_FACTOR,
            max_wait_time=self.config.RETRY_MAX_WAIT_SECONDS,
        )
        self.retry_handler = RetryHandler(retry_config)
        
        # Initialize LangChain ChatGoogleGenerativeAI
        self._client = None
        self._initialize_client()
        
        logger.info(
            f"Gemini service initialized: model={self.model}, "
            f"temperature={self.temperature}, max_tokens={self.max_tokens}"
        )
    
    def _initialize_client(self) -> None:
        """Initialize the ChatGoogleGenerativeAI client."""
        try:
            self._client = ChatGoogleGenerativeAI(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                google_api_key=self.api_key,
                timeout=self.config.REQUEST_TIMEOUT_SECONDS,
            )
            logger.debug(f"LangChain client initialized for model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize LangChain client: {e}")
            raise GeminiConfigError(f"Client initialization failed: {e}", original_error=e)
    
    def _is_valid_model(self, model: str) -> bool:
        """Check if the model name is valid."""
        valid_models = [
            self.config.GEMINI_PRO_MODEL,
            self.config.GEMINI_FLASH_MODEL,
            self.config.GEMINI_PRO_VISION_MODEL,
        ]
        return model in valid_models
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text using Gemini model.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Temperature override
            max_tokens: Max tokens override
            
        Returns:
            str: Generated text
            
        Raises:
            GeminiError: If generation fails
        """
        try:
            messages = self._prepare_messages(prompt, system_prompt)
            
            # Update client if temperature or max_tokens differ
            if (temperature is not None and temperature != self.temperature) or \
               (max_tokens is not None and max_tokens != self.max_tokens):
                self._client.temperature = temperature or self.temperature
                self._client.max_tokens = max_tokens or self.max_tokens
            
            # Execute with retry
            response = self.retry_handler.execute_with_retry(
                self._client.invoke,
                messages
            )
            
            return response.content
        
        except RetryableError as e:
            logger.error(f"Retryable error during generation: {e}")
            raise GeminiAPIError(f"Generation failed after retries: {e}", original_error=e)
        except Exception as e:
            logger.error(f"Error during generation: {e}")
            # Try to map to specific exception types
            error_str = str(e).lower()
            if "rate limit" in error_str or "429" in error_str:
                raise GeminiRateLimitError(original_error=e)
            elif "timeout" in error_str:
                raise GeminiTimeoutError(original_error=e)
            elif "authentication" in error_str or "401" in error_str or "403" in error_str:
                raise GeminiAuthenticationError(original_error=e)
            else:
                raise GeminiAPIError(f"Generation failed: {e}", original_error=e)
    
    def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> Any:
        """
        Generate text using streaming.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            
        Yields:
            str: Streamed text chunks
            
        Raises:
            GeminiError: If streaming fails
        """
        try:
            messages = self._prepare_messages(prompt, system_prompt)
            
            # Execute with retry
            for chunk in self.retry_handler.execute_with_retry(
                self._client.stream,
                messages
            ):
                if hasattr(chunk, 'content'):
                    yield chunk.content
        
        except Exception as e:
            logger.error(f"Error during streaming: {e}")
            raise GeminiAPIError(f"Streaming failed: {e}", original_error=e)
    
    def batch_generate(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
    ) -> List[str]:
        """
        Generate responses for multiple prompts.
        
        Args:
            prompts: List of prompts
            system_prompt: System prompt for all requests
            
        Returns:
            List[str]: Generated responses
            
        Raises:
            GeminiError: If batch generation fails
        """
        responses = []
        
        for i, prompt in enumerate(prompts):
            try:
                logger.debug(f"Processing batch item {i + 1}/{len(prompts)}")
                response = self.generate(prompt, system_prompt)
                responses.append(response)
            except Exception as e:
                logger.error(f"Error processing batch item {i + 1}: {e}")
                responses.append(f"Error: {str(e)}")
        
        return responses
    
    def change_model(
        self,
        model: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> None:
        """
        Change the active model.
        
        Args:
            model: New model name
            temperature: Temperature override
            max_tokens: Max tokens override
            
        Raises:
            GeminiConfigError: If model change fails
        """
        if not self._is_valid_model(model):
            raise GeminiConfigError(f"Invalid model: {model}")
        
        self.model = model
        self.temperature = temperature or self.config.TEMPERATURE_DEFAULT
        self.max_tokens = max_tokens or self.config.MAX_TOKENS_DEFAULT
        
        self._initialize_client()
        logger.info(f"Model changed to: {model}")
    
    def switch_to_flash(self) -> None:
        """Switch to Gemini Flash model."""
        self.change_model(self.config.GEMINI_FLASH_MODEL)
    
    def switch_to_pro(self) -> None:
        """Switch to Gemini Pro model."""
        self.change_model(self.config.GEMINI_PRO_MODEL)
    
    def get_current_model(self) -> str:
        """Get current active model."""
        return self.model
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about current model configuration.
        
        Returns:
            dict: Model information
        """
        return {
            "model": self.model,
            "is_flash": GeminiConfig.is_flash_model(self.model),
            "is_pro": GeminiConfig.is_pro_model(self.model),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "request_timeout": self.config.REQUEST_TIMEOUT_SECONDS,
        }
    
    def get_retry_history(self) -> List[dict]:
        """Get retry attempt history."""
        return self.retry_handler.get_attempt_history()
    
    def clear_retry_history(self) -> None:
        """Clear retry attempt history."""
        self.retry_handler.clear_history()
    
    @staticmethod
    def _prepare_messages(prompt: str, system_prompt: Optional[str] = None) -> List[BaseMessage]:
        """
        Prepare messages for the API.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            
        Returns:
            List[BaseMessage]: Prepared messages
        """
        messages = []
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=prompt))
        
        return messages


class GeminiFlashService(GeminiService):
    """Specialized service for Gemini Flash model."""
    
    def __init__(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize Gemini Flash service."""
        super().__init__(
            model=GeminiConfig.GEMINI_FLASH_MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
        )


class GeminiProService(GeminiService):
    """Specialized service for Gemini Pro model."""
    
    def __init__(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize Gemini Pro service."""
        super().__init__(
            model=GeminiConfig.GEMINI_PRO_MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
        )


# Singleton instances
_gemini_service: Optional[GeminiService] = None
_gemini_flash_service: Optional[GeminiFlashService] = None
_gemini_pro_service: Optional[GeminiProService] = None


def get_gemini_service(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> GeminiService:
    """
    Get or create a Gemini service instance.
    
    Args:
        model: Model name
        temperature: Temperature
        max_tokens: Max tokens
        
    Returns:
        GeminiService: Service instance
    """
    global _gemini_service
    
    if _gemini_service is None:
        _gemini_service = GeminiService(model, temperature, max_tokens)
    
    return _gemini_service


def get_gemini_flash_service() -> GeminiFlashService:
    """Get Gemini Flash service instance."""
    global _gemini_flash_service
    
    if _gemini_flash_service is None:
        _gemini_flash_service = GeminiFlashService()
    
    return _gemini_flash_service


def get_gemini_pro_service() -> GeminiProService:
    """Get Gemini Pro service instance."""
    global _gemini_pro_service
    
    if _gemini_pro_service is None:
        _gemini_pro_service = GeminiProService()
    
    return _gemini_pro_service
