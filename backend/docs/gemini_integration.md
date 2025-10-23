# Google Gemini API Integration

This document describes the Google Gemini API integration with LangChain for the System Architect Generator.

## Features

✅ **Implemented Features:**

- ✅ Google Gemini API credentials configuration via environment variables
- ✅ ChatGemini LangChain wrapper implementation
- ✅ Support for Gemini Pro model
- ✅ Support for Gemini Flash model
- ✅ Secure API key management with validation
- ✅ Comprehensive error handling with custom exception classes
- ✅ Exponential backoff retry logic with jitter
- ✅ Rate limiting support
- ✅ Request timeout configuration
- ✅ Streaming response support
- ✅ Batch processing capabilities
- ✅ Model switching (Pro ↔ Flash)
- ✅ Pydantic Settings for configuration management
- ✅ REST API endpoints
- ✅ Health check endpoint
- ✅ Comprehensive logging

## Architecture

### Folder Structure

```
app/
├── api/
│   ├── gemini.py           # REST API endpoints for Gemini
│   ├── health.py           # Health check endpoints
│   └── user.py             # User management endpoints
├── config/
│   ├── gemini_config.py    # Gemini configuration (Pydantic Settings)
│   └── logging_config.py   # Logging configuration
├── exceptions/
│   ├── __init__.py
│   └── gemini_exceptions.py # Custom exception classes
├── services/
│   ├── __init__.py
│   └── gemini_service.py   # Gemini service implementation
└── utils/
    ├── api_key_manager.py  # API key management
    └── retry_handler.py    # Retry logic with exponential backoff
```

## Configuration

### 1. Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required configuration:
```env
GOOGLE_API_KEY=your_actual_api_key_here
```

Optional configurations:
```env
DEFAULT_MODEL=gemini-1.5-flash
TEMPERATURE_DEFAULT=0.7
MAX_TOKENS_DEFAULT=2048
REQUEST_TIMEOUT_SECONDS=30
MAX_RETRIES=3
```

### 2. Get Google Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key and add it to your `.env` file

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

