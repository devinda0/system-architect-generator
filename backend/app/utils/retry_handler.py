"""
Retry Handler Module with Exponential Backoff

This module provides robust error handling and retry logic for API calls
with exponential backoff strategy.
"""

import asyncio
import logging
import time
from typing import Callable, Optional, Type, Union, Any, List
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_wait_time: float = 60.0,
        jitter: bool = True,
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            backoff_factor: Multiplier for exponential backoff
            max_wait_time: Maximum wait time between retries
            jitter: Whether to add randomness to backoff
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_wait_time = max_wait_time
        self.jitter = jitter
    
    def get_wait_time(self, attempt: int) -> float:
        """
        Calculate wait time for exponential backoff.
        
        Args:
            attempt: Attempt number (0-indexed)
            
        Returns:
            float: Wait time in seconds
        """
        wait_time = self.initial_delay * (self.backoff_factor ** attempt)
        wait_time = min(wait_time, self.max_wait_time)
        
        if self.jitter:
            import random
            wait_time *= (0.5 + random.random())
        
        return wait_time


class RetryableError(Exception):
    """Base exception for retryable errors."""
    pass


class RateLimitError(RetryableError):
    """Rate limit error (429)."""
    pass


class ServiceUnavailableError(RetryableError):
    """Service unavailable error (503)."""
    pass


class TimeoutError(RetryableError):
    """Timeout error."""
    pass


class APIError(Exception):
    """Base exception for non-retryable API errors."""
    pass


class RetryHandler:
    """
    Handles retries with exponential backoff for API calls.
    """
    
    # Retryable HTTP status codes
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
    
    # Retryable exception types
    RETRYABLE_EXCEPTIONS: tuple = (
        RetryableError,
        RateLimitError,
        ServiceUnavailableError,
        TimeoutError,
        ConnectionError,
        TimeoutError,
    )
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """
        Initialize retry handler.
        
        Args:
            config: RetryConfig instance or None for defaults
        """
        self.config = config or RetryConfig()
        self.attempt_history: List[dict] = []
    
    def should_retry(
        self,
        exception: Exception,
        attempt: int,
        retryable_exceptions: tuple = RETRYABLE_EXCEPTIONS,
    ) -> bool:
        """
        Determine if an exception should trigger a retry.
        
        Args:
            exception: The exception that occurred
            attempt: Current attempt number (0-indexed)
            retryable_exceptions: Tuple of retryable exception types
            
        Returns:
            bool: True if should retry
        """
        if attempt >= self.config.max_retries:
            return False
        
        return isinstance(exception, retryable_exceptions)
    
    def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a function with retry logic (synchronous).
        
        Args:
            func: Callable to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Any: Function return value
            
        Raises:
            Exception: The last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.config.max_retries + 1}")
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Request succeeded after {attempt} retries")
                
                return result
            
            except Exception as e:
                last_exception = e
                
                # Record attempt
                self.attempt_history.append({
                    "attempt": attempt,
                    "timestamp": datetime.now(),
                    "exception": str(e),
                    "exception_type": type(e).__name__,
                })
                
                if not self.should_retry(e, attempt):
                    logger.error(f"Non-retryable error: {e}")
                    raise
                
                wait_time = self.config.get_wait_time(attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {wait_time:.2f} seconds..."
                )
                time.sleep(wait_time)
        
        logger.error(f"All {self.config.max_retries + 1} attempts failed")
        raise last_exception
    
    async def execute_with_retry_async(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute an async function with retry logic.
        
        Args:
            func: Async callable to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Any: Function return value
            
        Raises:
            Exception: The last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                logger.debug(f"Async Attempt {attempt + 1}/{self.config.max_retries + 1}")
                result = await func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Async request succeeded after {attempt} retries")
                
                return result
            
            except Exception as e:
                last_exception = e
                
                # Record attempt
                self.attempt_history.append({
                    "attempt": attempt,
                    "timestamp": datetime.now(),
                    "exception": str(e),
                    "exception_type": type(e).__name__,
                })
                
                if not self.should_retry(e, attempt):
                    logger.error(f"Non-retryable error: {e}")
                    raise
                
                wait_time = self.config.get_wait_time(attempt)
                logger.warning(
                    f"Async Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {wait_time:.2f} seconds..."
                )
                await asyncio.sleep(wait_time)
        
        logger.error(f"All {self.config.max_retries + 1} async attempts failed")
        raise last_exception
    
    def get_attempt_history(self) -> List[dict]:
        """Get history of retry attempts."""
        return self.attempt_history.copy()
    
    def clear_history(self) -> None:
        """Clear attempt history."""
        self.attempt_history.clear()


def retry(
    config: Optional[RetryConfig] = None,
    retryable_exceptions: tuple = RetryHandler.RETRYABLE_EXCEPTIONS,
):
    """
    Decorator for adding retry logic to functions.
    
    Args:
        config: RetryConfig instance
        retryable_exceptions: Tuple of exception types to retry
        
    Returns:
        Decorator function
    """
    _config = config or RetryConfig()
    handler = RetryHandler(_config)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return handler.execute_with_retry(func, *args, **kwargs)
        
        return wrapper
    
    return decorator


def async_retry(
    config: Optional[RetryConfig] = None,
    retryable_exceptions: tuple = RetryHandler.RETRYABLE_EXCEPTIONS,
):
    """
    Decorator for adding retry logic to async functions.
    
    Args:
        config: RetryConfig instance
        retryable_exceptions: Tuple of exception types to retry
        
    Returns:
        Decorator function
    """
    _config = config or RetryConfig()
    handler = RetryHandler(_config)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await handler.execute_with_retry_async(func, *args, **kwargs)
        
        return wrapper
    
    return decorator
