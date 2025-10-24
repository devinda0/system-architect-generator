"""
Knowledge Base API Endpoints

This module provides FastAPI endpoints for managing and querying the
architecture knowledge base with RAG capabilities.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from app.config.mongodb_config import get_database
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.services.knowledge_base_service import KnowledgeBaseService
from app.schemas.knowledge_base import (
    KnowledgeDocument,
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    SearchResults,
    RAGContext,
    KnowledgeStats
)
from app.utils.knowledge_base_seeder import (
    KnowledgeBaseSeeder,
    seed_knowledge_base,
    get_knowledge_base_status
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])


# Dependency to get knowledge base service
async def get_kb_service(
    database: AsyncIOMotorDatabase = Depends(get_database)
) -> KnowledgeBaseService:
    """Get knowledge base service instance."""
    repository = KnowledgeBaseRepository(database)
    return KnowledgeBaseService(repository)


async def get_kb_repository(
    database: AsyncIOMotorDatabase = Depends(get_database)
) -> KnowledgeBaseRepository:
    """Get knowledge base repository instance."""
    return KnowledgeBaseRepository(database)


@router.post(
    "/documents",
    response_model=KnowledgeDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Create a knowledge document",
    description="Create a new document in the knowledge base and add to vector store"
)
async def create_document(
    document: KnowledgeDocumentCreate,
    repository: KnowledgeBaseRepository = Depends(get_kb_repository),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """Create a new knowledge base document."""
    try:
        # Create in MongoDB
        created_doc = await repository.create_document(document)
        
        # Add to vector store
        await kb_service.add_document(created_doc)
        
        logger.info(f"Created document: {created_doc.title}")
        return created_doc
        
    except Exception as e:
        logger.error(f"Failed to create document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document: {str(e)}"
        )


@router.get(
    "/documents/{document_id}",
    response_model=KnowledgeDocument,
    summary="Get a document by ID"
)
async def get_document(
    document_id: str,
    repository: KnowledgeBaseRepository = Depends(get_kb_repository)
):
    """Get a knowledge document by ID."""
    try:
        document = await repository.get_document_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )


@router.get(
    "/documents",
    response_model=List[KnowledgeDocument],
    summary="List all documents"
)
async def list_documents(
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum documents to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    verified_only: bool = Query(False, description="Only return verified documents"),
    repository: KnowledgeBaseRepository = Depends(get_kb_repository)
):
    """List all knowledge base documents with optional filtering."""
    try:
        if category:
            documents = await repository.get_documents_by_category(
                category, skip, limit
            )
        else:
            documents = await repository.get_all_documents(
                skip, limit, verified_only
            )
        
        return documents
        
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.put(
    "/documents/{document_id}",
    response_model=KnowledgeDocument,
    summary="Update a document"
)
async def update_document(
    document_id: str,
    update_data: KnowledgeDocumentUpdate,
    repository: KnowledgeBaseRepository = Depends(get_kb_repository),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """Update a knowledge base document."""
    try:
        updated_doc = await repository.update_document(document_id, update_data)
        
        if not updated_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        # Update in vector store
        await kb_service.add_document(updated_doc, force_update=True)
        
        logger.info(f"Updated document: {updated_doc.title}")
        return updated_doc
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document: {str(e)}"
        )


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document"
)
async def delete_document(
    document_id: str,
    repository: KnowledgeBaseRepository = Depends(get_kb_repository),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """Delete a knowledge base document."""
    try:
        deleted = await repository.delete_document(document_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        # Delete from vector store
        await kb_service.delete_document(document_id)
        
        logger.info(f"Deleted document: {document_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.get(
    "/search",
    response_model=SearchResults,
    summary="Search knowledge base",
    description="Perform semantic search on the knowledge base using vector similarity"
)
async def search_knowledge_base(
    query: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum similarity score"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """Search the knowledge base using semantic similarity."""
    try:
        results = await kb_service.search(
            query=query,
            top_k=top_k,
            category_filter=category,
            min_score=min_score
        )
        
        logger.info(f"Search for '{query}' returned {results.total_results} results")
        return results
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get(
    "/context",
    response_model=RAGContext,
    summary="Get RAG context",
    description="Get relevant context for RAG prompting based on a query"
)
async def get_rag_context(
    query: str = Query(..., min_length=1, description="Query or requirement text"),
    top_k: int = Query(5, ge=1, le=20, description="Number of relevant documents"),
    category: Optional[str] = Query(None, description="Filter by category"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """Get relevant context for RAG (Retrieval-Augmented Generation)."""
    try:
        context = await kb_service.get_context(
            query=query,
            top_k=top_k,
            category_filter=category
        )
        
        logger.info(f"Retrieved RAG context with {len(context.relevant_documents)} documents")
        return context
        
    except Exception as e:
        logger.error(f"Failed to get RAG context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get RAG context: {str(e)}"
        )


@router.get(
    "/statistics",
    response_model=KnowledgeStats,
    summary="Get knowledge base statistics"
)
async def get_statistics(
    repository: KnowledgeBaseRepository = Depends(get_kb_repository)
):
    """Get statistics about the knowledge base."""
    try:
        stats = await repository.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.post(
    "/seed",
    summary="Seed knowledge base",
    description="Seed the knowledge base with initial data"
)
async def seed_data(
    force_update: bool = Query(False, description="Force update existing documents"),
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Seed the knowledge base with initial data."""
    try:
        stats = await seed_knowledge_base(database, force_update)
        
        logger.info(f"Knowledge base seeded: {stats}")
        return {
            "message": "Knowledge base seeded successfully",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Seeding failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Seeding failed: {str(e)}"
        )


@router.get(
    "/status",
    summary="Get knowledge base status",
    description="Get current status and sync information"
)
async def get_status(
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get knowledge base status and sync information."""
    try:
        status_info = await get_knowledge_base_status(database)
        
        return {
            "message": "Knowledge base status retrieved",
            "status": status_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )


@router.get(
    "/tags/{tag}",
    response_model=List[KnowledgeDocument],
    summary="Search by tag"
)
async def search_by_tag(
    tag: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    repository: KnowledgeBaseRepository = Depends(get_kb_repository)
):
    """Search documents by tag."""
    try:
        documents = await repository.search_by_tags([tag], skip, limit)
        return documents
        
    except Exception as e:
        logger.error(f"Failed to search by tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search by tag: {str(e)}"
        )
