"""
Base Repository Class

This module provides a base repository class with common CRUD operations
for MongoDB collections. All specific repositories should inherit from this class.
"""

from typing import TypeVar, Generic, Optional, List, Dict, Any
from datetime import datetime, UTC
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError as PyMongoDuplicateKeyError
from bson import ObjectId
import logging

from app.exceptions.mongodb_exceptions import (
    DocumentNotFoundError,
    DuplicateKeyError,
    InvalidObjectIdError,
    DatabaseOperationError,
    QueryError
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository class providing common CRUD operations.
    
    This class implements the Repository pattern for MongoDB collections,
    providing a clean abstraction over database operations.
    """
    
    def __init__(self, collection: AsyncIOMotorCollection, collection_name: str):
        """
        Initialize the repository.
        
        Args:
            collection: Motor collection instance
            collection_name: Name of the collection (for error messages)
        """
        self.collection = collection
        self.collection_name = collection_name
    
    @staticmethod
    def _validate_object_id(object_id: str) -> ObjectId:
        """
        Validate and convert string to ObjectId.
        
        Args:
            object_id: String representation of ObjectId
            
        Returns:
            Valid ObjectId instance
            
        Raises:
            InvalidObjectIdError: If the ObjectId is invalid
        """
        if not ObjectId.is_valid(object_id):
            raise InvalidObjectIdError(object_id)
        return ObjectId(object_id)
    
    @staticmethod
    def _convert_id(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Convert MongoDB _id field to string.
        
        Args:
            doc: MongoDB document
            
        Returns:
            Document with _id converted to string
        """
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    async def create(self, data: Dict[str, Any]) -> str:
        """
        Create a new document.
        
        Args:
            data: Document data
            
        Returns:
            String ID of the created document
            
        Raises:
            DuplicateKeyError: If a unique constraint is violated
            DatabaseOperationError: If the operation fails
        """
        try:
            # Add timestamps
            now = datetime.now(UTC)
            data["created_at"] = now
            data["updated_at"] = now
            
            result = await self.collection.insert_one(data)
            logger.info(f"Created document in {self.collection_name}: {result.inserted_id}")
            return str(result.inserted_id)
            
        except PyMongoDuplicateKeyError as e:
            # Extract the duplicate key information
            key_pattern = e.details.get("keyPattern", {}) if e.details else {}
            key_value = e.details.get("keyValue", {}) if e.details else {}
            field = list(key_pattern.keys())[0] if key_pattern else "unknown"
            value = key_value.get(field, "unknown")
            
            logger.warning(f"Duplicate key error in {self.collection_name}: {field}={value}")
            raise DuplicateKeyError(self.collection_name, field, value, str(e))
            
        except Exception as e:
            logger.error(f"Error creating document in {self.collection_name}: {e}")
            raise DatabaseOperationError("create", str(e))
    
    async def find_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a document by its ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document if found, None otherwise
            
        Raises:
            InvalidObjectIdError: If the ID format is invalid
            DatabaseOperationError: If the operation fails
        """
        try:
            object_id = self._validate_object_id(document_id)
            doc = await self.collection.find_one({"_id": object_id})
            return self._convert_id(doc)
            
        except InvalidObjectIdError:
            raise
        except Exception as e:
            logger.error(f"Error finding document by ID in {self.collection_name}: {e}")
            raise DatabaseOperationError("find_by_id", str(e))
    
    async def find_one(self, filter_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching the filter.
        
        Args:
            filter_query: MongoDB filter query
            
        Returns:
            Document if found, None otherwise
            
        Raises:
            DatabaseOperationError: If the operation fails
        """
        try:
            doc = await self.collection.find_one(filter_query)
            return self._convert_id(doc)
            
        except Exception as e:
            logger.error(f"Error finding document in {self.collection_name}: {e}")
            raise DatabaseOperationError("find_one", str(e))
    
    async def find_many(
        self,
        filter_query: Dict[str, Any] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find multiple documents matching the filter.
        
        Args:
            filter_query: MongoDB filter query (default: {})
            skip: Number of documents to skip (pagination)
            limit: Maximum number of documents to return
            sort: Sort specification (e.g., [("created_at", -1)])
            
        Returns:
            List of documents
            
        Raises:
            QueryError: If the query fails
        """
        try:
            filter_query = filter_query or {}
            cursor = self.collection.find(filter_query)
            
            if sort:
                cursor = cursor.sort(sort)
            
            cursor = cursor.skip(skip).limit(limit)
            
            docs = await cursor.to_list(length=limit)
            return [self._convert_id(doc) for doc in docs]
            
        except Exception as e:
            logger.error(f"Error finding documents in {self.collection_name}: {e}")
            raise QueryError(f"Failed to query {self.collection_name}", str(e))
    
    async def update_by_id(
        self,
        document_id: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """
        Update a document by its ID.
        
        Args:
            document_id: Document ID
            update_data: Data to update
            
        Returns:
            True if document was updated, False if not found
            
        Raises:
            InvalidObjectIdError: If the ID format is invalid
            DuplicateKeyError: If update violates unique constraint
            DatabaseOperationError: If the operation fails
        """
        try:
            object_id = self._validate_object_id(document_id)
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.now(UTC)
            
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            if result.matched_count > 0:
                logger.info(f"Updated document in {self.collection_name}: {document_id}")
                return True
            return False
            
        except InvalidObjectIdError:
            raise
        except PyMongoDuplicateKeyError as e:
            key_pattern = e.details.get("keyPattern", {}) if e.details else {}
            key_value = e.details.get("keyValue", {}) if e.details else {}
            field = list(key_pattern.keys())[0] if key_pattern else "unknown"
            value = key_value.get(field, "unknown")
            
            logger.warning(f"Duplicate key error updating {self.collection_name}: {field}={value}")
            raise DuplicateKeyError(self.collection_name, field, value, str(e))
        except Exception as e:
            logger.error(f"Error updating document in {self.collection_name}: {e}")
            raise DatabaseOperationError("update_by_id", str(e))
    
    async def update_one(
        self,
        filter_query: Dict[str, Any],
        update_data: Dict[str, Any]
    ) -> bool:
        """
        Update a single document matching the filter.
        
        Args:
            filter_query: MongoDB filter query
            update_data: Data to update
            
        Returns:
            True if document was updated, False if not found
            
        Raises:
            DatabaseOperationError: If the operation fails
        """
        try:
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                filter_query,
                {"$set": update_data}
            )
            
            return result.matched_count > 0
            
        except Exception as e:
            logger.error(f"Error updating document in {self.collection_name}: {e}")
            raise DatabaseOperationError("update_one", str(e))
    
    async def delete_by_id(self, document_id: str) -> bool:
        """
        Delete a document by its ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if document was deleted, False if not found
            
        Raises:
            InvalidObjectIdError: If the ID format is invalid
            DatabaseOperationError: If the operation fails
        """
        try:
            object_id = self._validate_object_id(document_id)
            result = await self.collection.delete_one({"_id": object_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted document from {self.collection_name}: {document_id}")
                return True
            return False
            
        except InvalidObjectIdError:
            raise
        except Exception as e:
            logger.error(f"Error deleting document from {self.collection_name}: {e}")
            raise DatabaseOperationError("delete_by_id", str(e))
    
    async def delete_one(self, filter_query: Dict[str, Any]) -> bool:
        """
        Delete a single document matching the filter.
        
        Args:
            filter_query: MongoDB filter query
            
        Returns:
            True if document was deleted, False if not found
            
        Raises:
            DatabaseOperationError: If the operation fails
        """
        try:
            result = await self.collection.delete_one(filter_query)
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting document from {self.collection_name}: {e}")
            raise DatabaseOperationError("delete_one", str(e))
    
    async def delete_many(self, filter_query: Dict[str, Any]) -> int:
        """
        Delete multiple documents matching the filter.
        
        Args:
            filter_query: MongoDB filter query
            
        Returns:
            Number of documents deleted
            
        Raises:
            DatabaseOperationError: If the operation fails
        """
        try:
            result = await self.collection.delete_many(filter_query)
            logger.info(f"Deleted {result.deleted_count} documents from {self.collection_name}")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting documents from {self.collection_name}: {e}")
            raise DatabaseOperationError("delete_many", str(e))
    
    async def count(self, filter_query: Dict[str, Any] = None) -> int:
        """
        Count documents matching the filter.
        
        Args:
            filter_query: MongoDB filter query (default: {})
            
        Returns:
            Number of documents
            
        Raises:
            QueryError: If the count operation fails
        """
        try:
            filter_query = filter_query or {}
            count = await self.collection.count_documents(filter_query)
            return count
            
        except Exception as e:
            logger.error(f"Error counting documents in {self.collection_name}: {e}")
            raise QueryError(f"Failed to count documents in {self.collection_name}", str(e))
    
    async def exists(self, filter_query: Dict[str, Any]) -> bool:
        """
        Check if a document exists matching the filter.
        
        Args:
            filter_query: MongoDB filter query
            
        Returns:
            True if document exists, False otherwise
            
        Raises:
            QueryError: If the operation fails
        """
        try:
            count = await self.collection.count_documents(filter_query, limit=1)
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking document existence in {self.collection_name}: {e}")
            raise QueryError(f"Failed to check existence in {self.collection_name}", str(e))
