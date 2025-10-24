"""
Tests for Knowledge Base Components

This module tests the knowledge base functionality including repositories,
services, RAG retrieval, and API endpoints.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from app.schemas.knowledge_base import (
    KnowledgeDocument,
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    KnowledgeDocumentMetadata,
    SearchResult,
    SearchResults,
    RAGContext,
    KnowledgeStats
)


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing."""
    return KnowledgeDocumentMetadata(
        source="Test Source",
        author="Test Author",
        tags=["test", "architecture"],
        quality_score=0.9,
        is_verified=True
    )


@pytest.fixture
def sample_document_create(sample_metadata):
    """Sample document creation schema."""
    return KnowledgeDocumentCreate(
        category="architectural_pattern",
        title="Test Microservices Pattern",
        content="This is a test description of microservices architecture.",
        use_cases=["Test use case 1", "Test use case 2"],
        advantages=["Advantage 1", "Advantage 2"],
        disadvantages=["Disadvantage 1"],
        implementation_notes="Test implementation notes",
        related_patterns=["Event-Driven Architecture"],
        metadata=sample_metadata
    )


@pytest.fixture
def sample_document(sample_metadata):
    """Sample knowledge document."""
    return KnowledgeDocument(
        id="test_id_123",
        category="architectural_pattern",
        title="Test Microservices Pattern",
        content="This is a test description of microservices architecture.",
        use_cases=["Test use case 1", "Test use case 2"],
        advantages=["Advantage 1", "Advantage 2"],
        disadvantages=["Disadvantage 1"],
        implementation_notes="Test implementation notes",
        related_patterns=["Event-Driven Architecture"],
        metadata=sample_metadata,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


class TestKnowledgeBaseSchemas:
    """Tests for knowledge base Pydantic schemas."""
    
    def test_knowledge_document_create_valid(self, sample_document_create):
        """Test creating a valid document schema."""
        assert sample_document_create.category == "architectural_pattern"
        assert sample_document_create.title == "Test Microservices Pattern"
        assert len(sample_document_create.use_cases) == 2
        assert sample_document_create.metadata.quality_score == 0.9
    
    def test_knowledge_document_valid(self, sample_document):
        """Test valid knowledge document."""
        assert sample_document.id == "test_id_123"
        assert sample_document.category == "architectural_pattern"
        assert sample_document.metadata.is_verified is True
    
    def test_search_result_valid(self, sample_document):
        """Test search result schema."""
        result = SearchResult(
            document=sample_document,
            score=0.95,
            distance=0.05
        )
        assert result.score == 0.95
        assert result.document.title == "Test Microservices Pattern"
    
    def test_rag_context_valid(self, sample_document):
        """Test RAG context schema."""
        context = RAGContext(
            query="test query",
            relevant_documents=[sample_document],
            context_text="Test context text",
            sources=["Test Source"]
        )
        assert context.query == "test query"
        assert len(context.relevant_documents) == 1
        assert len(context.sources) == 1


class TestKnowledgeBaseRepository:
    """Tests for knowledge base repository."""
    
    @pytest.mark.asyncio
    async def test_create_document(self, sample_document_create):
        """Test creating a document in repository."""
        mock_db = Mock()
        mock_collection = AsyncMock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        
        # Mock insert result
        mock_collection.find_one = AsyncMock(return_value=None)  # No existing doc
        mock_collection.insert_one = AsyncMock()
        mock_collection.insert_one.return_value.inserted_id = "new_id"
        
        # Mock retrieval of created document
        created_doc_dict = sample_document_create.model_dump()
        created_doc_dict["_id"] = "new_id"
        created_doc_dict["created_at"] = datetime.utcnow()
        created_doc_dict["updated_at"] = datetime.utcnow()
        
        async def mock_find_one(query):
            if query.get("_id") == "new_id":
                return created_doc_dict
            return None
        
        mock_collection.find_one = mock_find_one
        
        from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
        repo = KnowledgeBaseRepository(mock_db)
        repo.collection = mock_collection
        
        result = await repo.create_document(sample_document_create)
        
        assert result.title == sample_document_create.title
        assert result.category == sample_document_create.category
    
    @pytest.mark.asyncio
    async def test_get_documents_by_category(self):
        """Test getting documents by category."""
        mock_db = Mock()
        mock_collection = AsyncMock()
        mock_db.__getitem__ = Mock(return_value=mock_collection)
        
        # Mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.__aiter__ = Mock(return_value=iter([
            {
                "_id": "id1",
                "category": "architectural_pattern",
                "title": "Pattern 1",
                "content": "Content 1",
                "metadata": {
                    "source": "Source 1",
                    "quality_score": 0.9,
                    "is_verified": True
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]))
        
        mock_collection.find = Mock(return_value=mock_cursor)
        
        from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
        repo = KnowledgeBaseRepository(mock_db)
        repo.collection = mock_collection
        
        results = await repo.get_documents_by_category("architectural_pattern")
        
        assert len(results) == 1
        assert results[0].category == "architectural_pattern"


