"""
Project Repository

Repository for managing project documents in MongoDB.
"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from app.repositories.base_repository import BaseRepository
from app.schemas.mongodb_schemas import ProjectInDB, ProjectCreate, ProjectUpdate
from app.config.mongodb_config import get_mongodb_config
from app.exceptions.mongodb_exceptions import DocumentNotFoundError

logger = logging.getLogger(__name__)


class ProjectRepository(BaseRepository[ProjectInDB]):
    """Repository for project collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize ProjectRepository.
        
        Args:
            database: MongoDB database instance
        """
        config = get_mongodb_config()
        collection = database[config.MONGODB_PROJECTS_COLLECTION]
        super().__init__(collection, config.MONGODB_PROJECTS_COLLECTION)
    
    async def create_project(self, user_id: str, project_data: ProjectCreate) -> str:
        """
        Create a new project.
        
        Args:
            user_id: ID of the user creating the project
            project_data: Project creation data
            
        Returns:
            ID of created project
        """
        data = project_data.model_dump()
        data["user_id"] = user_id
        data["design_count"] = 0
        
        project_id = await self.create(data)
        logger.info(f"Created project: {project_data.name} for user: {user_id}")
        return project_id
    
    async def update_project(self, project_id: str, project_update: ProjectUpdate) -> bool:
        """
        Update project information.
        
        Args:
            project_id: Project ID
            project_update: Update data
            
        Returns:
            True if updated successfully
            
        Raises:
            DocumentNotFoundError: If project not found
        """
        update_data = project_update.model_dump(exclude_unset=True)
        
        if not update_data:
            return False
        
        updated = await self.update_by_id(project_id, update_data)
        if not updated:
            raise DocumentNotFoundError(self.collection_name, project_id)
        
        return True
    
    async def find_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find all projects for a specific user.
        
        Args:
            user_id: User ID
            skip: Number of documents to skip
            limit: Maximum number of documents
            status: Optional status filter
            
        Returns:
            List of projects
        """
        filter_query = {"user_id": user_id}
        if status:
            filter_query["status"] = status
        
        return await self.find_many(
            filter_query,
            skip=skip,
            limit=limit,
            sort=[("updated_at", -1)]
        )
    
    async def increment_design_count(self, project_id: str) -> bool:
        """
        Increment the design count for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if incremented successfully
        """
        try:
            object_id = self._validate_object_id(project_id)
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$inc": {"design_count": 1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error incrementing design count: {e}")
            return False
    
    async def decrement_design_count(self, project_id: str) -> bool:
        """
        Decrement the design count for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if decremented successfully
        """
        try:
            object_id = self._validate_object_id(project_id)
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$inc": {"design_count": -1}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error decrementing design count: {e}")
            return False
    
    async def archive_project(self, project_id: str) -> bool:
        """
        Archive a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if archived successfully
        """
        return await self.update_by_id(project_id, {"status": "archived"})
    
    async def get_active_projects(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all active projects for a user.
        
        Args:
            user_id: User ID
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of active projects
        """
        return await self.find_by_user(user_id, skip, limit, status="active")
    
    async def search_projects(
        self,
        user_id: str,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search projects by name or description.
        
        Args:
            user_id: User ID
            search_term: Search term
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of matching projects
        """
        filter_query = {
            "user_id": user_id,
            "$or": [
                {"name": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}}
            ]
        }
        
        return await self.find_many(
            filter_query,
            skip=skip,
            limit=limit,
            sort=[("updated_at", -1)]
        )
    
    async def get_projects_by_tag(
        self,
        user_id: str,
        tag: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get projects by tag.
        
        Args:
            user_id: User ID
            tag: Tag to filter by
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of projects with the specified tag
        """
        filter_query = {
            "user_id": user_id,
            "tags": tag
        }
        
        return await self.find_many(
            filter_query,
            skip=skip,
            limit=limit,
            sort=[("updated_at", -1)]
        )
