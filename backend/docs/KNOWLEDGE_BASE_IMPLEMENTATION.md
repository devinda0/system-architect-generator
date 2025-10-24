# Architecture Knowledge Base with RAG Implementation

## Overview

This implementation provides a comprehensive **Architecture Knowledge Base** with **Retrieval-Augmented Generation (RAG)** capabilities for the System Architect Generator. It combines a vector database (ChromaDB) for semantic search with MongoDB for structured metadata, enabling the AI to ground its architectural recommendations in proven engineering principles.

## Architecture

### Components

1. **Vector Database (ChromaDB)**
   - Stores document embeddings for semantic similarity search
   - Uses sentence-transformers for high-quality embeddings
   - Enables fast retrieval of relevant architectural knowledge

2. **MongoDB Repository**
   - Manages structured document metadata
   - Provides CRUD operations for knowledge documents
   - Handles categorization, tagging, and versioning

3. **Knowledge Base Service**
   - Orchestrates hybrid search across vector and metadata stores
   - Formats retrieved context for LLM prompting
   - Manages document synchronization

4. **RAG Retriever**
   - LangChain-compatible retriever interface
   - Integrates seamlessly with LangChain chains
   - Supports single and multi-category retrieval

## Knowledge Base Structure

### Document Categories

- **Architectural Patterns**: Microservices, Event-Driven, Monolithic, Serverless, etc.
- **Technologies**: FastAPI, Next.js, PostgreSQL, MongoDB, etc.
- **Design Principles**: SOLID, DRY, Separation of Concerns, etc.
- **Best Practices**: API Design, Security (OWASP), Database Indexing, Error Handling, etc.

### Document Schema

Each knowledge document contains:
```python
{
    "id": "unique_identifier",
    "category": "architectural_pattern | technology | design_principle | best_practice",
    "title": "Document Title",
    "content": "Main description/content",
    "use_cases": ["Use case 1", "Use case 2"],
    "advantages": ["Advantage 1", "Advantage 2"],
    "disadvantages": ["Disadvantage 1"],
    "implementation_notes": "Implementation details",
    "tech_stack_compatibility": ["Tech 1", "Tech 2"],
    "related_patterns": ["Pattern 1", "Pattern 2"],
    "metadata": {
        "source": "Source reference",
        "author": "Author name",
        "url": "Reference URL",
        "tags": ["tag1", "tag2"],
        "quality_score": 0.95,
        "is_verified": true
    }
}
```

## Setup and Configuration

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `chromadb==0.5.23` - Vector database
- `langchain-chroma==0.1.4` - LangChain ChromaDB integration
- `sentence-transformers==3.3.1` - Embedding model

### 2. Environment Configuration

Create or update `.env` file:

```bash
# ChromaDB Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION_NAME=architecture_knowledge
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
DEFAULT_TOP_K=5
SIMILARITY_THRESHOLD=0.7
CHROMA_CLIENT_MODE=persistent  # or 'http' for server mode

# MongoDB Configuration (existing)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=system_architect_db
```

### 3. Initialize Knowledge Base

#### Option A: Using API Endpoint

```bash
# Start the server
python -m app.main

# Seed the knowledge base
curl -X POST "http://localhost:8000/api/knowledge-base/seed"
```

#### Option B: Using Python Script

```python
from app.config.mongodb_config import get_database
from app.utils.knowledge_base_seeder import seed_knowledge_base
import asyncio

async def main():
    db = await get_database()
    stats = await seed_knowledge_base(db, force_update=False)
    print(f"Seeding completed: {stats}")

asyncio.run(main())
```

## Usage

### 1. API Endpoints

#### Create a Knowledge Document

```bash
POST /api/knowledge-base/documents
Content-Type: application/json

{
    "category": "architectural_pattern",
    "title": "CQRS Pattern",
    "content": "Command Query Responsibility Segregation...",
    "use_cases": ["Event-sourced systems", "High-read applications"],
    "advantages": ["Scalability", "Optimized queries"],
    "disadvantages": ["Complexity", "Eventual consistency"],
    "metadata": {
        "source": "Martin Fowler Blog",
        "tags": ["architecture", "patterns"],
        "quality_score": 0.9,
        "is_verified": true
    }
}
```

