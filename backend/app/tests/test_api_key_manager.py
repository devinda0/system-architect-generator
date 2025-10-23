"""
Test suite for API Key Manager

Tests for API key management and security.
"""

import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from app.utils.api_key_manager import (
    APIKeyManager,
    GoogleAPIKeyManager,
)


class TestAPIKeyManager:
    """Tests for APIKeyManager."""
    
    def test_register_key_success(self):
        """Test successful key registration."""
        APIKeyManager._keys.clear()
        
        result = APIKeyManager.register_key(
            key_id="test_key",
            key_value="AIzaSyValidTestKeyForTestingPurposesOnly123456",
            provider="google",
        )
        
        assert result is True
        assert "test_key" in APIKeyManager._keys
    
    def test_register_key_invalid_format(self):
        """Test key registration with invalid format."""
        APIKeyManager._keys.clear()
        
        with pytest.raises(ValueError):
            APIKeyManager.register_key(
                key_id="test_key",
                key_value="invalid",
                provider="google",
            )
    
    def test_get_key(self):
        """Test retrieving a registered key."""
        APIKeyManager._keys.clear()
        test_key = "AIzaSyValidTestKeyForTestingPurposesOnly123456"
        
        APIKeyManager.register_key("test_key", test_key, "google")
        retrieved_key = APIKeyManager.get_key("test_key")
        
        assert retrieved_key == test_key
    
    def test_get_key_not_found(self):
        """Test getting non-existent key."""
        APIKeyManager._keys.clear()
        
        with pytest.raises(KeyError):
            APIKeyManager.get_key("nonexistent")
    
    def test_rotate_key(self):
        """Test key rotation."""
        APIKeyManager._keys.clear()
        old_key = "AIzaSyValidTestKeyForTestingPurposesOnly123456"
        new_key = "AIzaSyNewValidKeyForTestingPurposesOnly1234567"
        
        APIKeyManager.register_key("test_key", old_key, "google")
        result = APIKeyManager.rotate_key("test_key", new_key)
        
        assert result is True
        assert APIKeyManager.get_key("test_key") == new_key
    
    def test_rotate_key_invalid(self):
        """Test rotating with invalid new key."""
        APIKeyManager._keys.clear()
        old_key = "AIzaSyValidTestKeyForTestingPurposesOnly123456"
        
        APIKeyManager.register_key("test_key", old_key, "google")
        
        with pytest.raises(ValueError):
            APIKeyManager.rotate_key("test_key", "invalid")
    
    def test_revoke_key(self):
        """Test key revocation."""
        APIKeyManager._keys.clear()
        test_key = "AIzaSyValidTestKeyForTestingPurposesOnly123456"
        
        APIKeyManager.register_key("test_key", test_key, "google")
        result = APIKeyManager.revoke_key("test_key")
        
        assert result is True
        assert APIKeyManager.is_key_valid("test_key") is False
    
    def test_is_key_valid(self):
        """Test key validity check."""
        APIKeyManager._keys.clear()
        test_key = "AIzaSyValidTestKeyForTestingPurposesOnly123456"
        
        APIKeyManager.register_key("test_key", test_key, "google")
        assert APIKeyManager.is_key_valid("test_key") is True
        
        APIKeyManager.revoke_key("test_key")
        assert APIKeyManager.is_key_valid("test_key") is False
    
    def test_get_access_log(self):
        """Test access log retrieval."""
        APIKeyManager._access_log.clear()
        APIKeyManager._keys.clear()
        test_key = "AIzaSyValidTestKeyForTestingPurposesOnly123456"
        
        APIKeyManager.register_key("test_key", test_key, "google")
        APIKeyManager.get_key("test_key")
        
        log = APIKeyManager.get_access_log()
        assert len(log) > 0
    
    def test_get_access_log_filtered(self):
        """Test filtered access log retrieval."""
        APIKeyManager._access_log.clear()
        APIKeyManager._keys.clear()
        test_key = "AIzaSyValidTestKeyForTestingPurposesOnly123456"
        
        APIKeyManager.register_key("key1", test_key, "google")
        APIKeyManager.register_key("key2", test_key, "google")
        
        APIKeyManager.get_key("key1")
        APIKeyManager.get_key("key1")
        APIKeyManager.get_key("key2")
        
        log_key1 = APIKeyManager.get_access_log("key1")
        log_key2 = APIKeyManager.get_access_log("key2")
        
        assert len(log_key1) == 2
        assert len(log_key2) == 1
    
    def test_clear_old_logs(self):
        """Test clearing old access logs."""
        APIKeyManager._access_log.clear()
        APIKeyManager._keys.clear()
        
        # Add old log entries
        old_time = datetime.now() - timedelta(days=40)
        APIKeyManager._access_log.append({
            "key_id": "test_key",
            "timestamp": old_time,
            "action": "retrieve",
        })
        
        # Add recent log entries
        APIKeyManager._access_log.append({
            "key_id": "test_key",
            "timestamp": datetime.now(),
            "action": "retrieve",
        })
        
        cleared = APIKeyManager.clear_old_logs(days_to_keep=30)
        
        assert cleared == 1
        assert len(APIKeyManager._access_log) == 1
    
    def test_needs_rotation(self):
        """Test rotation necessity check."""
        APIKeyManager._last_rotation = None
        assert APIKeyManager.needs_rotation() is False
        
        APIKeyManager._last_rotation = datetime.now() - timedelta(days=35)
        assert APIKeyManager.needs_rotation() is True


class TestGoogleAPIKeyManager:
    """Tests for GoogleAPIKeyManager."""
    
    def test_init_from_env_success(self):
        """Test initialization from environment."""
        APIKeyManager._keys.clear()
        test_key = "AIzaSyValidTestKeyForTestingPurposesOnly123456"
        
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = test_key
            result = GoogleAPIKeyManager.init_from_env()
        
        assert result is True
    
    def test_init_from_env_no_key(self):
        """Test initialization when no key in environment."""
        APIKeyManager._keys.clear()
        
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = None
            result = GoogleAPIKeyManager.init_from_env()
        
        assert result is False
    
    def test_get_gemini_key(self):
        """Test getting Gemini API key."""
        APIKeyManager._keys.clear()
        test_key = "AIzaSyValidTestKeyForTestingPurposesOnly123456"
        
        APIKeyManager.register_key(
            GoogleAPIKeyManager.KEY_ID,
            test_key,
            GoogleAPIKeyManager.PROVIDER,
        )
        
        retrieved_key = GoogleAPIKeyManager.get_gemini_key()
        assert retrieved_key == test_key
