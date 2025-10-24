"""
RAG Retriever

This module provides a LangChain-compatible retriever that interfaces
with the KnowledgeBaseService for Retrieval-Augmented Generation.
"""

from typing import List, Optional
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
import logging

from app.services.knowledge_base_service import KnowledgeBaseService
from app.schemas.knowledge_base import KnowledgeDocument


logger = logging.getLogger(__name__)


class RAGRetriever(BaseRetriever):
    """
    LangChain-compatible retriever for the knowledge base.
    
    This retriever acts as a bridge between LangChain and our
    KnowledgeBaseService, enabling seamless RAG integration.
    """
    
    kb_service: KnowledgeBaseService
    top_k: int = 5
    category_filter: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None
    ) -> List[Document]:
        """
        Get relevant documents for a query (synchronous wrapper).
        
        Args:
            query: Search query
            run_manager: Callback manager
            
        Returns:
            List of LangChain Document objects
        """
        # This is a sync method required by BaseRetriever
        # For async usage, use _aget_relevant_documents
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self._aget_relevant_documents(query, run_manager=run_manager)
        )
    
    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None
    ) -> List[Document]:
        """
        Get relevant documents for a query (asynchronous).
        
        Args:
            query: Search query
            run_manager: Callback manager
            
        Returns:
            List of LangChain Document objects
        """
        try:
            # Get context from knowledge base service
            rag_context = await self.kb_service.get_context(
                query=query,
                top_k=self.top_k,
                category_filter=self.category_filter
            )
            
            # Convert KnowledgeDocuments to LangChain Documents
            documents = []
            for kb_doc in rag_context.relevant_documents:
                # Create metadata for LangChain document
                metadata = {
                    "source": kb_doc.metadata.source,
                    "title": kb_doc.title,
                    "category": kb_doc.category,
                    "quality_score": kb_doc.metadata.quality_score,
                }
                
                if kb_doc.metadata.url:
                    metadata["url"] = kb_doc.metadata.url
                
                if kb_doc.metadata.author:
                    metadata["author"] = kb_doc.metadata.author
                
                # Create page content
                page_content = self._format_document_content(kb_doc)
                
                # Create LangChain Document
                doc = Document(
                    page_content=page_content,
                    metadata=metadata
                )
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} relevant documents for query: {query[:50]}...")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {str(e)}")
            # Return empty list on error to prevent chain failure
            return []
    
    def _format_document_content(self, kb_doc: KnowledgeDocument) -> str:
        """
        Format knowledge document content for LangChain.
        
        Args:
            kb_doc: Knowledge base document
            
        Returns:
            Formatted content string
        """
        parts = [
            f"# {kb_doc.title}",
            f"\n**Category**: {kb_doc.category}",
            f"\n{kb_doc.content}"
        ]
        
        if kb_doc.use_cases:
            parts.append("\n**Use Cases**:")
            for uc in kb_doc.use_cases:
                parts.append(f"- {uc}")
        
        if kb_doc.advantages:
            parts.append("\n**Advantages**:")
            for adv in kb_doc.advantages:
                parts.append(f"- {adv}")
        
        if kb_doc.disadvantages:
            parts.append("\n**Disadvantages**:")
            for dis in kb_doc.disadvantages:
                parts.append(f"- {dis}")
        
        if kb_doc.implementation_notes:
            parts.append(f"\n**Implementation Notes**: {kb_doc.implementation_notes}")
        
        if kb_doc.related_patterns:
            parts.append(f"\n**Related Patterns**: {', '.join(kb_doc.related_patterns)}")
        
        return "\n".join(parts)


class MultiCategoryRAGRetriever(BaseRetriever):
    """
    RAG Retriever that searches across multiple categories.
    
    This retriever performs separate searches for each category
    and combines the results.
    """
    
    kb_service: KnowledgeBaseService
    categories: List[str]
    top_k_per_category: int = 2
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None
    ) -> List[Document]:
        """Get relevant documents (synchronous wrapper)."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self._aget_relevant_documents(query, run_manager=run_manager)
        )
    
    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None
    ) -> List[Document]:
        """Get relevant documents across multiple categories."""
        try:
            all_documents = []
            
            # Search in each category
            for category in self.categories:
                retriever = RAGRetriever(
                    kb_service=self.kb_service,
                    top_k=self.top_k_per_category,
                    category_filter=category
                )
                
                docs = await retriever._aget_relevant_documents(
                    query,
                    run_manager=run_manager
                )
                all_documents.extend(docs)
            
            logger.info(
                f"Retrieved {len(all_documents)} documents across "
                f"{len(self.categories)} categories"
            )
            return all_documents
            
        except Exception as e:
            logger.error(f"Multi-category retrieval failed: {str(e)}")
            return []