#### Search Knowledge Base

```bash
GET /api/knowledge-base/search?query=scalable+microservices&top_k=5
```

Response:
```json
{
    "query": "scalable microservices",
    "results": [
        {
            "document": {...},
            "score": 0.92,
            "distance": 0.08
        }
    ],
    "total_results": 5,
    "top_k": 5
}
```

#### Get RAG Context

```bash
GET /api/knowledge-base/context?query=design+event+driven+system&top_k=3
```

Response:
```json
{
    "query": "design event driven system",
    "relevant_documents": [...],
    "context_text": "Based on the Architecture Knowledge Base:\n\n1. Event-Driven Architecture...",
    "sources": ["AWS Architecture Center", "Martin Fowler Blog"]
}
```

### 2. Using RAG in LangChain

#### Basic RAG Chain

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from app.utils.rag_retriever import RAGRetriever
from app.services.knowledge_base_service import KnowledgeBaseService
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository

# Initialize components
repository = KnowledgeBaseRepository(database)
kb_service = KnowledgeBaseService(repository)
retriever = RAGRetriever(kb_service=kb_service, top_k=5)

# Create prompt template with RAG context
template = """You are an expert software architect. Use the following knowledge base context to answer the question.

Context from Knowledge Base:
{context}

Question: {question}

Provide a detailed architectural recommendation based on the context above."""

prompt = ChatPromptTemplate.from_template(template)

# Create LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro")

# Build RAG chain
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

combine_docs_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

# Use the chain
response = await rag_chain.ainvoke({
    "input": "How should I design a scalable e-commerce platform?"
})

print(response["answer"])
```

#### Multi-Category RAG Retriever

```python
from app.utils.rag_retriever import MultiCategoryRAGRetriever

# Retrieve from multiple categories
retriever = MultiCategoryRAGRetriever(
    kb_service=kb_service,
    categories=[
        "architectural_pattern",
        "technology",
        "best_practice"
    ],
    top_k_per_category=2
)

# Use in chain (same as above)
```

### 3. Direct Service Usage

```python
# Search for relevant documents
results = await kb_service.search(
    query="microservices communication patterns",
    top_k=5,
    category_filter="architectural_pattern"
)

for result in results.results:
    print(f"Title: {result.document.title}")
    print(f"Score: {result.score}")
    print(f"Content: {result.document.content[:200]}...")
    print("---")

# Get formatted RAG context
context = await kb_service.get_context(
    query="implement authentication in microservices",
    top_k=3
)

print(context.context_text)
# Use this in your prompt to the LLM
```

## Data Management

### Adding New Knowledge

```python
from app.schemas.knowledge_base import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentMetadata
)

# Create new knowledge document
new_doc = KnowledgeDocumentCreate(
    category="best_practice",
    title="API Rate Limiting",
    content="Rate limiting is essential for protecting APIs...",
    use_cases=["Public APIs", "Microservices"],
    advantages=["Prevents abuse", "Ensures fair usage"],
    implementation_notes="Use token bucket or sliding window",
    metadata=KnowledgeDocumentMetadata(
        source="API Design Best Practices",
        tags=["api", "security", "rate-limiting"],
        quality_score=0.88,
        is_verified=True
    )
)

# Add to knowledge base
created_doc = await repository.create_document(new_doc)
await kb_service.add_document(created_doc)
```

### Updating Knowledge

```python
from app.schemas.knowledge_base import KnowledgeDocumentUpdate

# Update existing document
update = KnowledgeDocumentUpdate(
    content="Updated content with new information...",
    advantages=["New advantage 1", "New advantage 2"]
)