```bash
# Development mode with auto-reload
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### API Endpoints

#### Health Check
```bash
GET /api/gemini/health
```

Response:
```json
{
  "status": "healthy",
  "api_key_configured": true,
  "config_valid": true,
  "message": "Gemini API is configured and ready"
}
```

#### Generate Text (Default Model)
```bash
POST /api/gemini/generate
```

Request:
```json
{
  "prompt": "Explain microservices architecture",
  "system_prompt": "You are a software architect expert",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

Response:
```json
{
  "content": "Generated text here...",
  "model": "gemini-1.5-flash",
  "success": true
}
```

#### Generate with Flash Model
```bash
POST /api/gemini/generate/flash
```

#### Generate with Pro Model
```bash
POST /api/gemini/generate/pro
```

#### Batch Generation
```bash
POST /api/gemini/batch
```

Request:
```json
{
  "prompts": [
    "What is REST API?",
    "What is GraphQL?",
    "What is gRPC?"
  ],
  "system_prompt": "Explain in one sentence"
}
```

#### Get Available Models
```bash
GET /api/gemini/models/available
```

#### Get Current Model Info
```bash
GET /api/gemini/models/current
```

### Python API Usage

#### Basic Usage

```python
from app.services import get_gemini_service

# Get service instance
service = get_gemini_service()

# Generate text
response = service.generate(
    prompt="Explain REST API",
    system_prompt="You are a technical expert"
)
print(response)
```

#### Using Flash Model

```python
from app.services import get_gemini_flash_service

service = get_gemini_flash_service()
response = service.generate("Explain microservices")
```

#### Using Pro Model

```python
from app.services import get_gemini_pro_service

service = get_gemini_pro_service()
response = service.generate("Design a scalable system")
```

#### Streaming Responses

```python
service = get_gemini_service()

for chunk in service.generate_streaming("Tell me a story"):
    print(chunk, end="", flush=True)
```

#### Batch Processing

```python
service = get_gemini_service()

prompts = [
    "What is Docker?",
    "What is Kubernetes?",
    "What is Terraform?"
]

responses = service.batch_generate(prompts)
for i, response in enumerate(responses):
    print(f"Q{i+1}: {response}\n")
```

#### Model Switching

```python
service = get_gemini_service()

# Switch to Flash
service.switch_to_flash()

# Switch to Pro
service.switch_to_pro()

# Change with parameters
service.change_model("gemini-pro", temperature=0.9, max_tokens=4096)
```

## Error Handling

The integration includes comprehensive error handling:

### Exception Hierarchy

```
GeminiError (base)
├── GeminiConfigError      # Configuration issues
├── GeminiAPIError         # General API errors
│   ├── GeminiRateLimitError      # Rate limit (429)
│   ├── GeminiTimeoutError        # Request timeout
│   ├── GeminiAuthenticationError # Auth failed (401/403)
│   └── GeminiInvalidRequestError # Invalid request (400)
```

### Handling Errors

```python
from app.exceptions import (
    GeminiError,
    GeminiRateLimitError,
    GeminiTimeoutError,
    GeminiAuthenticationError,
)

try:
    service = get_gemini_service()
    response = service.generate("Test prompt")
except GeminiRateLimitError as e:
    print("Rate limit exceeded, wait and retry")
except GeminiTimeoutError as e:
    print("Request timed out")
except GeminiAuthenticationError as e:
    print("Check your API key")
except GeminiError as e:
    print(f"Gemini error: {e}")
```

## Retry Logic

Automatic retry with exponential backoff:

- **Max Retries:** 3 (configurable)
- **Initial Delay:** 1 second
- **Backoff Factor:** 2.0 (doubles each retry)
- **Max Wait:** 60 seconds
- **Jitter:** Enabled (adds randomness to prevent thundering herd)

Retryable errors:
- Rate limit errors (429)
- Server errors (500, 502, 503, 504)
- Timeout errors
- Connection errors

## Logging

Comprehensive logging is implemented:

```python
import logging

# Get logger
logger = logging.getLogger(__name__)

# Log levels are configured in app/config/logging_config.py
# Default level: INFO
# Can be changed via LOG_LEVEL environment variable
```

## Testing

Run tests:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_gemini_service.py
```

## Best Practices

### 1. Configuration Management
- ✅ Use Pydantic Settings for type-safe configuration
- ✅ Environment variables for sensitive data
- ✅ Validation on startup

### 2. Error Handling
- ✅ Specific exception classes for different error types
- ✅ Proper HTTP status codes in API
- ✅ Detailed error messages for debugging

### 3. Security
- ✅ API keys stored in environment variables
- ✅ Never commit `.env` file
- ✅ API key validation on startup

### 4. Performance
- ✅ Singleton pattern for service instances
- ✅ Connection pooling via LangChain
- ✅ Retry logic with backoff
- ✅ Rate limiting awareness

### 5. Code Organization
- ✅ Separation of concerns (config, service, API, utils)
- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Consistent naming conventions

## Troubleshooting

### API Key Not Configured
```
Error: GOOGLE_API_KEY environment variable is not set
Solution: Add GOOGLE_API_KEY to .env file
```

### Rate Limit Exceeded
```
Error: GeminiRateLimitError: Rate limit exceeded
Solution: Wait before retrying, or upgrade your quota
```

### Authentication Failed
```
Error: GeminiAuthenticationError: Authentication failed
Solution: Verify your API key is correct
```

### Import Errors
```
Error: ModuleNotFoundError: No module named 'pydantic_settings'
Solution: pip install -r requirements.txt
```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify API key configuration
3. Check Google AI Studio for API quota
4. Review error messages in the response

## References

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [LangChain Google GenAI Integration](https://python.langchain.com/docs/integrations/platforms/google)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
