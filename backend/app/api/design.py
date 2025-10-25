"""
Design Engine API Endpoints

REST API endpoints for the AI Design Engine.
"""

from fastapi import APIRouter, HTTPException, Depends, status
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
from app.schemas.ai_action import (
    AIActionRequest,
    AIActionResponse,
    ElementUpdateRequest,
    ElementUpdateResponse,
    DesignTreeResponse,
)
from app.repositories.design_repository import DesignRepository
from app.config.mongodb_config import get_database
from app.middleware.auth import CurrentUserDep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/designs", tags=["Design Engine"])


# Dependency to get services
async def get_design_repository() -> DesignRepository:
    """Get design repository instance."""
    database = await get_database()
    return DesignRepository(database)


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


@router.get(
    "/{design_id}",
    response_model=DesignTreeResponse,
    summary="Get Design Tree",
    description="Get complete design tree structure with all elements and relationships"
)
async def get_design_tree(
    design_id: str,
    current_user: CurrentUserDep,
    repo: DesignRepository = Depends(get_design_repository),
) -> DesignTreeResponse:
    """
    Get design tree structure.
    
    Args:
        design_id: Design ID
        current_user: Authenticated user
        repo: Design repository
        
    Returns:
        Complete design tree with elements and relationships
        
    Raises:
        HTTPException: If design not found or access denied
    """
    try:
        design = await repo.find_by_id(design_id)
        
        if not design:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Design not found"
            )
        
        # Check if user has access to this design
        if design["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this design"
            )
        
        return DesignTreeResponse(
            design_id=design["_id"],
            project_id=design["project_id"],
            title=design["title"],
            description=design.get("description"),
            diagram_type=design["diagram_type"],
            version=design.get("version", 1),
            elements=design.get("elements", []),
            relationships=design.get("relationships", []),
            metadata=design.get("metadata", {}),
            created_at=design["created_at"].isoformat(),
            updated_at=design["updated_at"].isoformat(),
            created_by_ai=design.get("created_by_ai", False),
            ai_model=design.get("ai_model"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting design tree {design_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve design: {str(e)}"
        )


@router.post(
    "/{design_id}/ai-action",
    response_model=AIActionResponse,
    summary="Invoke AI Action",
    description="Invoke an AI design action on a design"
)
async def invoke_ai_action(
    design_id: str,
    request: AIActionRequest,
    current_user: CurrentUserDep,
    design_repo: DesignRepository = Depends(get_design_repository),
    engine: DesignEngineService = Depends(get_design_engine),
) -> AIActionResponse:
    """
    Invoke AI action on a design.
    
    Args:
        design_id: Design ID
        request: AI action request
        current_user: Authenticated user
        design_repo: Design repository
        engine: Design engine service
        
    Returns:
        AI action result
        
    Raises:
        HTTPException: If design not found, access denied, or action fails
    """
    try:
        # Verify design exists and user has access
        design = await design_repo.find_by_id(design_id)
        
        if not design:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Design not found"
            )
        
        if design["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this design"
            )
        
        # Execute AI action based on type
        result = None
        
        if request.action_type == "initial_generation":
            result = await engine.generate_initial_design(request.requirements)
        
        elif request.action_type == "tech_suggestion":
            result = await engine.suggest_technology(
                element_name=request.element_name,
                element_type=request.element_type,
                element_description=request.element_description,
                element_context=request.context,
            )
        
        elif request.action_type == "decomposition":
            result = await engine.suggest_sub_components(
                container_name=request.container_name,
                container_type=request.element_type,
                container_description=request.container_description,
                container_context=request.context,
            )
        
        elif request.action_type == "api_suggestion":
            result = await engine.suggest_api_endpoints(
                component_name=request.source_component_name,
                component_type=request.element_type,
                component_description=request.interaction_purpose,
                component_responsibilities=[],
                component_context=request.context,
            )
        
        elif request.action_type == "refactor":
            result = await engine.refactor_element(
                element_name=request.element_name,
                element_type=request.element_type,
                element_description=request.element_description,
                current_design=request.current_design or {},
                refactor_request=" ".join(request.refactor_goals or []),
                element_context=request.context,
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown action type: {request.action_type}"
            )
        
        return AIActionResponse(
            action_type=request.action_type,
            success=True,
            result=result,
            metadata={
                "design_id": design_id,
                "user_id": current_user["id"],
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing AI action on design {design_id}: {e}")
        return AIActionResponse(
            action_type=request.action_type,
            success=False,
            result={},
            error=str(e)
        )


@router.put(
    "/{design_id}/element/{element_id}",
    response_model=ElementUpdateResponse,
    summary="Update Design Element",
    description="Update a specific element in a design"
)
async def update_design_element(
    design_id: str,
    element_id: str,
    request: ElementUpdateRequest,
    current_user: CurrentUserDep,
    repo: DesignRepository = Depends(get_design_repository),
) -> ElementUpdateResponse:
    """
    Update a design element.
    
    Args:
        design_id: Design ID
        element_id: Element ID to update
        request: Element update data
        current_user: Authenticated user
        repo: Design repository
        
    Returns:
        Update result with updated element
        
    Raises:
        HTTPException: If design not found, access denied, or element not found
    """
    try:
        # Verify design exists and user has access
        design = await repo.find_by_id(design_id)
        
        if not design:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Design not found"
            )
        
        if design["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this design"
            )
        
        # Find and update element
        elements = design.get("elements", [])
        element_found = False
        updated_element = None
        
        for element in elements:
            if element.get("id") == element_id:
                element_found = True
                
                # Update fields
                if request.name is not None:
                    element["name"] = request.name
                if request.description is not None:
                    element["description"] = request.description
                if request.technology is not None:
                    element["technology"] = request.technology
                if request.tags is not None:
                    element["tags"] = request.tags
                if request.properties is not None:
                    element["properties"] = request.properties
                
                updated_element = element
                break
        
        if not element_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Element {element_id} not found in design"
            )
        
        # Update design with modified elements
        from app.schemas.mongodb_schemas import DesignUpdate
        update_data = DesignUpdate(elements=elements)
        await repo.update_design(design_id, update_data)
        
        logger.info(f"Element {element_id} updated in design {design_id}")
        
        return ElementUpdateResponse(
            success=True,
            element_id=element_id,
            message="Element updated successfully",
            updated_element=updated_element
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating element {element_id} in design {design_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update element: {str(e)}"
        )

