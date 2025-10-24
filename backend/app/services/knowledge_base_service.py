"""
Knowledge Base Service

This module provides the service layer for managing the hybrid knowledge base
(Vector DB + MongoDB) and performing RAG (Retrieval-Augmented Generation) operations.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
import logging

from app.config.chroma_config import get_chroma_config
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.schemas.knowledge_base import (
    KnowledgeDocument,
    SearchResult,
    SearchResults,
    RAGContext
)


logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """
    Service for managing the hybrid knowledge base.
    
    This service combines:
    - Vector database (ChromaDB) for semantic search
    - MongoDB for structured metadata and document storage
    """
    
    def __init__(
        self,
        repository: KnowledgeBaseRepository,
        embedding_model: Optional[SentenceTransformer] = None
    ):
        """
        Initialize the knowledge base service.
        
        Args:
            repository: Knowledge base MongoDB repository
            embedding_model: Sentence transformer model for embeddings
        """
        self.repository = repository
        self.config = get_chroma_config()
        
        # Initialize embedding model
        if embedding_model:
            self.embedding_model = embedding_model
        else:
            logger.info(f"Loading embedding model: {self.config.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(self.config.EMBEDDING_MODEL)
        
        # Initialize ChromaDB client
        self._init_chroma_client()
    
    def _init_chroma_client(self):
        """Initialize ChromaDB client based on configuration."""
        try:
            if self.config.CHROMA_CLIENT_MODE == "persistent":
                self.chroma_client = chromadb.PersistentClient(
                    path=self.config.CHROMA_PERSIST_DIRECTORY
                )
            else:
                self.chroma_client = chromadb.HttpClient(
                    host=self.config.CHROMA_HOST,
                    port=self.config.CHROMA_PORT
                )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.config.CHROMA_COLLECTION_NAME,
                metadata={"description": "Architecture knowledge base for RAG"}
            )
            
            logger.info(f"ChromaDB collection '{self.config.CHROMA_COLLECTION_NAME}' initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    async def add_document(
        self,
        document: KnowledgeDocument,
        force_update: bool = False
    ) -> bool:
        """
        Add a document to both vector and metadata stores.
        
        Args:
            document: Knowledge document to add
            force_update: Whether to update if document already exists
            
        Returns:
            True if added successfully
        """
        try:
            # Create embedding from document content
            content_for_embedding = self._prepare_content_for_embedding(document)
            embedding = self.embedding_model.encode(content_for_embedding).tolist()
            
            # Create metadata for vector store
            vector_metadata = {
                "document_id": document.id or "temp",
                "category": document.category,
                "title": document.title,
                "source": document.metadata.source,
                "quality_score": document.metadata.quality_score
            }
            
            # Add to vector store
            doc_id = document.id or f"{document.category}_{document.title}"
            
            # Check if document exists
            try:
                existing = self.collection.get(ids=[doc_id])
                if existing and existing['ids'] and not force_update:
                    logger.warning(f"Document {doc_id} already exists in vector store")
                    return False
            except Exception:
                pass  # Document doesn't exist
            
            # Add or update in vector store
            self.collection.upsert(
                documents=[content_for_embedding],
                embeddings=[embedding],
                metadatas=[vector_metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Document '{document.title}' added to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document to knowledge base: {str(e)}")
            raise
    
    def _prepare_content_for_embedding(self, document: KnowledgeDocument) -> str:
        """
        Prepare document content for embedding.
        
        Args:
            document: Knowledge document
            
        Returns:
            Formatted content string
        """
        parts = [
            f"Title: {document.title}",
            f"Category: {document.category}",
            f"Content: {document.content}"
        ]
        
        if document.use_cases:
            parts.append(f"Use Cases: {', '.join(document.use_cases)}")
        
        if document.advantages:
            parts.append(f"Advantages: {', '.join(document.advantages)}")
        
        if document.disadvantages:
            parts.append(f"Disadvantages: {', '.join(document.disadvantages)}")
        
        if document.implementation_notes:
            parts.append(f"Implementation: {document.implementation_notes}")
        
        return "\n".join(parts)
    
    async def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        category_filter: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> SearchResults:
        """
        Perform semantic search on the knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results to return
            category_filter: Filter by document category
            min_score: Minimum similarity score threshold
            
        Returns:
            Search results with relevant documents
        """
        try:
            k = top_k or self.config.DEFAULT_TOP_K
            threshold = min_score or self.config.SIMILARITY_THRESHOLD
            
            # Create query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Prepare where clause for filtering
            where_clause = {}
            if category_filter:
                where_clause["category"] = category_filter
            
            # Search in vector store
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where_clause if where_clause else None
            )
            
            # Process results
            search_results = []
            if results and results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    # Convert distance to similarity score (assuming cosine distance)
                    score = 1 - distance
                    
                    if score >= threshold:
                        # Get full document from MongoDB
                        metadata = results['metadatas'][0][i]
                        document_id = metadata.get('document_id')
                        
                        # Fetch from MongoDB if we have the ID
                        doc = None
                        if document_id and document_id != "temp":
                            doc = await self.repository.get_document_by_id(document_id)
                        
                        # If not found in MongoDB, create minimal document from metadata
                        if not doc:
                            doc = await self.repository.get_document_by_title(
                                metadata.get('title')
                            )
                        
                        if doc:
                            search_results.append(
                                SearchResult(
                                    document=doc,
                                    score=score,
                                    distance=distance
                                )
                            )
            
            return SearchResults(
                query=query,
                results=search_results,
                total_results=len(search_results),
                top_k=k
            )
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise
    
    async def get_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        category_filter: Optional[str] = None
    ) -> RAGContext:
        """
        Get relevant context for RAG prompting.
        
        This is the core method for RAG - it retrieves relevant knowledge
        and formats it for inclusion in LLM prompts.
        
        Args:
            query: Query or requirement text
            top_k: Number of relevant documents to retrieve
            category_filter: Filter by document category
            
        Returns:
            RAG context with formatted text and sources
        """
        try:
            # Perform semantic search
            search_results = await self.search(
                query=query,
                top_k=top_k,
                category_filter=category_filter
            )
            
            # Extract documents and sources
            relevant_docs = [result.document for result in search_results.results]
            sources = list(set([doc.metadata.source for doc in relevant_docs]))
            
            # Format context text for prompt
            context_text = self._format_context_for_prompt(relevant_docs)
            
            return RAGContext(
                query=query,
                relevant_documents=relevant_docs,
                context_text=context_text,
                sources=sources
            )
            
        except Exception as e:
            logger.error(f"Failed to get context: {str(e)}")
            raise
    
    def _format_context_for_prompt(
        self,
        documents: List[KnowledgeDocument]
    ) -> str:
        """
        Format retrieved documents into context text for prompts.
        
        Args:
            documents: List of relevant knowledge documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant knowledge base context available."
        
        context_parts = ["Based on the Architecture Knowledge Base:\n"]
        
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"\n{i}. {doc.title} ({doc.category})")
            context_parts.append(f"   {doc.content}")
            
            if doc.use_cases:
                context_parts.append(f"   Use Cases: {', '.join(doc.use_cases)}")
            
            if doc.advantages:
                context_parts.append(f"   Advantages: {', '.join(doc.advantages[:3])}")
            
            if doc.disadvantages:
                context_parts.append(f"   Considerations: {', '.join(doc.disadvantages[:3])}")
            
            context_parts.append(f"   Source: {doc.metadata.source}")
        
        return "\n".join(context_parts)
    
    async def bulk_add_documents(
        self,
        documents: List[KnowledgeDocument]
    ) -> Dict[str, int]:
        """
        Bulk add documents to knowledge base.
        
        Args:
            documents: List of knowledge documents
            
        Returns:
            Statistics about added documents
        """
        try:
            added_count = 0
            failed_count = 0
            
            for doc in documents:
                try:
                    success = await self.add_document(doc)
                    if success:
                        added_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"Failed to add document '{doc.title}': {str(e)}")
                    failed_count += 1
            
            logger.info(
                f"Bulk add complete: {added_count} added, {failed_count} failed"
            )
            
            return {
                "added": added_count,
                "failed": failed_count,
                "total": len(documents)
            }
            
        except Exception as e:
            logger.error(f"Bulk add failed: {str(e)}")
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from both vector and metadata stores.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deleted successfully
        """
        try:
            # Delete from vector store
            try:
                self.collection.delete(ids=[document_id])
                logger.info(f"Document {document_id} deleted from vector store")
            except Exception as e:
                logger.warning(f"Failed to delete from vector store: {str(e)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.config.CHROMA_COLLECTION_NAME,
                "total_embeddings": count,
                "embedding_model": self.config.EMBEDDING_MODEL,
                "embedding_dimension": self.config.EMBEDDING_DIMENSION
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {}
