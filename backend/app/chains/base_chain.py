"""
Base Chain for Design Engine

Provides a base class for all specialized design chains using LangChain Expression Language (LCEL).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
import logging

from app.utils.rag_retriever import RAGRetriever
from app.services.knowledge_base_service import KnowledgeBaseService
from app.config.gemini_config import GeminiConfig

logger = logging.getLogger(__name__)


class BaseDesignChain(ABC):
    """
    Base class for all specialized design chains.
    
    Each chain follows the pattern: Prompt -> RAG -> LLM -> Parser
    using LangChain Expression Language (LCEL).
    """
    
    def __init__(
        self,
        kb_service: Optional[KnowledgeBaseService] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        use_rag: bool = True,
    ):
        """
        Initialize the base design chain.
        
        Args:
            kb_service: Knowledge base service for RAG
            model_name: Gemini model name (defaults to config)
            temperature: Model temperature
            use_rag: Whether to use RAG retrieval
        """
        self.kb_service = kb_service
        self.use_rag = use_rag
        
        # Initialize LLM
        config = GeminiConfig()
        self.llm = ChatGoogleGenerativeAI(
            model=model_name or config.DEFAULT_MODEL,
            temperature=temperature,
            google_api_key=config.get_api_key()
        )
        
        # Initialize RAG retriever if enabled
        self.retriever: Optional[RAGRetriever] = None
        if use_rag and kb_service:
            self.retriever = RAGRetriever(
                kb_service=kb_service,
                top_k=5,
            )
        
        # Initialize output parser
        self.output_parser = JsonOutputParser()
        
        # Build the chain (to be implemented by subclasses)
        self.chain: Optional[Runnable] = None
    
    @abstractmethod
    def _create_prompt(self) -> ChatPromptTemplate:
        """
        Create the prompt template for this chain.
        
        Returns:
            ChatPromptTemplate for the chain
        """
        pass
    
    @abstractmethod
    def _build_chain(self) -> Runnable:
        """
        Build the LCEL chain.
        
        Returns:
            Runnable chain combining prompt, RAG, LLM, and parser
        """
        pass
    
    async def ainvoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronously invoke the chain.
        
        Args:
            inputs: Input dictionary for the chain
            
        Returns:
            Output from the chain
        """
        if not self.chain:
            self.chain = self._build_chain()
        
        try:
            result = await self.chain.ainvoke(inputs)
            return result
        except Exception as e:
            logger.error(f"Error invoking chain: {e}")
            raise
    
    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronously invoke the chain.
        
        Args:
            inputs: Input dictionary for the chain
            
        Returns:
            Output from the chain
        """
        if not self.chain:
            self.chain = self._build_chain()
        
        try:
            result = self.chain.invoke(inputs)
            return result
        except Exception as e:
            logger.error(f"Error invoking chain: {e}")
            raise
    
    async def _get_rag_context(self, query: str) -> str:
        """
        Get RAG context for a query.
        
        Args:
            query: Search query
            
        Returns:
            Formatted context string
        """
        if not self.retriever:
            return ""
        
        try:
            documents = await self.retriever._aget_relevant_documents(query)
            if not documents:
                return ""
            
            # Format documents into context
            context_parts = []
            for i, doc in enumerate(documents, 1):
                context_parts.append(
                    f"--- Document {i} ---\n"
                    f"Title: {doc.metadata.get('title', 'N/A')}\n"
                    f"Category: {doc.metadata.get('category', 'N/A')}\n"
                    f"Content:\n{doc.page_content}\n"
                )
            
            return "\n".join(context_parts)
        except Exception as e:
            logger.warning(f"Error getting RAG context: {e}")
            return ""
