"""
Gemini API Router

This module provides REST API endpoints for interacting with Google Gemini models.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.gemini_service import (
    get_gemini_service,
    get_gemini_flash_service,
    get_gemini_pro_service,
)
from app.config.gemini_config import get_config
from app.exceptions.gemini_exceptions import (
    GeminiError,
    GeminiConfigError,
    GeminiAPIError,
    GeminiRateLimitError,
    GeminiTimeoutError,
    GeminiAuthenticationError,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/gemini",
    tags=["gemini"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


# Request/Response Models
class GenerateRequest(BaseModel):
    """Request model for text generation."""
    
    prompt: str = Field(..., description="The prompt for text generation", min_length=1)
    system_prompt: Optional[str] = Field(None, description="Optional system prompt for context")
    model: Optional[str] = Field(None, description="Model to use (gemini-pro or gemini-1.5-flash)")
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0, description="Temperature for randomness")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens in response")


class GenerateResponse(BaseModel):
    """Response model for text generation."""
    
    content: str = Field(..., description="Generated text content")
    model: str = Field(..., description="Model used for generation")
    success: bool = Field(True, description="Whether generation was successful")


class BatchGenerateRequest(BaseModel):
    """Request model for batch text generation."""
    
    prompts: List[str] = Field(..., description="List of prompts", min_items=1)
    system_prompt: Optional[str] = Field(None, description="Optional system prompt for all requests")
    model: Optional[str] = Field(None, description="Model to use")


class BatchGenerateResponse(BaseModel):
    """Response model for batch text generation."""
    
    responses: List[str] = Field(..., description="Generated responses")
    model: str = Field(..., description="Model used for generation")
    success: bool = Field(True, description="Whether generation was successful")


class ModelInfo(BaseModel):
    """Model information response."""
    
    model: str
    is_flash: bool
    is_pro: bool
    temperature: float
    max_tokens: int
    request_timeout: int


class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str
    api_key_configured: bool
    config_valid: bool
    message: str


# Exception handler
def handle_gemini_exception(e: Exception) -> HTTPException:
    """Convert Gemini exceptions to HTTP exceptions."""
    if isinstance(e, GeminiRateLimitError):
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "Rate limit exceeded", "message": str(e)}
        )
    elif isinstance(e, GeminiTimeoutError):
        return HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail={"error": "Request timeout", "message": str(e)}
        )
    elif isinstance(e, GeminiAuthenticationError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Authentication failed", "message": str(e)}
        )
    elif isinstance(e, GeminiConfigError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Configuration error", "message": str(e)}
        )
    elif isinstance(e, GeminiAPIError):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "API error", "message": str(e)}
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal error", "message": str(e)}
        )


# Endpoints
@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Check Gemini API health and configuration.
    
    Returns:
        HealthCheckResponse: Health status information
    """
    try:
        config = get_config()
        api_key_configured = config.validate_api_key()
        
        return HealthCheckResponse(
            status="healthy" if api_key_configured else "unhealthy",
            api_key_configured=api_key_configured,
            config_valid=True,
            message="Gemini API is configured and ready" if api_key_configured else "API key not configured"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            api_key_configured=False,
            config_valid=False,
            message=f"Configuration error: {str(e)}"
        )


@router.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """
    Generate text using Google Gemini model.
    
    Args:
        request: GenerateRequest with prompt and parameters
        
    Returns:
        GenerateResponse: Generated text response
        
    Raises:
        HTTPException: If generation fails
    """
    try:
        service = get_gemini_service(
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        content = service.generate(
            prompt=request.prompt,
            system_prompt=request.system_prompt
        )
        
        return GenerateResponse(
            content=content,
            model=service.get_current_model(),
            success=True
        )
    
    except GeminiError as e:
        logger.error(f"Gemini error during generation: {e}")
        raise handle_gemini_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error during generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Generation failed", "message": str(e)}
        )


@router.post("/generate/flash", response_model=GenerateResponse)
async def generate_text_flash(request: GenerateRequest):
    """
    Generate text using Gemini Flash model (faster, optimized).
    
    Args:
        request: GenerateRequest with prompt and parameters
        
    Returns:
        GenerateResponse: Generated text response
    """
    try:
        service = get_gemini_flash_service()
        
        content = service.generate(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return GenerateResponse(
            content=content,
            model=service.get_current_model(),
            success=True
        )
    
    except GeminiError as e:
        logger.error(f"Gemini error during Flash generation: {e}")
        raise handle_gemini_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error during Flash generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Generation failed", "message": str(e)}
        )


@router.post("/generate/pro", response_model=GenerateResponse)
async def generate_text_pro(request: GenerateRequest):
    """
    Generate text using Gemini Pro model (more capable).
    
    Args:
        request: GenerateRequest with prompt and parameters
        
    Returns:
        GenerateResponse: Generated text response
    """
    try:
        service = get_gemini_pro_service()
        
        content = service.generate(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return GenerateResponse(
            content=content,
            model=service.get_current_model(),
            success=True
        )
    
    except GeminiError as e:
        logger.error(f"Gemini error during Pro generation: {e}")
        raise handle_gemini_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error during Pro generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Generation failed", "message": str(e)}
        )


@router.post("/batch", response_model=BatchGenerateResponse)
async def batch_generate(request: BatchGenerateRequest):
    """
    Generate text for multiple prompts in batch.
    
    Args:
        request: BatchGenerateRequest with list of prompts
        
    Returns:
        BatchGenerateResponse: List of generated responses
    """
    try:
        service = get_gemini_service(model=request.model)
        
        responses = service.batch_generate(
            prompts=request.prompts,
            system_prompt=request.system_prompt
        )
        
        return BatchGenerateResponse(
            responses=responses,
            model=service.get_current_model(),
            success=True
        )
    
    except GeminiError as e:
        logger.error(f"Gemini error during batch generation: {e}")
        raise handle_gemini_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error during batch generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Batch generation failed", "message": str(e)}
        )


@router.get("/models/current", response_model=ModelInfo)
async def get_current_model_info():
    """
    Get information about the current active model.
    
    Returns:
        ModelInfo: Current model configuration
    """
    try:
        service = get_gemini_service()
        info = service.get_model_info()
        
        return ModelInfo(**info)
    
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get model info", "message": str(e)}
        )


@router.get("/models/available")
async def get_available_models():
    """
    Get list of available Gemini models.
    
    Returns:
        dict: Available models and their descriptions
    """
    config = get_config()
    
    return {
        "models": [
            {
                "name": config.GEMINI_FLASH_MODEL,
                "type": "flash",
                "description": "Fast and efficient model for most tasks",
                "is_default": config.DEFAULT_MODEL == config.GEMINI_FLASH_MODEL
            },
            {
                "name": config.GEMINI_PRO_MODEL,
                "type": "pro",
                "description": "More capable model for complex tasks",
                "is_default": config.DEFAULT_MODEL == config.GEMINI_PRO_MODEL
            }
        ]
    }
