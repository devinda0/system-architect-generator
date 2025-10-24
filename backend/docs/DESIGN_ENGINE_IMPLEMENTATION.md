# Design Engine Implementation

## Overview

The **Design Engine** is the core AI-powered component of the System Architect Generator. It uses specialized LangChain chains to generate, analyze, and refactor software architecture designs based on the C4 model.

## Architecture

### Design Pattern: Specialized Chains with LCEL

Each design task is handled by a specialized chain built using **LangChain Expression Language (LCEL)**. The chains follow this pattern:

```
Input → RAG Context Retrieval → Prompt → LLM → Output Parser → Structured JSON
```

### Components

#### 1. Design Engine Service (`DesignEngineService`)

The central orchestrator that owns and manages all specialized chains.

**Location**: `app/services/design_engine_service.py`

**Chains**:
- `initial_generation_chain`: Creates SystemContext and Containers
- `tech_suggestion_chain`: Recommends technology stacks
- `decomposition_chain`: Breaks down containers into components
- `api_suggestion_chain`: Designs API endpoints
- `refactor_chain`: Refactors elements based on feedback

#### 2. Base Chain (`BaseDesignChain`)

Abstract base class providing common functionality for all chains.

**Location**: `app/chains/base_chain.py`

**Features**:
- LLM initialization (ChatGoogleGenerativeAI)
- RAG retriever integration
- JSON output parsing
- Async/sync invocation methods
- Context retrieval helper

## API Endpoints

All chains are exposed via REST API:

- `POST /api/design/generate-initial` - Generate initial design
- `POST /api/design/suggest-technology` - Suggest technology
- `POST /api/design/decompose-container` - Decompose container
- `POST /api/design/suggest-api` - Suggest API endpoints
- `POST /api/design/refactor` - Refactor element
- `GET /api/design/info` - Get engine information

## Testing

Run tests with:
```bash
pytest app/tests/test_design_engine.py -v
```

## Dependencies

All required dependencies are already in `requirements.txt`:
- langchain==0.3.13
- langchain-core==0.3.27
- langchain-google-genai==2.0.8

No additional installations needed!
