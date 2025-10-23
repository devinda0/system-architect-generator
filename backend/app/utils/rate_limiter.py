"""
Rate Limiting and Quota Management Module

This module provides rate limiting and quota management for API calls
to prevent exceeding service limits and manage usage across the application.
"""

import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from threading import Lock
from collections import deque
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class QuotaConfig:
    """Configuration for quota management."""
    
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    tokens_per_minute: int = 10000
    tokens_per_day: int = 100000


@dataclass
class QuotaUsage:
    """Track quota usage statistics."""
    
    total_requests: int = 0
    total_tokens: int = 0
    requests_this_minute: int = 0
    requests_this_hour: int = 0
    requests_this_day: int = 0
    tokens_this_minute: int = 0
    tokens_this_day: int = 0
    last_reset_minute: datetime = field(default_factory=datetime.now)
    last_reset_hour: datetime = field(default_factory=datetime.now)
    last_reset_day: datetime = field(default_factory=datetime.now)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: float):
        """
        Initialize rate limit exception.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        super().__init__(message)
        self.retry_after = retry_after


class QuotaExceeded(Exception):
    """Exception raised when quota is exceeded."""
    
    def __init__(self, message: str, quota_type: str):
        """
        Initialize quota exceeded exception.
        
        Args:
            message: Error message
            quota_type: Type of quota exceeded (minute/hour/day)
        """
        super().__init__(message)
        self.quota_type = quota_type


class RateLimiter:
    """
    Token bucket rate limiter implementation.
    
    Features:
    - Token bucket algorithm
    - Configurable rates and burst sizes
    - Thread-safe operations
    - Request tracking
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: Optional[int] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size (defaults to requests_per_minute)
        """
        self.rate = requests_per_minute / 60.0  # Requests per second
        self.burst_size = burst_size or requests_per_minute
        self.tokens = float(self.burst_size)
        self.last_update = time.time()
        self.lock = Lock()
        
        # Track request times
        self.request_times: deque = deque(maxlen=requests_per_minute)
        
        logger.info(
            f"Rate limiter initialized: {requests_per_minute} req/min, "
            f"burst: {self.burst_size}"
        )
    
    def acquire(self, tokens: int = 1, blocking: bool = True) -> bool:
        """
        Acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire
            blocking: Whether to block until tokens are available
            
        Returns:
            bool: True if tokens acquired, False otherwise
            
        Raises:
            RateLimitExceeded: If rate limit exceeded and blocking=False
        """
        with self.lock:
            current_time = time.time()
            
            # Add tokens based on elapsed time
            elapsed = current_time - self.last_update
            self.tokens = min(
                self.burst_size,
                self.tokens + elapsed * self.rate
            )
            self.last_update = current_time
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.request_times.append(current_time)
                logger.debug(f"Tokens acquired: {tokens}, remaining: {self.tokens:.2f}")
                return True
            
            # Not enough tokens
            if not blocking:
                wait_time = (tokens - self.tokens) / self.rate
                logger.warning(f"Rate limit exceeded, retry after {wait_time:.2f}s")
                raise RateLimitExceeded(
                    f"Rate limit exceeded. Please retry after {wait_time:.2f} seconds.",
                    retry_after=wait_time
                )
            
            # Block until tokens are available
            wait_time = (tokens - self.tokens) / self.rate
            logger.info(f"Rate limit reached, waiting {wait_time:.2f}s")
            time.sleep(wait_time)
            return self.acquire(tokens, blocking=False)
    
    def get_current_rate(self) -> float:
        """
        Get current request rate (requests per minute).
        
        Returns:
            Current request rate
        """
        with self.lock:
            current_time = time.time()
            # Count requests in the last minute
            cutoff = current_time - 60
            recent_requests = sum(1 for t in self.request_times if t > cutoff)
            return recent_requests
    
    def reset(self) -> None:
        """Reset the rate limiter."""
        with self.lock:
            self.tokens = float(self.burst_size)
            self.last_update = time.time()
            self.request_times.clear()
            logger.info("Rate limiter reset")


class QuotaManager:
    """
    Manage API usage quotas.
    
    Features:
    - Track requests and tokens
    - Per-minute, per-hour, and per-day limits
    - Automatic quota resets
    - Usage statistics
    """
    
    def __init__(self, config: Optional[QuotaConfig] = None):
        """
        Initialize quota manager.
        
        Args:
            config: Quota configuration
        """
        self.config = config or QuotaConfig()
        self.usage = QuotaUsage()
        self.lock = Lock()
        
        logger.info(
            f"Quota manager initialized: "
            f"{self.config.requests_per_minute} req/min, "
            f"{self.config.requests_per_hour} req/hour, "
            f"{self.config.requests_per_day} req/day"
        )
    
    def check_and_increment(
        self,
        tokens: int = 0,
        cost: int = 1
    ) -> None:
        """
        Check quota availability and increment usage.
        
        Args:
            tokens: Number of tokens to consume
            cost: Request cost (default: 1)
            
        Raises:
            QuotaExceeded: If quota exceeded
        """
        with self.lock:
            self._reset_if_needed()
            
            # Check minute quota
            if (self.usage.requests_this_minute + cost) > self.config.requests_per_minute:
                logger.warning("Per-minute quota exceeded")
                raise QuotaExceeded(
                    f"Per-minute quota exceeded: {self.config.requests_per_minute} requests/minute",
                    quota_type="minute"
                )
            
            # Check hour quota
            if (self.usage.requests_this_hour + cost) > self.config.requests_per_hour:
                logger.warning("Per-hour quota exceeded")
                raise QuotaExceeded(
                    f"Per-hour quota exceeded: {self.config.requests_per_hour} requests/hour",
                    quota_type="hour"
                )
            
            # Check day quota
            if (self.usage.requests_this_day + cost) > self.config.requests_per_day:
                logger.warning("Per-day quota exceeded")
                raise QuotaExceeded(
                    f"Per-day quota exceeded: {self.config.requests_per_day} requests/day",
                    quota_type="day"
                )
            
            # Check token quotas if applicable
            if tokens > 0:
                if (self.usage.tokens_this_minute + tokens) > self.config.tokens_per_minute:
                    logger.warning("Per-minute token quota exceeded")
                    raise QuotaExceeded(
                        f"Token quota exceeded: {self.config.tokens_per_minute} tokens/minute",
                        quota_type="minute_tokens"
                    )
                
                if (self.usage.tokens_this_day + tokens) > self.config.tokens_per_day:
                    logger.warning("Per-day token quota exceeded")
                    raise QuotaExceeded(
                        f"Token quota exceeded: {self.config.tokens_per_day} tokens/day",
                        quota_type="day_tokens"
                    )
            
            # Increment usage
            self.usage.total_requests += cost
            self.usage.total_tokens += tokens
            self.usage.requests_this_minute += cost
            self.usage.requests_this_hour += cost
            self.usage.requests_this_day += cost
            self.usage.tokens_this_minute += tokens
            self.usage.tokens_this_day += tokens
            
            logger.debug(
                f"Quota updated: {self.usage.requests_this_minute}/{self.config.requests_per_minute} req/min, "
                f"{self.usage.tokens_this_minute}/{self.config.tokens_per_minute} tokens/min"
            )
    
    def _reset_if_needed(self) -> None:
        """Reset quotas if time windows have passed."""
        now = datetime.now()
        
        # Reset minute quota
        if (now - self.usage.last_reset_minute).total_seconds() >= 60:
            self.usage.requests_this_minute = 0
            self.usage.tokens_this_minute = 0
            self.usage.last_reset_minute = now
            logger.debug("Per-minute quota reset")
        
        # Reset hour quota
        if (now - self.usage.last_reset_hour).total_seconds() >= 3600:
            self.usage.requests_this_hour = 0
            self.usage.last_reset_hour = now
            logger.debug("Per-hour quota reset")
        
        # Reset day quota
        if (now - self.usage.last_reset_day).total_seconds() >= 86400:
            self.usage.requests_this_day = 0
            self.usage.tokens_this_day = 0
            self.usage.last_reset_day = now
            logger.debug("Per-day quota reset")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get current usage statistics.
        
        Returns:
            Dictionary with usage stats
        """
        with self.lock:
            self._reset_if_needed()
            
            return {
                "total_requests": self.usage.total_requests,
                "total_tokens": self.usage.total_tokens,
                "current_minute": {
                    "requests": self.usage.requests_this_minute,
                    "limit": self.config.requests_per_minute,
                    "remaining": self.config.requests_per_minute - self.usage.requests_this_minute,
                    "tokens": self.usage.tokens_this_minute,
                    "token_limit": self.config.tokens_per_minute,
                },
                "current_hour": {
                    "requests": self.usage.requests_this_hour,
                    "limit": self.config.requests_per_hour,
                    "remaining": self.config.requests_per_hour - self.usage.requests_this_hour,
                },
                "current_day": {
                    "requests": self.usage.requests_this_day,
                    "limit": self.config.requests_per_day,
                    "remaining": self.config.requests_per_day - self.usage.requests_this_day,
                    "tokens": self.usage.tokens_this_day,
                    "token_limit": self.config.tokens_per_day,
                },
            }
    
    def reset(self) -> None:
        """Reset all quota counters."""
        with self.lock:
            self.usage = QuotaUsage()
            logger.info("Quota manager reset")


# Global instances
_rate_limiter: Optional[RateLimiter] = None
_quota_manager: Optional[QuotaManager] = None


def get_rate_limiter(requests_per_minute: int = 60) -> RateLimiter:
    """
    Get or create global rate limiter instance.
    
    Args:
        requests_per_minute: Maximum requests per minute
        
    Returns:
        RateLimiter instance
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(requests_per_minute=requests_per_minute)
    return _rate_limiter


def get_quota_manager(config: Optional[QuotaConfig] = None) -> QuotaManager:
    """
    Get or create global quota manager instance.
    
    Args:
        config: Quota configuration
        
    Returns:
        QuotaManager instance
    """
    global _quota_manager
    if _quota_manager is None:
        _quota_manager = QuotaManager(config=config)
    return _quota_manager
