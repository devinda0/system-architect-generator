"""
Test suite for Gemini Service

Tests for the GeminiService class and related functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.gemini_service import (
    GeminiService,
    GeminiFlashService,
    GeminiProService,
    GeminiServiceError,
)
from app.config.gemini_config import GeminiConfig


@pytest.fixture
def mock_api_key():
    """Provide a mock API key."""
    return "AIzaSyTestKeyForTestingPurposesOnly123456789"


@pytest.fixture
def gemini_config():
    """Provide Gemini config instance."""
    return GeminiConfig()


@pytest.fixture
def mock_langchain_client():
    """Mock LangChain client."""
    client = MagicMock()
    client.invoke = MagicMock()
    return client


class TestGeminiServiceInitialization:
    """Tests for Gemini service initialization."""
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    @patch("app.services.gemini_service.GoogleAPIKeyManager.init_from_env")
    @patch("app.services.gemini_service.GoogleAPIKeyManager.get_gemini_key")
    def test_init_with_default_config(
        self,
        mock_get_key,
        mock_init_env,
        mock_langchain,
        mock_api_key,
    ):
        """Test initialization with default configuration."""
        mock_init_env.return_value = True
        mock_get_key.return_value = mock_api_key
        
        service = GeminiService(api_key=mock_api_key)
        
        assert service.model == GeminiConfig.GEMINI_FLASH_MODEL
        assert service.temperature == GeminiConfig.TEMPERATURE_DEFAULT
        assert service.max_tokens == GeminiConfig.MAX_TOKENS_DEFAULT
        assert service.api_key == mock_api_key
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_init_with_custom_config(self, mock_langchain, mock_api_key):
        """Test initialization with custom configuration."""
        service = GeminiService(
            model=GeminiConfig.GEMINI_PRO_MODEL,
            temperature=0.5,
            max_tokens=1024,
            api_key=mock_api_key,
        )
        
        assert service.model == GeminiConfig.GEMINI_PRO_MODEL
        assert service.temperature == 0.5
        assert service.max_tokens == 1024
    
    @patch("app.services.gemini_service.GoogleAPIKeyManager.init_from_env")
    def test_init_fails_without_api_key(self, mock_init_env):
        """Test initialization fails when API key is not available."""
        mock_init_env.return_value = False
        
        with pytest.raises(GeminiServiceError):
            GeminiService()


class TestGeminiServiceGenerate:
    """Tests for text generation."""
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_generate_success(self, mock_langchain, mock_api_key):
        """Test successful text generation."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.content = "Generated text response"
        mock_langchain.return_value.invoke.return_value = mock_response
        
        service = GeminiService(api_key=mock_api_key)
        service._client = mock_langchain.return_value
        
        result = service.generate("Test prompt")
        
        assert result == "Generated text response"
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_generate_with_system_prompt(self, mock_langchain, mock_api_key):
        """Test generation with system prompt."""
        mock_response = MagicMock()
        mock_response.content = "Response with context"
        mock_langchain.return_value.invoke.return_value = mock_response
        
        service = GeminiService(api_key=mock_api_key)
        service._client = mock_langchain.return_value
        
        result = service.generate(
            "User prompt",
            system_prompt="You are a helpful assistant"
        )
        
        assert result == "Response with context"


class TestGeminiServiceModelSwitching:
    """Tests for model switching functionality."""
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_switch_to_flash(self, mock_langchain, mock_api_key):
        """Test switching to Flash model."""
        service = GeminiService(
            model=GeminiConfig.GEMINI_PRO_MODEL,
            api_key=mock_api_key
        )
        
        service.switch_to_flash()
        
        assert service.get_current_model() == GeminiConfig.GEMINI_FLASH_MODEL
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_switch_to_pro(self, mock_langchain, mock_api_key):
        """Test switching to Pro model."""
        service = GeminiService(
            model=GeminiConfig.GEMINI_FLASH_MODEL,
            api_key=mock_api_key
        )
        
        service.switch_to_pro()
        
        assert service.get_current_model() == GeminiConfig.GEMINI_PRO_MODEL
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_change_model_invalid(self, mock_langchain, mock_api_key):
        """Test changing to invalid model."""
        service = GeminiService(api_key=mock_api_key)
        
        with pytest.raises(GeminiServiceError):
            service.change_model("invalid-model")


class TestFlashAndProServices:
    """Tests for Flash and Pro specific services."""
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_flash_service_initialization(self, mock_langchain, mock_api_key):
        """Test Flash service initializes with correct model."""
        service = GeminiFlashService(api_key=mock_api_key)
        
        assert service.get_current_model() == GeminiConfig.GEMINI_FLASH_MODEL
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_pro_service_initialization(self, mock_langchain, mock_api_key):
        """Test Pro service initializes with correct model."""
        service = GeminiProService(api_key=mock_api_key)
        
        assert service.get_current_model() == GeminiConfig.GEMINI_PRO_MODEL


class TestBatchGeneration:
    """Tests for batch generation."""
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_batch_generate_multiple_prompts(self, mock_langchain, mock_api_key):
        """Test batch generation with multiple prompts."""
        responses = ["Response 1", "Response 2", "Response 3"]
        
        mock_response_obj = MagicMock()
        mock_langchain.return_value.invoke.side_effect = [
            MagicMock(content=resp) for resp in responses
        ]
        
        service = GeminiService(api_key=mock_api_key)
        service._client = mock_langchain.return_value
        
        prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
        results = service.batch_generate(prompts)
        
        assert len(results) == 3


class TestGetModelInfo:
    """Tests for model information retrieval."""
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_get_model_info_flash(self, mock_langchain, mock_api_key):
        """Test getting model info for Flash."""
        service = GeminiFlashService(api_key=mock_api_key)
        info = service.get_model_info()
        
        assert info["is_flash"] is True
        assert info["is_pro"] is False
        assert info["model"] == GeminiConfig.GEMINI_FLASH_MODEL
    
    @patch("app.services.gemini_service.ChatGoogleGenerativeAI")
    def test_get_model_info_pro(self, mock_langchain, mock_api_key):
        """Test getting model info for Pro."""
        service = GeminiProService(api_key=mock_api_key)
        info = service.get_model_info()
        
        assert info["is_flash"] is False
        assert info["is_pro"] is True
        assert info["model"] == GeminiConfig.GEMINI_PRO_MODEL
