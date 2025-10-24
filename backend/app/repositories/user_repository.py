"""
User Repository

Repository for managing user documents in MongoDB.
"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from app.repositories.base_repository import BaseRepository
from app.schemas.mongodb_schemas import UserInDB, UserCreate, UserUpdate
from app.config.mongodb_config import get_mongodb_config
from app.exceptions.mongodb_exceptions import DocumentNotFoundError

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[UserInDB]):
    """Repository for user collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize UserRepository.
        
        Args:
            database: MongoDB database instance
        """
        config = get_mongodb_config()
        collection = database[config.MONGODB_USERS_COLLECTION]
        super().__init__(collection, config.MONGODB_USERS_COLLECTION)
    
    async def create_user(self, user_data: UserCreate, hashed_password: str) -> str:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            hashed_password: Hashed password
            
        Returns:
            ID of created user
        """
        data = user_data.model_dump()
        data.pop("password", None)  # Remove plain password
        data["hashed_password"] = hashed_password
        
        user_id = await self.create(data)
        logger.info(f"Created user: {user_data.username}")
        return user_id
    
    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find user by email address.
        
        Args:
            email: User email
            
        Returns:
            User document if found
        """
        return await self.find_one({"email": email})
    
    async def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Find user by username.
        
        Args:
            username: Username
            
        Returns:
            User document if found
        """
        return await self.find_one({"username": username})
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> bool:
        """
        Update user information.
        
        Args:
            user_id: User ID
            user_update: Update data
            
        Returns:
            True if updated successfully
            
        Raises:
            DocumentNotFoundError: If user not found
        """
        # Only include fields that are set
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Handle password separately if provided
        if "password" in update_data:
            # Password should be hashed by the service layer
            update_data.pop("password")
        
        if not update_data:
            return False
        
        updated = await self.update_by_id(user_id, update_data)
        if not updated:
            raise DocumentNotFoundError(self.collection_name, user_id)
        
        return True
    
    async def update_last_login(self, user_id: str) -> bool:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User ID
            
        Returns:
            True if updated successfully
        """
        from datetime import datetime
        return await self.update_by_id(user_id, {"last_login": datetime.utcnow()})
    
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all active users.
        
        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of active users
        """
        return await self.find_many(
            {"is_active": True},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deactivated successfully
        """
        return await self.update_by_id(user_id, {"is_active": False})
    
    async def email_exists(self, email: str) -> bool:
        """
        Check if email already exists.
        
        Args:
            email: Email to check
            
        Returns:
            True if email exists
        """
        return await self.exists({"email": email})
    
    async def username_exists(self, username: str) -> bool:
        """
        Check if username already exists.
        
        Args:
            username: Username to check
            
        Returns:
            True if username exists
        """
        return await self.exists({"username": username})
