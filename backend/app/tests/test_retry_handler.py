"""
Test suite for Retry Handler

Tests for the retry handler with exponential backoff functionality.
"""

import pytest
import asyncio
import time
from app.utils.retry_handler import (
    RetryConfig,
    RetryHandler,
    RetryableError,
    RateLimitError,
    ServiceUnavailableError,
    retry,
    async_retry,
)


class TestRetryConfig:
    """Tests for RetryConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = RetryConfig()
        
        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.backoff_factor == 2.0
        assert config.max_wait_time == 60.0
        assert config.jitter is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = RetryConfig(
            max_retries=5,
            initial_delay=0.5,
            backoff_factor=1.5,
            max_wait_time=30.0,
            jitter=False,
        )
        
        assert config.max_retries == 5
        assert config.initial_delay == 0.5
        assert config.backoff_factor == 1.5
        assert config.max_wait_time == 30.0
        assert config.jitter is False
    
    def test_exponential_backoff_calculation(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(
            initial_delay=1.0,
            backoff_factor=2.0,
            jitter=False,
        )
        
        assert config.get_wait_time(0) == 1.0
        assert config.get_wait_time(1) == 2.0
        assert config.get_wait_time(2) == 4.0
        assert config.get_wait_time(3) == 8.0
    
    def test_max_wait_time_capping(self):
        """Test that wait time is capped at max_wait_time."""
        config = RetryConfig(
            initial_delay=1.0,
            backoff_factor=2.0,
            max_wait_time=10.0,
            jitter=False,
        )
        
        # Without capping: 1 * 2^5 = 32, but capped at 10
        assert config.get_wait_time(5) == 10.0


class TestRetryHandler:
    """Tests for RetryHandler."""
    
    def test_should_retry_retryable_exception(self):
        """Test should_retry with retryable exception."""
        handler = RetryHandler()
        exception = RateLimitError("Rate limited")
        
        assert handler.should_retry(exception, 0) is True
        assert handler.should_retry(exception, 1) is True
        assert handler.should_retry(exception, 2) is True
    
    def test_should_not_retry_max_attempts_exceeded(self):
        """Test should_retry when max attempts exceeded."""
        handler = RetryHandler()
        exception = RateLimitError("Rate limited")
        
        # With default max_retries=3, attempt 3 (0-indexed) exceeds max
        assert handler.should_retry(exception, 3) is False
    
    def test_should_not_retry_non_retryable_exception(self):
        """Test should_retry with non-retryable exception."""
        handler = RetryHandler()
        exception = ValueError("Invalid input")
        
        assert handler.should_retry(exception, 0) is False
    
    def test_execute_with_retry_success_first_attempt(self):
        """Test successful execution on first attempt."""
        handler = RetryHandler()
        
        def success_func():
            return "Success"
        
        result = handler.execute_with_retry(success_func)
        
        assert result == "Success"
        assert len(handler.attempt_history) == 0
    
    def test_execute_with_retry_success_after_retries(self):
        """Test successful execution after retries."""
        handler = RetryHandler(RetryConfig(initial_delay=0.01))
        attempt_count = [0]
        
        def sometimes_fails():
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise RateLimitError("Retry me")
            return "Success after retries"
        
        result = handler.execute_with_retry(sometimes_fails)
        
        assert result == "Success after retries"
        assert attempt_count[0] == 3
    
    def test_execute_with_retry_all_attempts_fail(self):
        """Test execution when all attempts fail."""
        handler = RetryHandler(RetryConfig(max_retries=2, initial_delay=0.01))
        
        def always_fails():
            raise RateLimitError("Always fails")
        
        with pytest.raises(RateLimitError):
            handler.execute_with_retry(always_fails)
    
    def test_attempt_history_recording(self):
        """Test that attempt history is recorded."""
        handler = RetryHandler(RetryConfig(max_retries=2, initial_delay=0.01))
        attempt_count = [0]
        
        def fails_twice():
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise RateLimitError(f"Attempt {attempt_count[0]} failed")
            return "Success"
        
        handler.execute_with_retry(fails_twice)
        
        history = handler.get_attempt_history()
        assert len(history) == 2
        assert all(h["exception_type"] == "RateLimitError" for h in history)
    
    def test_clear_history(self):
        """Test clearing attempt history."""
        handler = RetryHandler(RetryConfig(max_retries=1, initial_delay=0.01))
        
        def fails_once():
            raise RateLimitError("Failed")
        
        try:
            handler.execute_with_retry(fails_once)
        except RateLimitError:
            pass
        
        assert len(handler.get_attempt_history()) > 0
        handler.clear_history()
        assert len(handler.get_attempt_history()) == 0


class TestAsyncRetryHandler:
    """Tests for async retry handler."""
    
    @pytest.mark.asyncio
    async def test_async_execute_with_retry_success(self):
        """Test successful async execution."""
        handler = RetryHandler()
        
        async def async_success():
            return "Async success"
        
        result = await handler.execute_with_retry_async(async_success)
        
        assert result == "Async success"
    
    @pytest.mark.asyncio
    async def test_async_execute_with_retry_after_failures(self):
        """Test async execution with retries."""
        handler = RetryHandler(RetryConfig(initial_delay=0.01))
        attempt_count = [0]
        
        async def async_sometimes_fails():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise ServiceUnavailableError("Service unavailable")
            return "Success"
        
        result = await handler.execute_with_retry_async(async_sometimes_fails)
        
        assert result == "Success"
        assert attempt_count[0] == 2
    
    @pytest.mark.asyncio
    async def test_async_execute_all_attempts_fail(self):
        """Test async execution when all attempts fail."""
        handler = RetryHandler(RetryConfig(max_retries=1, initial_delay=0.01))
        
        async def async_always_fails():
            raise ServiceUnavailableError("Always fails")
        
        with pytest.raises(ServiceUnavailableError):
            await handler.execute_with_retry_async(async_always_fails)


class TestRetryDecorators:
    """Tests for retry decorators."""
    
    def test_retry_decorator(self):
        """Test sync retry decorator."""
        attempt_count = [0]
        
        @retry(RetryConfig(initial_delay=0.01))
        def decorated_func():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise RateLimitError("Retry")
            return "Success"
        
        result = decorated_func()
        
        assert result == "Success"
        assert attempt_count[0] == 2
    
    @pytest.mark.asyncio
    async def test_async_retry_decorator(self):
        """Test async retry decorator."""
        attempt_count = [0]
        
        @async_retry(RetryConfig(initial_delay=0.01))
        async def decorated_async_func():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise RateLimitError("Retry")
            return "Async success"
        
        result = await decorated_async_func()
        
        assert result == "Async success"
        assert attempt_count[0] == 2


class TestRetryableErrors:
    """Tests for different retryable error types."""
    
    def test_rate_limit_error_is_retryable(self):
        """Test that RateLimitError is retryable."""
        handler = RetryHandler()
        exception = RateLimitError("429 Too Many Requests")
        
        assert handler.should_retry(exception, 0) is True
    
    def test_service_unavailable_error_is_retryable(self):
        """Test that ServiceUnavailableError is retryable."""
        handler = RetryHandler()
        exception = ServiceUnavailableError("503 Service Unavailable")
        
        assert handler.should_retry(exception, 0) is True
    
    def test_timeout_error_is_retryable(self):
        """Test that TimeoutError is retryable."""
        handler = RetryHandler()
        exception = TimeoutError("Request timed out")
        
        assert handler.should_retry(exception, 0) is True
