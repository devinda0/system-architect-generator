"""
Knowledge Base Repository

This module provides MongoDB repository for managing knowledge base documents,
including CRUD operations and metadata management.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base_repository import BaseRepository
from app.schemas.knowledge_base import (
    KnowledgeDocument,
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    KnowledgeStats
)
from app.exceptions.mongodb_exceptions import (
    DocumentNotFoundError,
    DocumentAlreadyExistsError,
    DatabaseOperationError
)


class KnowledgeBaseRepository(BaseRepository):
    """Repository for knowledge base documents."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize knowledge base repository.
        
        Args:
            database: MongoDB database instance
        """
        super().__init__(database, "knowledge_base")
    
    async def create_document(
        self,
        document: KnowledgeDocumentCreate
    ) -> KnowledgeDocument:
        """
        Create a new knowledge base document.
        
        Args:
            document: Document creation schema
            
        Returns:
            Created knowledge document
            
        Raises:
            DocumentAlreadyExistsError: If document with same title exists
            DatabaseOperationError: If operation fails
        """
        try:
            # Check if document with same title exists
            existing = await self.collection.find_one({"title": document.title})
            if existing:
                raise DocumentAlreadyExistsError(
                    f"Document with title '{document.title}' already exists"
                )
            
            # Prepare document
            doc_dict = document.model_dump()
            doc_dict["created_at"] = datetime.utcnow()
            doc_dict["updated_at"] = datetime.utcnow()
            
            # Insert document
            result = await self.collection.insert_one(doc_dict)
            
            # Retrieve and return created document
            created_doc = await self.collection.find_one({"_id": result.inserted_id})
            if created_doc:
                created_doc["_id"] = str(created_doc["_id"])
                return KnowledgeDocument(**created_doc)
            
            raise DatabaseOperationError("Failed to retrieve created document")
            
        except DocumentAlreadyExistsError:
            raise
        except Exception as e:
            raise DatabaseOperationError(f"Failed to create document: {str(e)}")
    
    async def get_document_by_id(self, document_id: str) -> Optional[KnowledgeDocument]:
        """
        Get a knowledge document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Knowledge document or None if not found
            
        Raises:
            DatabaseOperationError: If operation fails
        """
        try:
            doc = await self.collection.find_one({"_id": ObjectId(document_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                return KnowledgeDocument(**doc)
            return None
        except Exception as e:
            raise DatabaseOperationError(f"Failed to get document: {str(e)}")
    
    async def get_document_by_title(self, title: str) -> Optional[KnowledgeDocument]:
        """
        Get a knowledge document by title.
        
        Args:
            title: Document title
            
        Returns:
            Knowledge document or None if not found
        """
        try:
            doc = await self.collection.find_one({"title": title})
            if doc:
                doc["_id"] = str(doc["_id"])
                return KnowledgeDocument(**doc)
            return None
        except Exception as e:
            raise DatabaseOperationError(f"Failed to get document by title: {str(e)}")
    
    async def get_documents_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[KnowledgeDocument]:
        """
        Get all documents in a category.
        
        Args:
            category: Document category
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of knowledge documents
        """
        try:
            cursor = self.collection.find({"category": category}).skip(skip).limit(limit)
            documents = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                documents.append(KnowledgeDocument(**doc))
            return documents
        except Exception as e:
            raise DatabaseOperationError(f"Failed to get documents by category: {str(e)}")
    
    async def get_all_documents(
        self,
        skip: int = 0,
        limit: int = 100,
        verified_only: bool = False
    ) -> List[KnowledgeDocument]:
        """
        Get all knowledge documents.
        
        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            verified_only: Only return verified documents
            
        Returns:
            List of knowledge documents
        """
        try:
            query = {}
            if verified_only:
                query["metadata.is_verified"] = True
            
            cursor = self.collection.find(query).skip(skip).limit(limit)
            documents = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                documents.append(KnowledgeDocument(**doc))
            return documents
        except Exception as e:
            raise DatabaseOperationError(f"Failed to get all documents: {str(e)}")
    
    async def update_document(
        self,
        document_id: str,
        update_data: KnowledgeDocumentUpdate
    ) -> Optional[KnowledgeDocument]:
        """
        Update a knowledge document.
        
        Args:
            document_id: Document ID
            update_data: Update schema
            
        Returns:
            Updated knowledge document or None if not found
            
        Raises:
            DatabaseOperationError: If operation fails
        """
        try:
            # Get only non-None fields
            update_dict = update_data.model_dump(exclude_unset=True)
            if not update_dict:
                # Nothing to update
                return await self.get_document_by_id(document_id)
            
            update_dict["updated_at"] = datetime.utcnow()
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(document_id)},
                {"$set": update_dict},
                return_document=True
            )
            
            if result:
                result["_id"] = str(result["_id"])
                return KnowledgeDocument(**result)
            return None
        except Exception as e:
            raise DatabaseOperationError(f"Failed to update document: {str(e)}")
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a knowledge document.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            DatabaseOperationError: If operation fails
        """
        try:
            result = await self.collection.delete_one({"_id": ObjectId(document_id)})
            return result.deleted_count > 0
        except Exception as e:
            raise DatabaseOperationError(f"Failed to delete document: {str(e)}")
    
    async def search_by_tags(
        self,
        tags: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[KnowledgeDocument]:
        """
        Search documents by tags.
        
        Args:
            tags: List of tags to search for
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of matching knowledge documents
        """
        try:
            cursor = self.collection.find(
                {"metadata.tags": {"$in": tags}}
            ).skip(skip).limit(limit)
            
            documents = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                documents.append(KnowledgeDocument(**doc))
            return documents
        except Exception as e:
            raise DatabaseOperationError(f"Failed to search by tags: {str(e)}")
    
    async def get_statistics(self) -> KnowledgeStats:
        """
        Get knowledge base statistics.
        
        Returns:
            Knowledge base statistics
            
        Raises:
            DatabaseOperationError: If operation fails
        """
        try:
            # Total documents
            total = await self.collection.count_documents({})
            
            # Count by category
            pipeline = [
                {"$group": {"_id": "$category", "count": {"$sum": 1}}}
            ]
            category_counts = {}
            async for result in self.collection.aggregate(pipeline):
                category_counts[result["_id"]] = result["count"]
            
            # Verified documents
            verified = await self.collection.count_documents(
                {"metadata.is_verified": True}
            )
            
            # Average quality score
            avg_pipeline = [
                {"$group": {"_id": None, "avg_score": {"$avg": "$metadata.quality_score"}}}
            ]
            avg_score = 0.0
            async for result in self.collection.aggregate(avg_pipeline):
                avg_score = result.get("avg_score", 0.0)
            
            # Last updated
            last_doc = await self.collection.find_one(
                sort=[("updated_at", -1)]
            )
            last_updated = last_doc.get("updated_at") if last_doc else None
            
            return KnowledgeStats(
                total_documents=total,
                by_category=category_counts,
                verified_documents=verified,
                last_updated=last_updated,
                average_quality_score=avg_score
            )
        except Exception as e:
            raise DatabaseOperationError(f"Failed to get statistics: {str(e)}")
    
    async def bulk_create_documents(
        self,
        documents: List[KnowledgeDocumentCreate]
    ) -> List[str]:
        """
        Bulk create knowledge documents.
        
        Args:
            documents: List of document creation schemas
            
        Returns:
            List of created document IDs
            
        Raises:
            DatabaseOperationError: If operation fails
        """
        try:
            if not documents:
                return []
            
            docs_to_insert = []
            for doc in documents:
                doc_dict = doc.model_dump()
                doc_dict["created_at"] = datetime.utcnow()
                doc_dict["updated_at"] = datetime.utcnow()
                docs_to_insert.append(doc_dict)
            
            result = await self.collection.insert_many(docs_to_insert)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            raise DatabaseOperationError(f"Failed to bulk create documents: {str(e)}")
