"""
Design Engine API Endpoints

REST API endpoints for the AI Design Engine.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from app.services.design_engine_service import DesignEngineService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.schemas.design_schemas import (
    InitialDesignRequest,
    InitialDesignResponse,
    TechSuggestionRequest,
    TechSuggestionResponse,
    DecompositionRequest,
    DecompositionResponse,
    APISuggestionRequest,
    APISuggestionResponse,
    RefactorRequest,
    RefactorResponse,
    EngineInfoResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/design", tags=["Design Engine"])


# Dependency to get services
async def get_kb_service() -> KnowledgeBaseService:
    """Get knowledge base service instance."""
    # This will be properly initialized with actual DB connections
    # For now, return None to allow the engine to work without RAG if needed
    try:
        from app.services.knowledge_base_service import KnowledgeBaseService
        # Initialize with actual service - this would come from dependency injection
        return None  # TODO: Initialize properly with DB connections
    except Exception as e:
        logger.warning(f"Could not initialize KB service: {e}")
        return None


async def get_design_engine(
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
) -> DesignEngineService:
    """Get design engine service instance."""
    return DesignEngineService(
        kb_service=kb_service,
        use_rag=kb_service is not None,
    )


@router.post(
    "/generate-initial",
    response_model=Dict[str, Any],
    summary="Generate Initial Design",
    description="Generate initial system architecture from user requirements"
)
async def generate_initial_design(
    request: InitialDesignRequest,
    engine: DesignEngineService = Depends(get_design_engine),
) -> Dict[str, Any]:
    """
    Generate initial system design from requirements.
    
    Creates:
    - SystemContext: Overall system definition
    - Containers: High-level containers
    - Design rationale: Explanation of decisions
    """
    try:
        logger.info("Received request for initial design generation")
        result = await engine.generate_initial_design(request.requirements)
        logger.info("Initial design generated successfully")
        return result
    except Exception as e:
        logger.error(f"Error generating initial design: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/suggest-technology",
    response_model=Dict[str, Any],
    summary="Suggest Technology",
    description="Suggest technology stack for an architecture element"
)
async def suggest_technology(
    request: TechSuggestionRequest,
    engine: DesignEngineService = Depends(get_design_engine),
) -> Dict[str, Any]:
    """
    Suggest technology stack for an element.
    
    Provides:
    - Primary recommendation with rationale
    - Alternative options
    - Implementation guidance
    - Integration considerations
    """
    try:
        logger.info(f"Suggesting technology for {request.element_name}")
        result = await engine.suggest_technology(
            element_name=request.element_name,
            element_type=request.element_type,
            element_description=request.element_description,
            element_context=request.element_context,
        )
        logger.info("Technology suggestion completed")
        return result
    except Exception as e:
        logger.error(f"Error suggesting technology: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/decompose-container",
    response_model=Dict[str, Any],
    summary="Decompose Container",
    description="Decompose a container into detailed components"
)
async def decompose_container(
    request: DecompositionRequest,
    engine: DesignEngineService = Depends(get_design_engine),
) -> Dict[str, Any]:
    """
    Decompose container into components.
    
    Provides:
    - Component definitions
    - Component layers
    - Internal flows
    - Design patterns
    """
    try:
        logger.info(f"Decomposing container {request.container_name}")
        result = await engine.suggest_sub_components(
            container_name=request.container_name,
            container_type=request.container_type,
            container_description=request.container_description,
            container_context=request.container_context,
        )
        logger.info("Container decomposition completed")
        return result
    except Exception as e:
        logger.error(f"Error decomposing container: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/suggest-api",
    response_model=Dict[str, Any],
    summary="Suggest API Endpoints",
    description="Suggest API endpoints for a component"
)
async def suggest_api_endpoints(
    request: APISuggestionRequest,
    engine: DesignEngineService = Depends(get_design_engine),
) -> Dict[str, Any]:
    """
    Suggest API endpoints for a component.
    
    Provides:
    - Endpoint definitions
    - Request/response schemas
    - Authentication schemes
    - Error handling
    - Rate limiting
    """
    try:
        logger.info(f"Suggesting API endpoints for {request.component_name}")
        result = await engine.suggest_api_endpoints(
            component_name=request.component_name,
            component_type=request.component_type,
            component_description=request.component_description,
            component_responsibilities=request.component_responsibilities,
            component_context=request.component_context,
        )
        logger.info("API suggestion completed")
        return result
    except Exception as e:
        logger.error(f"Error suggesting API endpoints: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/refactor",
    response_model=Dict[str, Any],
    summary="Refactor Element",
    description="Refactor an architecture element based on user request"
)
async def refactor_element(
    request: RefactorRequest,
    engine: DesignEngineService = Depends(get_design_engine),
) -> Dict[str, Any]:
    """
    Refactor an architecture element.
    
    Provides:
    - Refactored design
    - Rationale for changes
    - Migration strategy
    - Impact analysis
    - Alternatives considered
    """
    try:
        logger.info(f"Refactoring element {request.element_name}")
        result = await engine.refactor_element(
            element_name=request.element_name,
            element_type=request.element_type,
            element_description=request.element_description,
            current_design=request.current_design,
            refactor_request=request.refactor_request,
            element_context=request.element_context,
        )
        logger.info("Refactoring completed")
        return result
    except Exception as e:
        logger.error(f"Error refactoring element: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/info",
    response_model=EngineInfoResponse,
    summary="Get Engine Info",
    description="Get information about the Design Engine and available chains"
)
async def get_engine_info(
    engine: DesignEngineService = Depends(get_design_engine),
) -> EngineInfoResponse:
    """
    Get information about the Design Engine.
    
    Returns:
    - Engine version
    - RAG status
    - Model information
    - Available chains and their purposes
    """
    try:
        info = engine.get_chain_info()
        return EngineInfoResponse(**info)
    except Exception as e:
        logger.error(f"Error getting engine info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