updated_doc = await repository.update_document(document_id, update)
await kb_service.add_document(updated_doc, force_update=True)
```

### Bulk Operations

```python
# Bulk add documents
docs = [doc1, doc2, doc3]
stats = await kb_service.bulk_add_documents(docs)
print(f"Added: {stats['added']}, Failed: {stats['failed']}")
```

## Monitoring and Statistics

### Get Knowledge Base Status

```bash
GET /api/knowledge-base/status
```

Response:
```json
{
    "mongodb": {
        "total_documents": 150,
        "by_category": {
            "architectural_pattern": 45,
            "technology": 60,
            "design_principle": 25,
            "best_practice": 20
        },
        "verified_documents": 120,
        "average_quality_score": 0.87
    },
    "vector_db": {
        "collection_name": "architecture_knowledge",
        "total_embeddings": 150,
        "embedding_model": "all-MiniLM-L6-v2"
    },
    "sync_status": {
        "in_sync": true,
        "mongodb_count": 150,
        "vector_db_count": 150
    }
}
```

### Statistics Endpoint

```bash
GET /api/knowledge-base/statistics
```

## Best Practices

### 1. Document Quality

- **Verify Sources**: Always set `is_verified=True` only for well-researched content
- **Quality Scores**: Assign higher scores (0.9+) to authoritative sources
- **Keep Updated**: Regularly review and update documents with new information
- **Tag Appropriately**: Use consistent, meaningful tags for better categorization

### 2. Search Optimization

- **Specific Queries**: More specific queries yield better results
- **Category Filtering**: Use category filters when you know the domain
- **Adjust top_k**: Start with 3-5 results, increase if needed
- **Monitor Scores**: Similarity scores below 0.7 may not be relevant

### 3. RAG Integration

- **Context Length**: Don't retrieve too many documents (5-7 is optimal)
- **Format Context**: Use structured formatting for better LLM understanding
- **Include Sources**: Always include source attribution in responses
- **Combine Strategies**: Mix semantic search with keyword filtering

### 4. Performance

- **Use Persistent Mode**: For development, use persistent ChromaDB
- **Batch Operations**: Use bulk operations for adding multiple documents
- **Cache Results**: Cache frequently accessed knowledge
- **Monitor Latency**: Track search and retrieval times

## Testing

Run the test suite:

```bash
# Run all knowledge base tests
pytest app/tests/test_knowledge_base.py -v

# Run with coverage
pytest app/tests/test_knowledge_base.py --cov=app.services.knowledge_base_service --cov=app.repositories.knowledge_base_repository --cov-report=html
```

## Troubleshooting

### ChromaDB Connection Issues

```python
# Check if ChromaDB is accessible
from app.services.knowledge_base_service import KnowledgeBaseService

try:
    service = KnowledgeBaseService(repository)
    stats = service.get_collection_stats()
    print(f"ChromaDB is working: {stats}")
except Exception as e:
    print(f"ChromaDB error: {e}")
```

### Sync Issues

If MongoDB and ChromaDB are out of sync:

```python
# Re-sync all documents
documents = await repository.get_all_documents(limit=1000)
stats = await kb_service.bulk_add_documents(documents)
```

### Embedding Model Issues

If the embedding model fails to load:

```bash
# Download model manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

## Future Enhancements

1. **Advanced Search**
   - Hybrid search combining semantic and keyword search
   - Filters by date, quality score, verification status
   - Fuzzy matching for typos

2. **Knowledge Curation**
   - Automated quality assessment
   - Duplicate detection
   - Automatic tagging using NLP

3. **Multi-modal Support**
   - Support for diagrams and images
   - Code snippet indexing
   - Video content integration

4. **Analytics**
   - Track most queried topics
   - Monitor search effectiveness
   - Identify knowledge gaps

## References

- [LangChain RAG Documentation](https://python.langchain.com/docs/use_cases/question_answering/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [System Architecture Documentation](../docs/system_architecture.md)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the test cases for usage examples
3. Consult the API documentation at `/docs` (Swagger UI)
