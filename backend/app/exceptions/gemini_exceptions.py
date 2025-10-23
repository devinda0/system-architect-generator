"""
Exception classes for Google Gemini API integration.
"""


class GeminiError(Exception):
    """Base exception for all Gemini-related errors."""
    
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class GeminiConfigError(GeminiError):
    """Exception raised for configuration errors."""
    pass


class GeminiAPIError(GeminiError):
    """Exception raised for API-related errors."""
    
    def __init__(self, message: str, status_code: int = None, original_error: Exception = None):
        self.status_code = status_code
        super().__init__(message, original_error)


class GeminiRateLimitError(GeminiAPIError):
    """Exception raised when rate limit is exceeded (429)."""
    
    def __init__(self, message: str = "Rate limit exceeded", original_error: Exception = None):
        super().__init__(message, status_code=429, original_error=original_error)


class GeminiTimeoutError(GeminiAPIError):
    """Exception raised when request times out."""
    
    def __init__(self, message: str = "Request timed out", original_error: Exception = None):
        super().__init__(message, status_code=408, original_error=original_error)


class GeminiAuthenticationError(GeminiAPIError):
    """Exception raised for authentication errors (401, 403)."""
    
    def __init__(self, message: str = "Authentication failed", status_code: int = 401, original_error: Exception = None):
        super().__init__(message, status_code=status_code, original_error=original_error)


class GeminiInvalidRequestError(GeminiAPIError):
    """Exception raised for invalid requests (400)."""
    
    def __init__(self, message: str = "Invalid request", original_error: Exception = None):
        super().__init__(message, status_code=400, original_error=original_error)
