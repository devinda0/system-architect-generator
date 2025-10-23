"""
API Key Management Module

This module provides secure handling of API keys with validation,
storage, and lifecycle management capabilities.
"""

import os
import logging
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class APIKeyManager:
    """
    Manages API key lifecycle and security.
    
    Features:
    - API key validation
    - Secure storage in environment
    - Key rotation support
    - Access logging
    """
    
    # Store for API keys with metadata
    _keys: dict = {}
    _access_log: list = []
    _last_rotation: Optional[datetime] = None
    _rotation_interval_days: int = 30
    
    @classmethod
    def register_key(
        cls,
        key_id: str,
        key_value: str,
        provider: str = "google",
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Register an API key securely.
        
        Args:
            key_id (str): Unique identifier for the key
            key_value (str): The actual API key
            provider (str): Provider name (e.g., 'google')
            metadata (dict, optional): Additional metadata
            
        Returns:
            bool: True if registered successfully
            
        Raises:
            ValueError: If key validation fails
        """
        if not cls._validate_key_format(key_value):
            raise ValueError(f"Invalid API key format for {provider}")
        
        cls._keys[key_id] = {
            "value": key_value,
            "provider": provider,
            "created_at": datetime.now(),
            "last_used": None,
            "metadata": metadata or {},
        }
        
        logger.info(f"API key '{key_id}' registered for provider '{provider}'")
        return True
    
    @classmethod
    def get_key(cls, key_id: str) -> Optional[str]:
        """
        Retrieve an API key.
        
        Args:
            key_id (str): Unique identifier for the key
            
        Returns:
            str: The API key value
            
        Raises:
            KeyError: If key not found
        """
        if key_id not in cls._keys:
            raise KeyError(f"API key '{key_id}' not found")
        
        key_entry = cls._keys[key_id]
        key_entry["last_used"] = datetime.now()
        
        # Log access
        cls._access_log.append({
            "key_id": key_id,
            "timestamp": datetime.now(),
            "action": "retrieve",
        })
        
        logger.debug(f"API key '{key_id}' accessed")
        return key_entry["value"]
    
    @classmethod
    def rotate_key(cls, key_id: str, new_key_value: str) -> bool:
        """
        Rotate an API key with a new one.
        
        Args:
            key_id (str): Unique identifier for the key
            new_key_value (str): The new API key value
            
        Returns:
            bool: True if rotation successful
            
        Raises:
            KeyError: If key not found
            ValueError: If validation fails
        """
        if key_id not in cls._keys:
            raise KeyError(f"API key '{key_id}' not found")
        
        if not cls._validate_key_format(new_key_value):
            raise ValueError("Invalid new API key format")
        
        old_key_entry = cls._keys[key_id]
        old_key_entry["value"] = new_key_value
        old_key_entry["rotated_at"] = datetime.now()
        
        cls._last_rotation = datetime.now()
        
        logger.info(f"API key '{key_id}' rotated successfully")
        return True
    
    @classmethod
    def revoke_key(cls, key_id: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_id (str): Unique identifier for the key
            
        Returns:
            bool: True if revoked successfully
        """
        if key_id in cls._keys:
            cls._keys[key_id]["revoked"] = True
            cls._keys[key_id]["revoked_at"] = datetime.now()
            logger.warning(f"API key '{key_id}' revoked")
            return True
        return False
    
    @classmethod
    def is_key_valid(cls, key_id: str) -> bool:
        """
        Check if an API key is valid and not revoked.
        
        Args:
            key_id (str): Unique identifier for the key
            
        Returns:
            bool: True if key is valid
        """
        if key_id not in cls._keys:
            return False
        
        key_entry = cls._keys[key_id]
        return not key_entry.get("revoked", False)
    
    @classmethod
    def _validate_key_format(cls, key: str) -> bool:
        """
        Validate API key format.
        
        Args:
            key (str): The API key to validate
            
        Returns:
            bool: True if format is valid
        """
        if not isinstance(key, str) or len(key) < 20:
            return False
        return True
    
    @classmethod
    def needs_rotation(cls) -> bool:
        """
        Check if API key needs rotation.
        
        Returns:
            bool: True if rotation is recommended
        """
        if cls._last_rotation is None:
            return False
        
        days_since_rotation = (datetime.now() - cls._last_rotation).days
        return days_since_rotation >= cls._rotation_interval_days
    
    @classmethod
    def get_access_log(cls, key_id: Optional[str] = None) -> list:
        """
        Get access log for API keys.
        
        Args:
            key_id (str, optional): Filter by specific key ID
            
        Returns:
            list: Access log entries
        """
        if key_id:
            return [log for log in cls._access_log if log["key_id"] == key_id]
        return cls._access_log
    
    @classmethod
    def clear_old_logs(cls, days_to_keep: int = 30) -> int:
        """
        Clear old access logs.
        
        Args:
            days_to_keep (int): Number of days to keep
            
        Returns:
            int: Number of logs cleared
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        original_length = len(cls._access_log)
        cls._access_log = [
            log for log in cls._access_log
            if log["timestamp"] > cutoff_date
        ]
        cleared = original_length - len(cls._access_log)
        logger.info(f"Cleared {cleared} old access logs")
        return cleared


class GoogleAPIKeyManager(APIKeyManager):
    """
    Specialized manager for Google API keys.
    """
    
    KEY_ID = "google_gemini"
    PROVIDER = "google"
    
    @classmethod
    def init_from_env(cls) -> bool:
        """
        Initialize Google API key from environment variable.
        
        Returns:
            bool: True if initialization successful
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not found in environment")
            return False
        
        try:
            cls.register_key(
                key_id=cls.KEY_ID,
                key_value=api_key,
                provider=cls.PROVIDER,
                metadata={"source": "environment"}
            )
            return True
        except ValueError as e:
            logger.error(f"Failed to register Google API key: {e}")
            return False
    
    @classmethod
    def get_gemini_key(cls) -> str:
        """
        Get Google Gemini API key.
        
        Returns:
            str: The API key
            
        Raises:
            KeyError: If key not registered
        """
        return cls.get_key(cls.KEY_ID)
