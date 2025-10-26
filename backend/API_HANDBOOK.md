# System Architect Generator - API Handbook

A comprehensive guide to the System Architect Generator Backend API

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL & Headers](#base-url--headers)
4. [Error Handling](#error-handling)
5. [API Endpoints](#api-endpoints)
   - [Health Check](#health-check)
   - [Authentication](#authentication-endpoints)
   - [User Management](#user-management)  
   - [Project Management](#project-management)
   - [Design Engine](#design-engine)
   - [Gemini AI Integration](#gemini-ai-integration)
   - [Knowledge Base](#knowledge-base)
6. [Data Models](#data-models)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)
9. [Development Setup](#development-setup)

---

## Overview

The System Architect Generator Backend is a FastAPI-based REST API that provides intelligent system architecture generation using Google Gemini AI integration. The API supports user management, project creation, AI-powered design generation, and knowledge base management.

**Key Features:**
- JWT-based authentication
- AI-powered architecture generation via Google Gemini
- Project and design management
- Vector-based knowledge base with RAG capabilities
- MongoDB for data persistence
- Comprehensive error handling and logging

---

## Authentication

The API uses JWT (JSON Web Token) based authentication with Bearer tokens.

### Authentication Flow
1. Register a new user or login with existing credentials
2. Receive an access token in the response
3. Include the token in subsequent requests via the `Authorization` header

### Token Format
```
Authorization: Bearer <your_access_token>
```

### Token Expiration
- Access tokens expire after 30 minutes (1800 seconds)
- Currently no refresh token mechanism (logout is client-side)

---

## Base URL & Headers

### Base URL
```
http://localhost:8000
```

### Common Headers
```
Content-Type: application/json
Authorization: Bearer <token>  # Required for protected endpoints
```

### CORS Configuration
- All origins allowed in development (`allow_origins=["*"]`)
- All methods and headers permitted
- Credentials supported

---

## Error Handling

The API returns structured error responses with appropriate HTTP status codes.

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Validation Error
- `429` - Too Many Requests
- `500` - Internal Server Error

### Gemini-Specific Error Codes
- `429` - Rate limit exceeded
- `401` - Authentication error with Gemini API
- `500` - Gemini API error or timeout

---

## API Endpoints

### Health Check

#### GET `/health`
Simple health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "Server is running"
}
```

#### GET `/api/health`
Comprehensive health check including database status.

**Response:**
```json
{
  "status": "ok",
  "database": {
    "status": "connected",
    "message": "MongoDB is healthy"
  }
}
```

---

### Authentication Endpoints

#### POST `/api/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string (optional)",
  "profile": {} // optional object
}
```

**Response (201):**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "is_active": true,
  "created_at": "2023-10-26T10:00:00Z",
  "updated_at": "2023-10-26T10:00:00Z",
  "profile": {}
}
```

**Errors:**
- `409` - Email already registered or username taken
- `422` - Validation errors

#### POST `/api/auth/login`
Authenticate user and receive access token.

**Request Body (Form Data):**
```
username: string  // username or email
password: string
```

**Response:**
```json
{
  "user": {
    "id": "string",
    "username": "string",
    "email": "string",
    "full_name": "string",
    "is_active": true,
    "created_at": "2023-10-26T10:00:00Z",
    "updated_at": "2023-10-26T10:00:00Z",
    "profile": {}
  },
  "tokens": {
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

**Errors:**
- `401` - Invalid credentials or disabled account

#### POST `/api/auth/logout`
Logout current user (client-side token removal).

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

#### GET `/api/auth/me`
Get current authenticated user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "is_active": true,
  "created_at": "2023-10-26T10:00:00Z",
  "updated_at": "2023-10-26T10:00:00Z",
  "profile": {}
}
```

#### PUT `/api/auth/me`
Update current user information.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "username": "string (optional)",
  "email": "string (optional)",
  "full_name": "string (optional)",
  "profile": {} // optional
}
```

**Response:** Updated user object (same format as GET `/api/auth/me`)

---

### User Management

*Note: This is a simplified user management endpoint with in-memory storage*

#### POST `/api/users`
Create a new user (simplified version).

**Request Body:**
```json
{
  "username": "string",
  "email": "string"
}
```

#### GET `/api/users`
Get all users.

**Response:**
```json
[
  {
    "id": 1,
    "username": "string",
    "email": "string"
  }
]
```

#### GET `/api/users/{user_id}`
Get user by ID.

#### PUT `/api/users/{user_id}`
Update user information.

#### DELETE `/api/users/{user_id}`
Delete a user.

---

### Project Management

#### POST `/api/projects`
Create a new project.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "string",
  "description": "string (optional)",
  "tags": ["string"],
  "metadata": {}
}
```

**Response (201):**
```json
{
  "id": "string",
  "user_id": "string",
  "name": "string",
  "description": "string",
  "tags": ["string"],
  "status": "active",
  "metadata": {},
  "design_count": 0,
  "created_at": "2023-10-26T10:00:00Z",
  "updated_at": "2023-10-26T10:00:00Z"
}
```

#### GET `/api/projects`
Get user's projects with pagination and filtering.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip`: number (default: 0)
- `limit`: number (default: 10, max: 100)
- `tags`: string (comma-separated)
- `status`: string

#### GET `/api/projects/{project_id}`
Get project details.

#### PUT `/api/projects/{project_id}`
Update project information.

#### DELETE `/api/projects/{project_id}`
Delete a project.

---

### Design Engine

The Design Engine provides AI-powered architecture generation capabilities.

#### POST `/api/designs/generate-initial`
Generate initial system architecture from requirements.

**Request Body:**
```json
{
  "requirements": "string"  // User requirements description
}
```

**Response:**
```json
{
  "system_context": {
    "id": "string",
    "name": "string",
    "description": "string",
    "external_systems": [],
    "actors": []
  },
  "containers": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "technology": "string",
      "responsibilities": ["string"]
    }
  ],
  "relationships": [],
  "design_rationale": "string"
}
```

#### POST `/api/designs/suggest-technologies`
Get technology recommendations for components.

**Request Body:**
```json
{
  "component_description": "string",
  "requirements": "string",
  "constraints": ["string"]
}
```

#### POST `/api/designs/decompose`
Decompose containers into components.

**Request Body:**
```json
{
  "container_id": "string",
  "container_description": "string",
  "requirements": "string"
}
```

#### POST `/api/designs/suggest-apis`
Generate API recommendations for components.

**Request Body:**
```json
{
  "component_description": "string",
  "interactions": ["string"],
  "requirements": "string"
}
```

#### POST `/api/designs/refactor`
Refactor existing design based on feedback.

**Request Body:**
```json
{
  "current_design": {},
  "feedback": "string",
  "requirements": "string"
}
```

---

### Gemini AI Integration

Direct access to Google Gemini AI capabilities.

#### POST `/api/gemini/generate`
Generate text using Gemini models.

**Request Body:**
```json
{
  "prompt": "string",
  "system_prompt": "string (optional)",
  "model": "gemini-pro | gemini-1.5-flash (optional)",
  "temperature": 0.7, // 0.0-1.0 (optional)
  "max_tokens": 2048  // optional
}
```

**Response:**
```json
{
  "content": "string",
  "model": "string",
  "success": true
}
```

#### POST `/api/gemini/batch-generate`
Generate multiple responses in batch.

**Request Body:**
```json
{
  "prompts": ["string"],
  "system_prompt": "string (optional)",
  "model": "string (optional)"
}
```

**Response:**
```json
{
  "responses": ["string"],
  "model": "string",
  "success": true
}
```

#### GET `/api/gemini/models`
Get available Gemini models and their configurations.

#### GET `/api/gemini/health`
Check Gemini API health and configuration.

**Response:**
```json
{
  "status": "healthy",
  "api_key_configured": true,
  "config_valid": true,
  "message": "Gemini API is ready"
}
```

---

### Knowledge Base

Vector-based knowledge base with RAG (Retrieval-Augmented Generation) capabilities.

#### POST `/api/knowledge-base/documents`
Create a new knowledge document.

**Request Body:**
```json
{
  "title": "string",
  "content": "string",
  "category": "string",
  "tags": ["string"],
  "metadata": {},
  "source_url": "string (optional)"
}
```

**Response (201):**
```json
{
  "id": "string",
  "title": "string",
  "content": "string",
  "category": "string",
  "tags": ["string"],
  "metadata": {},
  "source_url": "string",
  "created_at": "2023-10-26T10:00:00Z",
  "updated_at": "2023-10-26T10:00:00Z"
}
```

#### GET `/api/knowledge-base/documents/{document_id}`
Get document by ID.

#### GET `/api/knowledge-base/documents`
List documents with filtering and pagination.

**Query Parameters:**
- `category`: string
- `tags`: string (comma-separated)
- `skip`: number
- `limit`: number

#### POST `/api/knowledge-base/search`
Semantic search in knowledge base.

**Request Body:**
```json
{
  "query": "string",
  "categories": ["string"],
  "limit": 10,
  "similarity_threshold": 0.7
}
```

**Response:**
```json
{
  "results": [
    {
      "document": {
        "id": "string",
        "title": "string",
        "content": "string",
        "category": "string"
      },
      "similarity_score": 0.85,
      "relevant_chunks": ["string"]
    }
  ],
  "total_results": 5,
  "query_embedding_time": 0.123
}
```

#### POST `/api/knowledge-base/rag-query`
RAG-enhanced query with context.

**Request Body:**
```json
{
  "query": "string",
  "context_limit": 5,
  "include_sources": true
}
```

#### GET `/api/knowledge-base/stats`
Get knowledge base statistics.

#### POST `/api/knowledge-base/seed`
Seed knowledge base with default documents.

---

## Data Models

### User Models

```typescript
interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  profile?: object;
}

interface UserCreate {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  profile?: object;
}

interface UserUpdate {
  username?: string;
  email?: string;
  full_name?: string;
  profile?: object;
}
```

### Project Models

```typescript
interface Project {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  tags: string[];
  status: 'active' | 'archived' | 'deleted';
  metadata: object;
  design_count: number;
  created_at: string;
  updated_at: string;
}

interface ProjectCreateRequest {
  name: string;
  description?: string;
  tags: string[];
  metadata?: object;
}
```

### Design Models

```typescript
interface SystemContext {
  id: string;
  name: string;
  description: string;
  external_systems: ExternalSystem[];
  actors: Actor[];
}

interface Container {
  id: string;
  name: string;
  description: string;
  technology: string;
  responsibilities: string[];
}

interface Component {
  id: string;
  name: string;
  description: string;
  container_id: string;
  responsibilities: string[];
  interfaces: string[];
}
```

### Knowledge Base Models

```typescript
interface KnowledgeDocument {
  id: string;
  title: string;
  content: string;
  category: string;
  tags: string[];
  metadata: object;
  source_url?: string;
  created_at: string;
  updated_at: string;
}

interface SearchResult {
  document: KnowledgeDocument;
  similarity_score: number;
  relevant_chunks: string[];
}
```

---

## Rate Limiting

### Gemini API Limits
- Requests per minute: Varies by model and tier
- Tokens per minute: Model-dependent
- The API includes automatic retry logic with exponential backoff

### General API Limits
- No specific rate limiting implemented on the FastAPI side
- MongoDB connection pooling: 10-100 connections
- Request timeout: 30 seconds default

---

## Examples

### Authentication Flow
```bash
# 1. Register a new user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "architect",
    "email": "architect@example.com",
    "password": "secure123",
    "full_name": "System Architect"
  }'

# 2. Login to get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=architect&password=secure123"

# Response includes access_token
# {
#   "user": {...},
#   "tokens": {
#     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#     "token_type": "bearer",
#     "expires_in": 1800
#   }
# }
```

### Creating a Project
```bash
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "name": "E-commerce Platform",
    "description": "Modern e-commerce system with microservices",
    "tags": ["ecommerce", "microservices", "api"],
    "metadata": {
      "budget": "50000",
      "timeline": "6 months"
    }
  }'
```

### Generating Initial Design
```bash
curl -X POST "http://localhost:8000/api/designs/generate-initial" \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Build a scalable e-commerce platform that handles product catalog, user management, order processing, and payment integration. Must support high traffic and be cloud-native."
  }'
```

### Searching Knowledge Base
```bash
curl -X POST "http://localhost:8000/api/knowledge-base/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "microservices architecture patterns",
    "categories": ["architecture", "patterns"],
    "limit": 5,
    "similarity_threshold": 0.7
  }'
```

### Using Gemini AI
```bash
curl -X POST "http://localhost:8000/api/gemini/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain the benefits of microservices architecture",
    "model": "gemini-1.5-flash",
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

---

## Development Setup

### Prerequisites
- Python 3.8+
- MongoDB 7.0+
- Google Gemini API key

### Installation
```bash
# 1. Clone repository
git clone <repository-url>
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 4. Start services
docker-compose up -d mongodb  # Start MongoDB
python -m app.main            # Start API server
```

### Using Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### API Documentation
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### Testing
```bash
# Run tests
python -m pytest

# Validate setup
python scripts/validate_setup.py

# Check MongoDB connection
python scripts/validate_mongodb.py
```

---

## Configuration

### Environment Variables

```env
# Required
GOOGLE_API_KEY=your_api_key_here

# MongoDB Configuration
MONGODB_URL=mongodb://admin:admin123@localhost:27017/system_architect_generator?authSource=admin
MONGODB_DB_NAME=system_architect_generator
MONGODB_USERNAME=admin
MONGODB_PASSWORD=admin123

# Gemini Configuration
DEFAULT_MODEL=gemini-1.5-flash
TEMPERATURE_DEFAULT=0.7
MAX_TOKENS_DEFAULT=2048
REQUEST_TIMEOUT_SECONDS=30
MAX_RETRIES=3

# JWT Configuration
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ChromaDB (Knowledge Base)
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=architecture_knowledge
```

### Production Considerations
- Use strong `SECRET_KEY` for JWT tokens
- Restrict CORS origins (`allow_origins=["https://yourdomain.com"]`)
- Enable HTTPS
- Configure proper MongoDB authentication
- Set up monitoring and logging
- Implement rate limiting
- Use environment-specific configurations

---

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check if MongoDB is running: `docker-compose ps`
   - Verify connection string in environment variables
   - Check network connectivity

2. **Gemini API Key Error**
   - Verify API key is set: `echo $GOOGLE_API_KEY`
   - Check key validity at https://aistudio.google.com/app/apikey
   - Ensure proper permissions

3. **Authentication Errors**
   - Check JWT token expiration
   - Verify token format: `Bearer <token>`
   - Ensure SECRET_KEY consistency

4. **Import Errors**
   - Check all dependencies installed: `pip install -r requirements.txt`
   - Verify Python path: `python -m app.main`

### Health Checks
```bash
# Check API health
curl http://localhost:8000/health

# Check database health
curl http://localhost:8000/api/health

# Check Gemini health
curl http://localhost:8000/api/gemini/health
```

---

This handbook provides comprehensive documentation for the System Architect Generator Backend API. For the latest updates and additional information, refer to the project's README files and inline code documentation.