"""
Exception classes for the application.
"""

from app.exceptions.gemini_exceptions import (
    GeminiError,
    GeminiConfigError,
    GeminiAPIError,
    GeminiRateLimitError,
    GeminiTimeoutError,
    GeminiAuthenticationError,
    GeminiInvalidRequestError,
)

__all__ = [
    "GeminiError",
    "GeminiConfigError",
    "GeminiAPIError",
    "GeminiRateLimitError",
    "GeminiTimeoutError",
    "GeminiAuthenticationError",
    "GeminiInvalidRequestError",
]
