# Quick Start Guide - Knowledge Base with RAG

This guide will help you quickly set up and start using the Architecture Knowledge Base with RAG capabilities.

## Prerequisites

- Python 3.9+
- MongoDB running locally or accessible via connection string
- Git (to clone the repository)

## 5-Minute Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the `backend` directory:

```env
# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=system_architect_db

# ChromaDB (Vector Database)
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=architecture_knowledge
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 3. Start the Application

```bash
python -m app.main
```

The server will start on `http://localhost:8000`

### 4. Seed the Knowledge Base

Open a new terminal and run:

```bash
curl -X POST "http://localhost:8000/api/knowledge-base/seed"
```

Or visit the Swagger UI at `http://localhost:8000/docs` and use the `/api/knowledge-base/seed` endpoint.

This will populate the knowledge base with:
- 4 Architectural Patterns (Microservices, Event-Driven, Monolithic, Serverless)
- 4 Technologies (FastAPI, Next.js, PostgreSQL, MongoDB)
- 3 Design Principles (SOLID, DRY, Separation of Concerns)
- 4 Best Practices (API Design, Security, Database Indexing, Error Handling)

## Quick Examples

### Example 1: Search for Architectural Patterns

```bash
curl "http://localhost:8000/api/knowledge-base/search?query=scalable+microservices&top_k=3"
```

### Example 2: Get RAG Context for Prompt

```bash
curl "http://localhost:8000/api/knowledge-base/context?query=design+event+driven+system"
```

The response will contain formatted context that you can inject into your LLM prompts.

### Example 3: Using RAG with Gemini

```python
from app.utils.rag_retriever import RAGRetriever
from app.services.knowledge_base_service import KnowledgeBaseService
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.config.mongodb_config import get_database
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Initialize
db = get_database()
repository = KnowledgeBaseRepository(db)
kb_service = KnowledgeBaseService(repository)

# Get RAG context
context = await kb_service.get_context(
    query="How to design a scalable e-commerce platform?",
    top_k=5
)

# Create prompt with context
prompt = ChatPromptTemplate.from_template("""
You are an expert software architect. Use the following knowledge base context 
to provide architectural recommendations.

Knowledge Base Context:
{context}

User Question: {question}

Provide a comprehensive architectural design with justifications based on the context.
""")

# Create chain
llm = ChatGoogleGenerativeAI(model="gemini-pro")
chain = prompt | llm

# Get response
response = await chain.ainvoke({
    "context": context.context_text,
    "question": "How should I design a scalable e-commerce platform?"
})

print(response.content)
```

## Verify Installation

### Check Knowledge Base Status

```bash
curl "http://localhost:8000/api/knowledge-base/status"
```

Expected response should show:
- Total documents in MongoDB
- Total embeddings in ChromaDB
- Documents by category
- Sync status

### Check API Health

```bash
curl "http://localhost:8000/api/health"
```

## Explore the API

Visit `http://localhost:8000/docs` to explore all available endpoints:

- **POST /api/knowledge-base/documents** - Create new knowledge documents
- **GET /api/knowledge-base/documents** - List all documents
- **GET /api/knowledge-base/search** - Semantic search
- **GET /api/knowledge-base/context** - Get RAG context
- **GET /api/knowledge-base/statistics** - Get statistics

## Common Tasks

### Add a New Knowledge Document

```bash
curl -X POST "http://localhost:8000/api/knowledge-base/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "best_practice",
    "title": "API Versioning",
    "content": "API versioning is crucial for maintaining backward compatibility...",
    "use_cases": ["Public APIs", "Long-lived applications"],
    "advantages": ["Backward compatibility", "Gradual migration"],
    "metadata": {
      "source": "API Design Guidelines",
      "tags": ["api", "versioning"],
      "quality_score": 0.9,
      "is_verified": true
    }
  }'
```

### Search by Category

```bash
curl "http://localhost:8000/api/knowledge-base/documents?category=architectural_pattern&limit=10"
```

### Get Statistics

```bash
curl "http://localhost:8000/api/knowledge-base/statistics"
```

## Next Steps

1. **Read the Full Documentation**: See [KNOWLEDGE_BASE_IMPLEMENTATION.md](./KNOWLEDGE_BASE_IMPLEMENTATION.md)
2. **Add Custom Knowledge**: Add your organization's architectural patterns and standards
3. **Integrate with Gemini**: Use the RAG retriever in your LangChain chains
4. **Explore Examples**: Check the test files for more usage examples

## Troubleshooting

### ChromaDB Directory Issues

If you encounter permissions issues with the ChromaDB directory:

```bash
mkdir -p ./chroma_db
chmod 755 ./chroma_db
```

### MongoDB Connection Issues

Ensure MongoDB is running:

```bash
# Check if MongoDB is running
mongosh --eval "db.adminCommand('ping')"
```

### Missing Dependencies

If you get import errors:

```bash
pip install --upgrade -r requirements.txt
```

### Clear and Reseed

To start fresh:

```bash
# This will clear existing data and reseed
curl -X POST "http://localhost:8000/api/knowledge-base/seed?force_update=true"
```

## Support

For detailed information, see:
- [Full Implementation Guide](./KNOWLEDGE_BASE_IMPLEMENTATION.md)
- [System Architecture](./system_architecture.md)
- [API Documentation](http://localhost:8000/docs)

Happy coding! 🚀
