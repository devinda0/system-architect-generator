"""
Project API Endpoints

REST API endpoints for project management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
import logging

from app.schemas.project import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectListResponse,
    ProjectDetailResponse,
)
from app.schemas.mongodb_schemas import ProjectCreate, ProjectUpdate
from app.repositories.project_repository import ProjectRepository
from app.repositories.design_repository import DesignRepository
from app.config.mongodb_config import get_database
from app.middleware.auth import CurrentUserDep
from app.exceptions.mongodb_exceptions import DocumentNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["Projects"])


async def get_project_repository() -> ProjectRepository:
    """Get project repository instance."""
    database = get_database()
    return ProjectRepository(database)


async def get_design_repository() -> DesignRepository:
    """Get design repository instance."""
    database = get_database()
    return DesignRepository(database)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Create a new architecture project for the authenticated user"
)
async def create_project(
    request: ProjectCreateRequest,
    current_user: CurrentUserDep,
    repo: ProjectRepository = Depends(get_project_repository),
) -> ProjectResponse:
    """
    Create a new project.
    
    Args:
        request: Project creation data
        current_user: Authenticated user
        repo: Project repository
        
    Returns:
        Created project details
    """
    try:
        # Convert request to ProjectCreate schema
        project_data = ProjectCreate(
            name=request.name,
            description=request.description,
            tags=request.tags,
            metadata=request.metadata,
        )
        
        # Create project
        project_id = await repo.create_project(current_user.id, project_data)
        
        # Fetch created project
        project = await repo.find_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created project"
            )
        
        logger.info(f"Project created: {project_id} by user: {current_user.id}")
        
        return ProjectResponse(
            id=project["_id"],
            user_id=project["user_id"],
            name=project["name"],
            description=project.get("description"),
            tags=project.get("tags", []),
            status=project.get("status", "active"),
            metadata=project.get("metadata", {}),
            design_count=project.get("design_count", 0),
            created_at=project["created_at"],
            updated_at=project["updated_at"],
        )
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Get project details",
    description="Get detailed information about a specific project"
)
async def get_project(
    project_id: str,
    current_user: CurrentUserDep,
    project_repo: ProjectRepository = Depends(get_project_repository),
    design_repo: DesignRepository = Depends(get_design_repository),
) -> ProjectDetailResponse:
    """
    Get project details.
    
    Args:
        project_id: Project ID
        current_user: Authenticated user
        project_repo: Project repository
        design_repo: Design repository
        
    Returns:
        Project details including recent designs
        
    Raises:
        HTTPException: If project not found or access denied
    """
    try:
        project = await project_repo.find_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check if user has access to this project
        if project["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this project"
            )
        
        # Get recent designs for this project
        recent_designs = await design_repo.find_by_project(
            project_id=project_id,
            skip=0,
            limit=5
        )
        
        return ProjectDetailResponse(
            id=project["_id"],
            user_id=project["user_id"],
            name=project["name"],
            description=project.get("description"),
            tags=project.get("tags", []),
            status=project.get("status", "active"),
            metadata=project.get("metadata", {}),
            design_count=project.get("design_count", 0),
            created_at=project["created_at"],
            updated_at=project["updated_at"],
            recent_designs=recent_designs,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve project: {str(e)}"
        )


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List user projects",
    description="Get a list of all projects for the authenticated user"
)
async def list_projects(
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    repo: ProjectRepository = Depends(get_project_repository),
) -> ProjectListResponse:
    """
    List projects for the current user.
    
    Args:
        current_user: Authenticated user
        skip: Number of projects to skip
        limit: Maximum number of projects to return
        status_filter: Optional status filter (active, archived, deleted)
        repo: Project repository
        
    Returns:
        List of projects with pagination info
    """
    try:
        projects = await repo.find_by_user(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            status=status_filter,
        )
        
        total = await repo.count_by_user(current_user.id, status=status_filter)
        
        project_responses = [
            ProjectResponse(
                id=p["_id"],
                user_id=p["user_id"],
                name=p["name"],
                description=p.get("description"),
                tags=p.get("tags", []),
                status=p.get("status", "active"),
                metadata=p.get("metadata", {}),
                design_count=p.get("design_count", 0),
                created_at=p["created_at"],
                updated_at=p["updated_at"],
            )
            for p in projects
        ]
        
        return ProjectListResponse(
            projects=project_responses,
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        logger.error(f"Error listing projects for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Update project information"
)
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    current_user: CurrentUserDep,
    repo: ProjectRepository = Depends(get_project_repository),
) -> ProjectResponse:
    """
    Update a project.
    
    Args:
        project_id: Project ID
        request: Project update data
        current_user: Authenticated user
        repo: Project repository
        
    Returns:
        Updated project details
        
    Raises:
        HTTPException: If project not found or access denied
    """
    try:
        # Check if project exists and user has access
        project = await repo.find_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this project"
            )
        
        # Convert request to ProjectUpdate schema
        update_data = ProjectUpdate(
            name=request.name,
            description=request.description,
            tags=request.tags,
            status=request.status,
            metadata=request.metadata,
        )
        
        # Update project
        await repo.update_project(project_id, update_data)
        
        # Fetch updated project
        updated_project = await repo.find_by_id(project_id)
        
        logger.info(f"Project updated: {project_id} by user: {current_user.id}")
        
        return ProjectResponse(
            id=updated_project["_id"],
            user_id=updated_project["user_id"],
            name=updated_project["name"],
            description=updated_project.get("description"),
            tags=updated_project.get("tags", []),
            status=updated_project.get("status", "active"),
            metadata=updated_project.get("metadata", {}),
            design_count=updated_project.get("design_count", 0),
            created_at=updated_project["created_at"],
            updated_at=updated_project["updated_at"],
        )
    except HTTPException:
        raise
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Delete a project (soft delete by setting status to 'deleted')"
)
async def delete_project(
    project_id: str,
    current_user: CurrentUserDep,
    hard_delete: bool = False,
    repo: ProjectRepository = Depends(get_project_repository),
) -> None:
    """
    Delete a project.
    
    By default, performs a soft delete by setting status to 'deleted'.
    If hard_delete=true, permanently removes the project.
    
    Args:
        project_id: Project ID
        current_user: Authenticated user
        hard_delete: Whether to permanently delete (default: False)
        repo: Project repository
        
    Raises:
        HTTPException: If project not found or access denied
    """
    try:
        # Check if project exists and user has access
        project = await repo.find_by_id(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this project"
            )
        
        if hard_delete:
            # Permanently delete
            deleted = await repo.delete_by_id(project_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete project"
                )
            logger.info(f"Project hard deleted: {project_id} by user: {current_user.id}")
        else:
            # Soft delete
            update_data = ProjectUpdate(status="deleted")
            await repo.update_project(project_id, update_data)
            logger.info(f"Project soft deleted: {project_id} by user: {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )
