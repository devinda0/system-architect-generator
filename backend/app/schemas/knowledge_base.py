"""
Knowledge Base Schemas

This module provides Pydantic models for the Architecture Knowledge Base,
including documents, metadata, and search results for RAG functionality.
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId


class KnowledgeDocumentMetadata(BaseModel):
    """Metadata for knowledge base documents."""
    
    source: str = Field(..., description="Source of the document (e.g., blog, book, official docs)")
    author: Optional[str] = Field(None, description="Author of the document")
    url: Optional[str] = Field(None, description="URL reference")
    version: str = Field(default="1.0", description="Version of the document")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Quality score (0-1)")
    last_reviewed: Optional[datetime] = Field(None, description="Last review date")
    is_verified: bool = Field(default=False, description="Whether content is verified by expert")


class KnowledgeDocument(BaseModel):
    """Document model for the knowledge base."""
    
    id: Optional[str] = Field(None, alias="_id", description="Unique identifier")
    category: Literal[
        "architectural_pattern",
        "technology",
        "design_principle",
        "best_practice"
    ] = Field(..., description="Category of the knowledge")
    
    title: str = Field(..., min_length=1, max_length=500, description="Document title")
    content: str = Field(..., min_length=1, description="Main content/description")
    
    # Structured fields for different categories
    use_cases: Optional[List[str]] = Field(None, description="Typical use cases")
    advantages: Optional[List[str]] = Field(None, description="Advantages/strengths")
    disadvantages: Optional[List[str]] = Field(None, description="Disadvantages/weaknesses")
    implementation_notes: Optional[str] = Field(None, description="Implementation considerations")
    
    # Technology-specific fields
    tech_stack_compatibility: Optional[List[str]] = Field(None, description="Compatible technologies")
    programming_languages: Optional[List[str]] = Field(None, description="Supported languages")
    
    # Pattern-specific fields
    related_patterns: Optional[List[str]] = Field(None, description="Related architectural patterns")
    anti_patterns: Optional[List[str]] = Field(None, description="Anti-patterns to avoid")
    
    # Metadata
    metadata: KnowledgeDocumentMetadata
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "category": "architectural_pattern",
                "title": "Microservices Architecture",
                "content": "Microservices is an architectural style that structures an application as a collection of loosely coupled services...",
                "use_cases": ["Scalable web applications", "Complex business domains"],
                "advantages": ["Independent deployment", "Technology diversity"],
                "disadvantages": ["Increased complexity", "Network overhead"],
                "implementation_notes": "Requires robust DevOps practices and monitoring",
                "metadata": {
                    "source": "Martin Fowler Blog",
                    "tags": ["architecture", "distributed-systems"],
                    "quality_score": 0.95
                }
            }
        }


class KnowledgeDocumentCreate(BaseModel):
    """Schema for creating a new knowledge document."""
    
    category: Literal[
        "architectural_pattern",
        "technology",
        "design_principle",
        "best_practice"
    ]
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    use_cases: Optional[List[str]] = None
    advantages: Optional[List[str]] = None
    disadvantages: Optional[List[str]] = None
    implementation_notes: Optional[str] = None
    tech_stack_compatibility: Optional[List[str]] = None
    programming_languages: Optional[List[str]] = None
    related_patterns: Optional[List[str]] = None
    anti_patterns: Optional[List[str]] = None
    metadata: KnowledgeDocumentMetadata


class KnowledgeDocumentUpdate(BaseModel):
    """Schema for updating a knowledge document."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    use_cases: Optional[List[str]] = None
    advantages: Optional[List[str]] = None
    disadvantages: Optional[List[str]] = None
    implementation_notes: Optional[str] = None
    tech_stack_compatibility: Optional[List[str]] = None
    programming_languages: Optional[List[str]] = None
    related_patterns: Optional[List[str]] = None
    anti_patterns: Optional[List[str]] = None
    metadata: Optional[KnowledgeDocumentMetadata] = None


class SearchResult(BaseModel):
    """Single search result from knowledge base."""
    
    document: KnowledgeDocument
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    distance: float = Field(..., ge=0.0, description="Vector distance")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document": {
                    "title": "Microservices Architecture",
                    "category": "architectural_pattern",
                    "content": "...",
                    "metadata": {"source": "Martin Fowler"}
                },
                "score": 0.92,
                "distance": 0.15
            }
        }


class SearchResults(BaseModel):
    """Collection of search results."""
    
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(default_factory=list)
    total_results: int = Field(default=0, description="Total number of results")
    top_k: int = Field(default=5, description="Number of results requested")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "scalable web architecture",
                "results": [],
                "total_results": 10,
                "top_k": 5
            }
        }


class RAGContext(BaseModel):
    """Context retrieved from RAG for prompt augmentation."""
    
    query: str = Field(..., description="Original query")
    relevant_documents: List[KnowledgeDocument] = Field(default_factory=list)
    context_text: str = Field(..., description="Formatted context for prompt")
    sources: List[str] = Field(default_factory=list, description="Sources used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "event-driven architecture",
                "relevant_documents": [],
                "context_text": "Based on the knowledge base:\n\n1. Event-Driven Architecture...",
                "sources": ["Martin Fowler Blog", "AWS Documentation"]
            }
        }


class KnowledgeStats(BaseModel):
    """Statistics about the knowledge base."""
    
    total_documents: int = 0
    by_category: Dict[str, int] = Field(default_factory=dict)
    verified_documents: int = 0
    last_updated: Optional[datetime] = None
    average_quality_score: float = 0.0
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_documents": 150,
                "by_category": {
                    "architectural_pattern": 45,
                    "technology": 60,
                    "design_principle": 25,
                    "best_practice": 20
                },
                "verified_documents": 120,
                "average_quality_score": 0.87
            }
        }
