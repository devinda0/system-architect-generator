# System Architect Generator - Backend

FastAPI backend with Google Gemini API integration for intelligent system architecture generation.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 3. Validate setup
python scripts/validate_setup.py

# 4. Start server
python -m app.main
```

Visit http://127.0.0.1:8000/docs for API documentation.

## ✅ Features

### Google Gemini API Integration
- ✅ **Multiple Models:** Support for Gemini Pro and Flash models
- ✅ **LangChain Integration:** Built on LangChain for flexibility
- ✅ **API Key Management:** Secure credential handling with validation
- ✅ **Error Handling:** Comprehensive exception hierarchy
- ✅ **Retry Logic:** Exponential backoff with jitter
- ✅ **Streaming Support:** Real-time response streaming
- ✅ **Batch Processing:** Process multiple prompts efficiently
- ✅ **REST API:** Complete REST endpoints for all features

### Best Practices
- ✅ **Type Safety:** Pydantic models throughout
- ✅ **Configuration:** Pydantic Settings with environment variables
- ✅ **Logging:** Structured logging with configurable levels
- ✅ **Testing:** Comprehensive unit tests
- ✅ **Documentation:** Detailed guides and API docs
- ✅ **Security:** Secure API key management
- ✅ **Code Quality:** Proper folder structure and separation of concerns

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/              # REST API endpoints
│   │   ├── gemini.py     # Gemini API routes
│   │   ├── health.py     # Health checks
│   │   └── user.py       # User routes
│   ├── config/           # Configuration modules
│   │   ├── gemini_config.py     # Gemini configuration
│   │   └── logging_config.py    # Logging setup
│   ├── exceptions/       # Custom exception classes
│   │   └── gemini_exceptions.py # Gemini-specific exceptions
│   ├── services/         # Business logic
│   │   └── gemini_service.py    # Gemini service implementation
│   ├── utils/            # Utility functions
│   │   ├── api_key_manager.py   # API key management
│   │   └── retry_handler.py     # Retry logic
│   └── tests/            # Unit tests
├── docs/                 # Documentation
│   ├── SETUP.md         # Complete setup guide
│   ├── gemini_integration.md    # Integration docs
│   ├── QUICK_REFERENCE.md       # Quick reference
│   └── IMPLEMENTATION_SUMMARY.md # Implementation summary
├── scripts/             # Utility scripts
│   └── validate_setup.py # Setup validation
├── .env.example         # Example environment configuration
├── .gitignore          # Git ignore rules
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)** - Complete installation and configuration
- **[Integration Guide](docs/gemini_integration.md)** - Detailed integration documentation
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Common commands and examples
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - What's been implemented

## 🔧 Configuration

### Required
```env
GOOGLE_API_KEY=your_api_key_here  # Get from https://aistudio.google.com/app/apikey
```

### Optional
```env
DEFAULT_MODEL=gemini-1.5-flash    # or gemini-pro
TEMPERATURE_DEFAULT=0.7           # 0.0 (deterministic) to 1.0 (creative)
MAX_TOKENS_DEFAULT=2048           # Maximum output tokens
REQUEST_TIMEOUT_SECONDS=30        # Request timeout
MAX_RETRIES=3                     # Retry attempts
```

See `.env.example` for all available options.

## 🚀 Usage

### Python API

```python
from app.services import get_gemini_service

# Generate text
service = get_gemini_service()
response = service.generate(
    prompt="Explain microservices architecture",
    system_prompt="You are a software architect",
    temperature=0.7
)
print(response)
```

### REST API

```bash
# Generate text
curl -X POST http://localhost:8000/api/gemini/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is Docker?",
    "temperature": 0.7
  }'
```

### Model Selection

```python
# Use Flash (fast, optimized)
from app.services import get_gemini_flash_service
service = get_gemini_flash_service()

# Use Pro (more capable)
from app.services import get_gemini_pro_service
service = get_gemini_pro_service()
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_gemini_service.py
```

## 🔍 Validation

Validate your setup before running:

```bash
python scripts/validate_setup.py
```

This checks:
- ✅ Dependencies installed
- ✅ `.env` file exists
- ✅ API key configured
- ✅ Configuration valid
- ✅ Service initialization works

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint |
| `/api/health` | GET | Application health |
| `/api/gemini/health` | GET | Gemini API health |
| `/api/gemini/generate` | POST | Generate text (default model) |
| `/api/gemini/generate/flash` | POST | Generate with Flash model |
| `/api/gemini/generate/pro` | POST | Generate with Pro model |
| `/api/gemini/batch` | POST | Batch generation |
| `/api/gemini/models/available` | GET | List available models |
| `/api/gemini/models/current` | GET | Current model info |
| `/docs` | GET | Interactive API documentation |

## 🐛 Troubleshooting

### API Key Issues
```bash
# Check if .env exists
ls -la .env

# Verify API key is set
grep GOOGLE_API_KEY .env
```

### Dependency Issues
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Import Errors
```bash
# Make sure you're in the backend directory
cd backend

# Run from project root
python -m app.main
```

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --port 8001
```

## 📊 Error Handling

The implementation includes comprehensive error handling:

```python
from app.exceptions import (
    GeminiRateLimitError,      # Rate limit exceeded
    GeminiTimeoutError,        # Request timeout
    GeminiAuthenticationError, # Auth failed
    GeminiAPIError,           # General API error
)

try:
    service.generate("prompt")
except GeminiRateLimitError:
    # Wait and retry (happens automatically)
    pass
except GeminiAuthenticationError:
    # Check your API key
    pass
```

## 🔐 Security

- ✅ API keys stored in environment variables
- ✅ `.env` file excluded from git
- ✅ API key validation on startup
- ✅ Secure error messages (no key exposure)
- ✅ Rate limiting awareness

**Never commit `.env` file or expose API keys!**

## 📦 Dependencies

Key dependencies:
- **FastAPI** - Modern web framework
- **LangChain** - LLM application framework
- **Pydantic** - Data validation
- **Google Generative AI** - Gemini API client

See `requirements.txt` for complete list with versions.

## 🚀 Deployment

### Development
```bash
python -m app.main
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Future)
```bash
docker build -t system-architect-backend .
docker run -p 8000:8000 --env-file .env system-architect-backend
```

## 📝 Development

### Adding New Endpoints
1. Create route in `app/api/`
2. Register in `app/main.py`
3. Add tests in `app/tests/`
4. Update documentation

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings
- Add unit tests

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Run validation before committing

## 📖 Additional Resources

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

## 📄 License

[Your License Here]

## 👤 Author

[Your Name/Team]

---

**Need Help?** Check the [Setup Guide](docs/SETUP.md) or [Quick Reference](docs/QUICK_REFERENCE.md)
