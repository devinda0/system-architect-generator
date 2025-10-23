"""
Integration tests for Gemini Service with comprehensive mocking

This test suite covers:
- JSON parsing functionality
- Rate limiting behavior
- Quota management
- API call logging
- Error handling with various scenarios
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime

from app.services.gemini_service import GeminiService
from app.utils.json_parser import (
    GeminiJSONParser,
    parse_json_response,
    JSONParserError,
    JSONValidationError,
)
from app.utils.rate_limiter import (
    RateLimiter,
    QuotaManager,
    QuotaConfig,
    RateLimitExceeded,
    QuotaExceeded,
)
from app.exceptions.gemini_exceptions import (
    GeminiAPIError,
    GeminiRateLimitError,
    GeminiConfigError,
)
from pydantic import BaseModel, Field


# Test Models
class UserResponse(BaseModel):
    """Test model for JSON parsing."""
    name: str = Field(..., description="User name")
    age: int = Field(..., ge=0, description="User age")
    email: str = Field(..., description="User email")


class ProductResponse(BaseModel):
    """Test model for product data."""
    id: int
    title: str
    price: float
    in_stock: bool


@pytest.fixture
def mock_api_key():
    """Provide a mock API key."""
    return "AIzaSyTestKeyForTestingPurposesOnly123456789"


@pytest.fixture
def mock_langchain_response():
    """Mock LangChain response."""
    response = MagicMock()
    response.content = "This is a test response"
    return response


@pytest.fixture
def mock_json_response():
    """Mock JSON response."""
    response = MagicMock()
    response.content = '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
    return response


class TestJSONParser:
    """Test JSON parser functionality."""
    
    def test_parse_simple_json(self):
        """Test parsing simple JSON string."""
        parser = GeminiJSONParser()
        text = '{"key": "value", "number": 42}'
        
        result = parser.parse(text)
        
        assert result == {"key": "value", "number": 42}
    
    def test_parse_json_from_markdown(self):
        """Test extracting JSON from markdown code blocks."""
        parser = GeminiJSONParser()
        text = """
        Here is your JSON:
        ```json
        {"name": "Alice", "age": 25}
        ```
        """
        
        result = parser.parse(text)
        
        assert result == {"name": "Alice", "age": 25}
    
    def test_parse_json_with_schema(self):
        """Test parsing with Pydantic schema validation."""
        parser = GeminiJSONParser(schema=UserResponse)
        text = '{"name": "Bob", "age": 35, "email": "bob@test.com"}'
        
        result = parser.parse(text)
        
        assert result["name"] == "Bob"
        assert result["age"] == 35
        assert result["email"] == "bob@test.com"
    
    def test_parse_to_model(self):
        """Test parsing directly to Pydantic model."""
        parser = GeminiJSONParser()
        text = '{"name": "Carol", "age": 28, "email": "carol@test.com"}'
        
        result = parser.parse_to_model(text, UserResponse)
        
        assert isinstance(result, UserResponse)
        assert result.name == "Carol"
        assert result.age == 28
    
    def test_parse_invalid_json(self):
        """Test handling of invalid JSON."""
        parser = GeminiJSONParser()
        text = "This is not JSON at all"
        
        with pytest.raises(JSONParserError):
            parser.parse(text)
    
    def test_parse_json_validation_error(self):
        """Test validation error with schema."""
        parser = GeminiJSONParser(schema=UserResponse)
        text = '{"name": "Dave", "age": -5, "email": "dave@test.com"}'  # Invalid age
        
        with pytest.raises(JSONValidationError):
            parser.parse(text)
    
    def test_extract_json_from_text_with_surrounding_content(self):
        """Test extracting JSON embedded in text."""
        parser = GeminiJSONParser()
        text = 'Sure! Here is the data: {"result": "success", "count": 10} Hope this helps!'
        
        result = parser.parse(text)
        
        assert result["result"] == "success"
        assert result["count"] == 10
    
    def test_get_format_instructions(self):
        """Test format instructions generation."""
        parser = GeminiJSONParser(schema=UserResponse)
        
        instructions = parser.get_format_instructions()
        
        assert isinstance(instructions, str)
        assert len(instructions) > 0


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_allows_requests_within_limit(self):
        """Test that requests within limit are allowed."""
        limiter = RateLimiter(requests_per_minute=10)
        
        # Should allow 10 requests
        for _ in range(10):
            assert limiter.acquire(blocking=False) is True
    
    def test_rate_limiter_blocks_excess_requests(self):
        """Test that excess requests are blocked."""
        limiter = RateLimiter(requests_per_minute=5, burst_size=5)
        
        # Use up all tokens
        for _ in range(5):
            limiter.acquire(blocking=False)
        
        # Next request should raise exception
        with pytest.raises(RateLimitExceeded):
            limiter.acquire(blocking=False)
    
    def test_rate_limiter_blocking_wait(self):
        """Test blocking wait for tokens."""
        limiter = RateLimiter(requests_per_minute=60)  # 1 req/sec
        
        # Use up tokens
        limiter.tokens = 0
        
        start = time.time()
        limiter.acquire(tokens=1, blocking=True)
        elapsed = time.time() - start
        
        # Should have waited approximately 1 second
        assert elapsed >= 0.9
    
    def test_rate_limiter_reset(self):
        """Test rate limiter reset."""
        limiter = RateLimiter(requests_per_minute=10)
        
        # Use some tokens
        limiter.acquire(tokens=5, blocking=False)
        assert limiter.tokens < 10
        
        # Reset
        limiter.reset()
        assert limiter.tokens == 10
    
    def test_get_current_rate(self):
        """Test getting current request rate."""
        limiter = RateLimiter(requests_per_minute=60)
        
        # Make some requests
        for _ in range(5):
            limiter.acquire(blocking=False)
        
        rate = limiter.get_current_rate()
        assert rate == 5


class TestQuotaManager:
    """Test quota management functionality."""
    
    def test_quota_manager_allows_within_limits(self):
        """Test requests within quota are allowed."""
        config = QuotaConfig(
            requests_per_minute=10,
            requests_per_hour=100,
            requests_per_day=1000,
        )
        manager = QuotaManager(config)
        
        # Should allow requests within limits
        for _ in range(5):
            manager.check_and_increment()
        
        stats = manager.get_usage_stats()
        assert stats["current_minute"]["requests"] == 5
    
    def test_quota_manager_blocks_over_minute_limit(self):
        """Test quota exceeded for per-minute limit."""
        config = QuotaConfig(requests_per_minute=5)
        manager = QuotaManager(config)
        
        # Use up quota
        for _ in range(5):
            manager.check_and_increment()
        
        # Next request should fail
        with pytest.raises(QuotaExceeded) as exc_info:
            manager.check_and_increment()
        
        assert exc_info.value.quota_type == "minute"
    
    def test_quota_manager_blocks_over_hour_limit(self):
        """Test quota exceeded for per-hour limit."""
        config = QuotaConfig(requests_per_minute=100, requests_per_hour=10)
        manager = QuotaManager(config)
        
        # Use up hour quota
        for _ in range(10):
            manager.check_and_increment()
        
        with pytest.raises(QuotaExceeded) as exc_info:
            manager.check_and_increment()
        
        assert exc_info.value.quota_type == "hour"
    
    def test_quota_manager_tracks_tokens(self):
        """Test token usage tracking."""
        config = QuotaConfig(tokens_per_minute=1000)
        manager = QuotaManager(config)
        
        manager.check_and_increment(tokens=500)
        
        stats = manager.get_usage_stats()
        assert stats["current_minute"]["tokens"] == 500
    
    def test_quota_manager_reset(self):
        """Test quota manager reset."""
        manager = QuotaManager()
        
        # Add some usage
        manager.check_and_increment(tokens=100)
        
        # Reset
        manager.reset()
        
        stats = manager.get_usage_stats()
        assert stats["total_requests"] == 0
        assert stats["total_tokens"] == 0
    
    def test_get_usage_stats(self):
        """Test usage statistics retrieval."""
        config = QuotaConfig(requests_per_minute=60)
        manager = QuotaManager(config)
        
        manager.check_and_increment(tokens=100)
        
        stats = manager.get_usage_stats()
        
        assert "total_requests" in stats
        assert "current_minute" in stats
        assert "current_hour" in stats
        assert "current_day" in stats
        assert stats["current_minute"]["remaining"] == 59


class TestGeminiServiceIntegration:
    """Integration tests for GeminiService with mocking."""
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_service_with_rate_limiting(self, mock_langchain, mock_api_key, mock_langchain_response):
        """Test service with rate limiting enabled."""
        mock_langchain.return_value.invoke.return_value = mock_langchain_response
        
        service = GeminiService(
            api_key=mock_api_key,
            enable_rate_limiting=True,
        )
        
        # Make requests
        for _ in range(3):
            result = service.generate("test prompt")
            assert result == "This is a test response"
        
        # Check rate limiter stats
        rate_info = service.get_rate_limit_info()
        assert rate_info["enabled"] is True
        assert rate_info["current_rate"] == 3
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_service_with_quota_management(self, mock_langchain, mock_api_key, mock_langchain_response):
        """Test service with quota management enabled."""
        mock_langchain.return_value.invoke.return_value = mock_langchain_response
        
        service = GeminiService(
            api_key=mock_api_key,
            enable_quota_management=True,
        )
        
        # Make requests
        for _ in range(5):
            service.generate("test prompt")
        
        # Check quota stats
        quota_stats = service.get_quota_stats()
        assert quota_stats["enabled"] is True
        assert quota_stats["total_requests"] == 5
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_service_logging(self, mock_langchain, mock_api_key, mock_langchain_response, caplog):
        """Test API call logging."""
        mock_langchain.return_value.invoke.return_value = mock_langchain_response
        
        service = GeminiService(api_key=mock_api_key)
        
        with caplog.at_level("INFO"):
            service.generate("test prompt")
        
        # Check logs
        log_messages = [record.message for record in caplog.records]
        assert any("Starting generation" in msg for msg in log_messages)
        assert any("Generation completed" in msg for msg in log_messages)
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_rate_limit_exceeded_handling(self, mock_langchain, mock_api_key):
        """Test handling when rate limit is exceeded."""
        service = GeminiService(
            api_key=mock_api_key,
            enable_rate_limiting=True,
        )
        
        # Set rate limiter to exhausted state
        service.rate_limiter.tokens = 0
        
        with pytest.raises(GeminiRateLimitError):
            service.generate("test prompt")
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_quota_exceeded_handling(self, mock_langchain, mock_api_key):
        """Test handling when quota is exceeded."""
        config = QuotaConfig(requests_per_minute=1)
        
        service = GeminiService(
            api_key=mock_api_key,
            enable_quota_management=True,
        )
        service.quota_manager = QuotaManager(config)
        
        mock_response = MagicMock()
        mock_response.content = "test"
        mock_langchain.return_value.invoke.return_value = mock_response
        
        # First request should work
        service.generate("test")
        
        # Second request should fail
        with pytest.raises(GeminiRateLimitError):
            service.generate("test")
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_service_without_rate_limiting(self, mock_langchain, mock_api_key, mock_langchain_response):
        """Test service with rate limiting disabled."""
        mock_langchain.return_value.invoke.return_value = mock_langchain_response
        
        service = GeminiService(
            api_key=mock_api_key,
            enable_rate_limiting=False,
            enable_quota_management=False,
        )
        
        result = service.generate("test prompt")
        assert result == "This is a test response"
        
        # Check disabled features
        rate_info = service.get_rate_limit_info()
        assert rate_info["enabled"] is False
        
        quota_stats = service.get_quota_stats()
        assert quota_stats["enabled"] is False
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_json_response_parsing(self, mock_langchain, mock_api_key):
        """Test parsing JSON responses from Gemini."""
        mock_response = MagicMock()
        mock_response.content = '{"name": "Test User", "age": 25, "email": "test@example.com"}'
        mock_langchain.return_value.invoke.return_value = mock_response
        
        service = GeminiService(api_key=mock_api_key)
        response = service.generate("Generate user data")
        
        # Parse the response
        parser = GeminiJSONParser(schema=UserResponse)
        result = parser.parse(response)
        
        assert result["name"] == "Test User"
        assert result["age"] == 25
        assert result["email"] == "test@example.com"
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_batch_generation_with_rate_limiting(self, mock_langchain, mock_api_key):
        """Test batch generation with rate limiting."""
        mock_response = MagicMock()
        mock_response.content = "response"
        mock_langchain.return_value.invoke.return_value = mock_response
        
        service = GeminiService(
            api_key=mock_api_key,
            enable_rate_limiting=True,
        )
        
        prompts = ["prompt1", "prompt2", "prompt3"]
        results = service.batch_generate(prompts)
        
        assert len(results) == 3
        assert all(r == "response" for r in results)


class TestErrorScenarios:
    """Test various error scenarios."""
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_api_error_logging(self, mock_langchain, mock_api_key, caplog):
        """Test that API errors are properly logged."""
        mock_langchain.return_value.invoke.side_effect = Exception("API Error")
        
        service = GeminiService(api_key=mock_api_key)
        
        with caplog.at_level("ERROR"):
            with pytest.raises(GeminiAPIError):
                service.generate("test")
        
        # Check error was logged
        assert any("Error during generation" in record.message for record in caplog.records)
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_timeout_error_handling(self, mock_langchain, mock_api_key):
        """Test timeout error handling."""
        mock_langchain.return_value.invoke.side_effect = Exception("timeout")
        
        service = GeminiService(api_key=mock_api_key)
        
        with pytest.raises(GeminiAPIError):
            service.generate("test")
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_authentication_error_handling(self, mock_langchain, mock_api_key):
        """Test authentication error handling."""
        mock_langchain.return_value.invoke.side_effect = Exception("401 authentication failed")
        
        service = GeminiService(api_key=mock_api_key)
        
        with pytest.raises(GeminiAPIError):
            service.generate("test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
