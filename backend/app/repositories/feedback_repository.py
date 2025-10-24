"""
Feedback Repository

Repository for managing feedback documents in MongoDB.
"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from app.repositories.base_repository import BaseRepository
from app.schemas.mongodb_schemas import FeedbackInDB, FeedbackCreate, FeedbackUpdate
from app.config.mongodb_config import get_mongodb_config
from app.exceptions.mongodb_exceptions import DocumentNotFoundError

logger = logging.getLogger(__name__)


class FeedbackRepository(BaseRepository[FeedbackInDB]):
    """Repository for feedback collection operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize FeedbackRepository.
        
        Args:
            database: MongoDB database instance
        """
        config = get_mongodb_config()
        collection = database[config.MONGODB_FEEDBACK_COLLECTION]
        super().__init__(collection, config.MONGODB_FEEDBACK_COLLECTION)
    
    async def create_feedback(
        self,
        user_id: str,
        feedback_data: FeedbackCreate
    ) -> str:
        """
        Create new feedback.
        
        Args:
            user_id: ID of the user providing feedback
            feedback_data: Feedback creation data
            
        Returns:
            ID of created feedback
        """
        data = feedback_data.model_dump()
        data["user_id"] = user_id
        data["status"] = "new"
        
        feedback_id = await self.create(data)
        logger.info(f"Created feedback for design: {feedback_data.design_id}")
        return feedback_id
    
    async def update_feedback(
        self,
        feedback_id: str,
        feedback_update: FeedbackUpdate
    ) -> bool:
        """
        Update feedback information.
        
        Args:
            feedback_id: Feedback ID
            feedback_update: Update data
            
        Returns:
            True if updated successfully
            
        Raises:
            DocumentNotFoundError: If feedback not found
        """
        update_data = feedback_update.model_dump(exclude_unset=True)
        
        if not update_data:
            return False
        
        updated = await self.update_by_id(feedback_id, update_data)
        if not updated:
            raise DocumentNotFoundError(self.collection_name, feedback_id)
        
        return True
    
    async def find_by_design(
        self,
        design_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find all feedback for a specific design.
        
        Args:
            design_id: Design ID
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of feedback
        """
        return await self.find_many(
            {"design_id": design_id},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def find_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find all feedback by a specific user.
        
        Args:
            user_id: User ID
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of feedback
        """
        return await self.find_many(
            {"user_id": user_id},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def get_feedback_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get feedback by status.
        
        Args:
            status: Feedback status (new, reviewed, resolved, dismissed)
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of feedback with the specified status
        """
        return await self.find_many(
            {"status": status},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def get_feedback_by_type(
        self,
        feedback_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get feedback by type.
        
        Args:
            feedback_type: Type of feedback
            skip: Number of documents to skip
            limit: Maximum number of documents
            
        Returns:
            List of feedback of the specified type
        """
        return await self.find_many(
            {"feedback_type": feedback_type},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def get_average_rating_for_design(self, design_id: str) -> Optional[float]:
        """
        Calculate average rating for a design.
        
        Args:
            design_id: Design ID
            
        Returns:
            Average rating or None if no feedback
        """
        try:
            pipeline = [
                {"$match": {"design_id": design_id}},
                {"$group": {
                    "_id": None,
                    "average_rating": {"$avg": "$rating"}
                }}
            ]
            
            cursor = self.collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            
            if result:
                return result[0].get("average_rating")
            return None
            
        except Exception as e:
            logger.error(f"Error calculating average rating: {e}")
            return None
    
    async def get_rating_distribution(self, design_id: str) -> Dict[int, int]:
        """
        Get rating distribution for a design.
        
        Args:
            design_id: Design ID
            
        Returns:
            Dictionary mapping rating (1-5) to count
        """
        try:
            pipeline = [
                {"$match": {"design_id": design_id}},
                {"$group": {
                    "_id": "$rating",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            cursor = self.collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            # Initialize all ratings to 0
            distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            
            # Fill in actual counts
            for result in results:
                rating = result.get("_id")
                count = result.get("count", 0)
                if rating in distribution:
                    distribution[rating] = count
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error getting rating distribution: {e}")
            return {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    async def count_by_design(self, design_id: str) -> int:
        """
        Count feedback for a design.
        
        Args:
            design_id: Design ID
            
        Returns:
            Number of feedback items
        """
        return await self.count({"design_id": design_id})
    
    async def mark_as_reviewed(self, feedback_id: str) -> bool:
        """
        Mark feedback as reviewed.
        
        Args:
            feedback_id: Feedback ID
            
        Returns:
            True if marked successfully
        """
        return await self.update_by_id(feedback_id, {"status": "reviewed"})
    
    async def mark_as_resolved(self, feedback_id: str) -> bool:
        """
        Mark feedback as resolved.
        
        Args:
            feedback_id: Feedback ID
            
        Returns:
            True if marked successfully
        """
        return await self.update_by_id(feedback_id, {"status": "resolved"})
    
    async def dismiss_feedback(self, feedback_id: str) -> bool:
        """
        Dismiss feedback.
        
        Args:
            feedback_id: Feedback ID
            
        Returns:
            True if dismissed successfully
        """
        return await self.update_by_id(feedback_id, {"status": "dismissed"})
