"""
Knowledge Base Seeding Utility

This module provides utilities for seeding and managing the knowledge base
with initial data and updates.
"""

import asyncio
import logging
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.knowledge_base import KnowledgeDocument, KnowledgeDocumentCreate
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.services.knowledge_base_service import KnowledgeBaseService
from app.utils.knowledge_base_seed_data import ALL_SEED_DATA


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeBaseSeeder:
    """Utility class for seeding the knowledge base."""
    
    def __init__(
        self,
        repository: KnowledgeBaseRepository,
        kb_service: KnowledgeBaseService
    ):
        """
        Initialize the seeder.
        
        Args:
            repository: Knowledge base MongoDB repository
            kb_service: Knowledge base service with vector DB
        """
        self.repository = repository
        self.kb_service = kb_service
    
    async def seed_initial_data(
        self,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """
        Seed the knowledge base with initial data.
        
        Args:
            force_update: Whether to update existing documents
            
        Returns:
            Statistics about the seeding operation
        """
        logger.info("Starting knowledge base seeding...")
        
        stats = {
            "total_processed": 0,
            "added_to_mongodb": 0,
            "added_to_vector_db": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "by_category": {}
        }
        
        try:
            for doc_create in ALL_SEED_DATA:
                stats["total_processed"] += 1
                category = doc_create.category
                
                if category not in stats["by_category"]:
                    stats["by_category"][category] = {
                        "added": 0,
                        "updated": 0,
                        "skipped": 0
                    }
                
                try:
                    # Check if document exists in MongoDB
                    existing = await self.repository.get_document_by_title(
                        doc_create.title
                    )
                    
                    if existing and not force_update:
                        logger.info(f"Skipping existing document: {doc_create.title}")
                        stats["skipped"] += 1
                        stats["by_category"][category]["skipped"] += 1
                        continue
                    
                    # Create or update in MongoDB
                    if existing:
                        # Update existing document
                        from app.schemas.knowledge_base import KnowledgeDocumentUpdate
                        update_data = KnowledgeDocumentUpdate(
                            content=doc_create.content,
                            use_cases=doc_create.use_cases,
                            advantages=doc_create.advantages,
                            disadvantages=doc_create.disadvantages,
                            implementation_notes=doc_create.implementation_notes,
                            tech_stack_compatibility=doc_create.tech_stack_compatibility,
                            programming_languages=doc_create.programming_languages,
                            related_patterns=doc_create.related_patterns,
                            anti_patterns=doc_create.anti_patterns,
                            metadata=doc_create.metadata
                        )
                        doc = await self.repository.update_document(
                            existing.id,
                            update_data
                        )
                        stats["updated"] += 1
                        stats["by_category"][category]["updated"] += 1
                        logger.info(f"Updated document: {doc_create.title}")
                    else:
                        # Create new document
                        doc = await self.repository.create_document(doc_create)
                        stats["added_to_mongodb"] += 1
                        stats["by_category"][category]["added"] += 1
                        logger.info(f"Created document: {doc_create.title}")
                    
                    # Add to vector database
                    if doc:
                        success = await self.kb_service.add_document(
                            doc,
                            force_update=force_update
                        )
                        if success:
                            stats["added_to_vector_db"] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing '{doc_create.title}': {str(e)}")
                    stats["errors"] += 1
            
            logger.info("Knowledge base seeding completed!")
            logger.info(f"Statistics: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Seeding failed: {str(e)}")
            raise
    
    async def clear_knowledge_base(self) -> bool:
        """
        Clear all documents from the knowledge base.
        
        WARNING: This will delete all data!
        
        Returns:
            True if successful
        """
        logger.warning("Clearing knowledge base...")
        
        try:
            # Get all documents
            all_docs = await self.repository.get_all_documents(limit=10000)
            
            # Delete from MongoDB
            for doc in all_docs:
                await self.repository.delete_document(doc.id)
            
            # Clear vector database collection
            self.kb_service.collection.delete(
                where={}  # This deletes all documents
            )
            
            logger.info(f"Cleared {len(all_docs)} documents from knowledge base")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear knowledge base: {str(e)}")
            raise
    
    async def get_seeding_status(self) -> Dict[str, Any]:
        """
        Get current status of the knowledge base.
        
        Returns:
            Status information
        """
        try:
            # Get MongoDB stats
            mongo_stats = await self.repository.get_statistics()
            
            # Get vector DB stats
            vector_stats = self.kb_service.get_collection_stats()
            
            return {
                "mongodb": mongo_stats.model_dump(),
                "vector_db": vector_stats,
                "sync_status": {
                    "in_sync": mongo_stats.total_documents == vector_stats.get("total_embeddings", 0),
                    "mongodb_count": mongo_stats.total_documents,
                    "vector_db_count": vector_stats.get("total_embeddings", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get seeding status: {str(e)}")
            raise


async def seed_knowledge_base(
    database: AsyncIOMotorDatabase,
    force_update: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to seed the knowledge base.
    
    Args:
        database: MongoDB database instance
        force_update: Whether to update existing documents
        
    Returns:
        Seeding statistics
    """
    repository = KnowledgeBaseRepository(database)
    kb_service = KnowledgeBaseService(repository)
    seeder = KnowledgeBaseSeeder(repository, kb_service)
    
    return await seeder.seed_initial_data(force_update=force_update)


async def get_knowledge_base_status(
    database: AsyncIOMotorDatabase
) -> Dict[str, Any]:
    """
    Get the current status of the knowledge base.
    
    Args:
        database: MongoDB database instance
        
    Returns:
        Status information
    """
    repository = KnowledgeBaseRepository(database)
    kb_service = KnowledgeBaseService(repository)
    seeder = KnowledgeBaseSeeder(repository, kb_service)
    
    return await seeder.get_seeding_status()


if __name__ == "__main__":
    # Example usage
    from app.config.mongodb_config import get_database
    
    async def main():
        db = get_database()
        stats = await seed_knowledge_base(db, force_update=False)
        print(f"Seeding completed: {stats}")
        
        status = await get_knowledge_base_status(db)
        print(f"Knowledge base status: {status}")
    
    asyncio.run(main())