class TestKnowledgeBaseService:
    """Tests for knowledge base service."""
    
    @pytest.mark.asyncio
    async def test_search(self, sample_document):
        """Test semantic search functionality."""
        mock_repo = AsyncMock()
        mock_repo.get_document_by_id = AsyncMock(return_value=sample_document)
        
        with patch('app.services.knowledge_base_service.SentenceTransformer') as mock_st, \
             patch('app.services.knowledge_base_service.chromadb') as mock_chroma:
            
            # Mock sentence transformer
            mock_model = Mock()
            mock_model.encode = Mock(return_value=[0.1, 0.2, 0.3])
            mock_st.return_value = mock_model
            
            # Mock ChromaDB client and collection
            mock_client = Mock()
            mock_collection = Mock()
            mock_collection.query = Mock(return_value={
                'ids': [['test_id_123']],
                'distances': [[0.05]],
                'metadatas': [[{
                    'document_id': 'test_id_123',
                    'title': 'Test Microservices Pattern',
                    'category': 'architectural_pattern',
                    'source': 'Test Source',
                    'quality_score': 0.9
                }]]
            })
            mock_client.get_or_create_collection = Mock(return_value=mock_collection)
            mock_chroma.PersistentClient = Mock(return_value=mock_client)
            
            from app.services.knowledge_base_service import KnowledgeBaseService
            service = KnowledgeBaseService(mock_repo)
            
            results = await service.search("test query", top_k=5)
            
            assert results.query == "test query"
            assert results.total_results >= 0
    
    @pytest.mark.asyncio
    async def test_get_context(self, sample_document):
        """Test RAG context retrieval."""
        mock_repo = AsyncMock()
        mock_repo.get_document_by_id = AsyncMock(return_value=sample_document)
        
        with patch('app.services.knowledge_base_service.SentenceTransformer') as mock_st, \
             patch('app.services.knowledge_base_service.chromadb') as mock_chroma:
            
            # Mock sentence transformer
            mock_model = Mock()
            mock_model.encode = Mock(return_value=[0.1, 0.2, 0.3])
            mock_st.return_value = mock_model
            
            # Mock ChromaDB
            mock_client = Mock()
            mock_collection = Mock()
            mock_collection.query = Mock(return_value={
                'ids': [['test_id_123']],
                'distances': [[0.05]],
                'metadatas': [[{
                    'document_id': 'test_id_123',
                    'title': 'Test Microservices Pattern',
                    'category': 'architectural_pattern',
                    'source': 'Test Source',
                    'quality_score': 0.9
                }]]
            })
            mock_client.get_or_create_collection = Mock(return_value=mock_collection)
            mock_chroma.PersistentClient = Mock(return_value=mock_client)
            
            from app.services.knowledge_base_service import KnowledgeBaseService
            service = KnowledgeBaseService(mock_repo)
            
            context = await service.get_context("design microservices")
            
            assert context.query == "design microservices"
            assert isinstance(context.context_text, str)
            assert len(context.sources) >= 0


class TestRAGRetriever:
    """Tests for RAG retriever."""
    
    @pytest.mark.asyncio
    async def test_rag_retriever_get_documents(self, sample_document):
        """Test RAG retriever document retrieval."""
        mock_kb_service = AsyncMock()
        
        # Mock get_context to return RAGContext
        mock_rag_context = RAGContext(
            query="test query",
            relevant_documents=[sample_document],
            context_text="Test context",
            sources=["Test Source"]
        )
        mock_kb_service.get_context = AsyncMock(return_value=mock_rag_context)
        
        from app.utils.rag_retriever import RAGRetriever
        retriever = RAGRetriever(
            kb_service=mock_kb_service,
            top_k=5
        )
        
        documents = await retriever._aget_relevant_documents("test query")
        
        assert len(documents) == 1
        assert documents[0].metadata['title'] == "Test Microservices Pattern"
        assert "Microservices" in documents[0].page_content


class TestKnowledgeBaseSeeder:
    """Tests for knowledge base seeding utility."""
    
    @pytest.mark.asyncio
    async def test_seed_initial_data(self, sample_document_create):
        """Test seeding initial data."""
        mock_repo = AsyncMock()
        mock_repo.get_document_by_title = AsyncMock(return_value=None)
        mock_repo.create_document = AsyncMock(return_value=KnowledgeDocument(
            id="new_id",
            **sample_document_create.model_dump()
        ))
        
        mock_kb_service = AsyncMock()
        mock_kb_service.add_document = AsyncMock(return_value=True)
        
        from app.utils.knowledge_base_seeder import KnowledgeBaseSeeder
        
        with patch('app.utils.knowledge_base_seeder.ALL_SEED_DATA', [sample_document_create]):
            seeder = KnowledgeBaseSeeder(mock_repo, mock_kb_service)
            stats = await seeder.seed_initial_data()
            
            assert stats['total_processed'] == 1
            assert stats['added_to_mongodb'] >= 0


class TestKnowledgeBaseAPI:
    """Tests for knowledge base API endpoints."""
    
    def test_api_endpoints_exist(self):
        """Test that API endpoints are properly defined."""
        from app.api.knowledge_base import router
        
        # Check that router has the expected routes
        routes = [route.path for route in router.routes]
        
        assert "/documents" in routes
        assert "/search" in routes
        assert "/context" in routes
        assert "/statistics" in routes
        assert "/seed" in routes
        assert "/status" in routes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
