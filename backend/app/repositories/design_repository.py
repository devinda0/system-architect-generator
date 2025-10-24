"""
Design Repository

Repository for managing design documents in MongoDB.
"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from app.repositories.base_repository import BaseRepository
from app.schemas.mongodb_schemas import DesignInDB, DesignCreate, DesignUpdate
from app.config.mongodb_config import get_mongodb_config
from app.exceptions.mongodb_exceptions import DocumentNotFoundError

logger = logging.getLogger(__name__)


class DesignRepository(BaseRepository[DesignInDB]):
    """Repository for design collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize DesignRepository.
        
        Args:
            database: MongoDB database instance
        """
        config = get_mongodb_config()
        collection = database[config.MONGODB_DESIGNS_COLLECTION]
        super().__init__(collection, config.MONGODB_DESIGNS_COLLECTION)
    
    async def create_design(
        self,
        user_id: str,
        design_data: DesignCreate,
        created_by_ai: bool = False,
        ai_model: Optional[str] = None
    ) -> str:
        """
        Create a new design.
        
        Args:
            user_id: ID of the user creating the design
            design_data: Design creation data
            created_by_ai: Whether the design was created by AI
            ai_model: Name of the AI model if created by AI
            
        Returns:
            ID of created design
        """
        data = design_data.model_dump()
        data["user_id"] = user_id
        data["created_by_ai"] = created_by_ai
        data["ai_model"] = ai_model
        
        design_id = await self.create(data)
        logger.info(f"Created design: {design_data.title} for project: {design_data.project_id}")
        return design_id
    
    async def update_design(self, design_id: str, design_update: DesignUpdate) -> bool:
        """
        Update design information.
        
        Args:
            design_id: Design ID
            design_update: Update data
            
        Returns:
            True if updated successfully
            
        Raises:
            DocumentNotFoundError: If design not found
        """
        update_data = design_update.model_dump(exclude_unset=True)
        
        if not update_data:
            return False
        
        updated = await self.update_by_id(design_id, update_data)
        if not updated:
            raise DocumentNotFoundError(self.collection_name, design_id)
        
        return True
    
    async def find_by_project(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find all designs for a specific project.
        
        Args:
            project_id: Project ID
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of designs
        """
        return await self.find_many(
            {"project_id": project_id},
            skip=skip,
            limit=limit,
            sort=[("version", -1), ("created_at", -1)]
        )
    
    async def find_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find all designs for a specific user.
        
        Args:
            user_id: User ID
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of designs
        """
        return await self.find_many(
            {"user_id": user_id},
            skip=skip,
            limit=limit,
            sort=[("updated_at", -1)]
        )
    
    async def find_latest_version(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Find the latest version of a design for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Latest design document if found
        """
        designs = await self.find_many(
            {"project_id": project_id},
            skip=0,
            limit=1,
            sort=[("version", -1)]
        )
        return designs[0] if designs else None
    
    async def get_version_history(
        self,
        project_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get version history of designs for a project.
        
        Args:
            project_id: Project ID
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of designs ordered by version
        """
        return await self.find_many(
            {"project_id": project_id},
            skip=skip,
            limit=limit,
            sort=[("version", -1)]
        )
    
    async def get_ai_generated_designs(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all AI-generated designs for a user.
        
        Args:
            user_id: User ID
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of AI-generated designs
        """
        return await self.find_many(
            {"user_id": user_id, "created_by_ai": True},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def search_designs(
        self,
        user_id: str,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search designs by title or description.
        
        Args:
            user_id: User ID
            search_term: Search term
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of matching designs
        """
        filter_query = {
            "user_id": user_id,
            "$or": [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}}
            ]
        }
        
        return await self.find_many(
            filter_query,
            skip=skip,
            limit=limit,
            sort=[("updated_at", -1)]
        )
    
    async def get_designs_by_type(
        self,
        user_id: str,
        diagram_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get designs by diagram type.
        
        Args:
            user_id: User ID
            diagram_type: Type of diagram
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of designs of the specified type
        """
        return await self.find_many(
            {"user_id": user_id, "diagram_type": diagram_type},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def count_by_project(self, project_id: str) -> int:
        """
        Count designs for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Number of designs
        """
        return await self.count({"project_id": project_id})
