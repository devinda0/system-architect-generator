# Setup Guide - Google Gemini API Integration

This guide will walk you through setting up the Google Gemini API integration from scratch.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Google account for Gemini API access

## Step 1: Install Dependencies

### Option A: Using pip (Recommended)

```bash
cd backend
pip install -r requirements.txt
```

### Option B: Using virtual environment (Best Practice)

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Get Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Select a project or create a new one
5. Copy the generated API key (starts with `AIzaSy...`)

## Step 3: Configure Environment Variables

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file:**
   ```bash
   # Open in your editor
   nano .env
   # or
   code .env
   ```

3. **Add your API key:**
   ```env
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

4. **Optional: Customize other settings:**
   ```env
   DEFAULT_MODEL=gemini-1.5-flash
   TEMPERATURE_DEFAULT=0.7
   MAX_TOKENS_DEFAULT=2048
   ```

## Step 4: Validate Setup

Run the validation script to check if everything is configured correctly:

```bash
python scripts/validate_setup.py
```

Expected output:
```
============================================================
Google Gemini API Configuration Validation
============================================================

Checking dependencies...
  ✓ fastapi
  ✓ uvicorn
  ✓ pydantic
  ✓ pydantic_settings
  ✓ langchain
  ✓ langchain_google_genai
  ✓ google.generativeai
✓ All dependencies installed

Checking .env file...
  ✓ .env file exists

Checking API key configuration...
  ✓ API key configured (length: 39)

Checking configuration...
  ✓ Configuration loaded successfully
    - Default model: gemini-1.5-flash
    - Temperature: 0.7
    - Max tokens: 2048
    - Request timeout: 30s
    - Max retries: 3

Testing Gemini service initialization...
  ✓ Service initialized successfully
    - Model: gemini-1.5-flash
    - Type: Flash

============================================================
Validation Summary
============================================================
  ✓ PASS - Dependencies
  ✓ PASS - .env file
  ✓ PASS - API key
  ✓ PASS - Configuration
  ✓ PASS - Service initialization

✅ All checks passed! Your Gemini API integration is ready.
```

## Step 5: Start the Server

### Development Mode (with auto-reload)

```bash
python -m app.main
```

Or:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Expected output:
```
INFO:     Will watch for changes in these directories: ['/path/to/backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Starting System Architect Generator API...
INFO:     ✓ Google Gemini API key configured successfully
INFO:     Application startup complete
INFO:     Application startup complete.
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Step 6: Test the API

### Using Browser

1. Open http://127.0.0.1:8000
2. You should see:
   ```json
   {
     "name": "System Architect Generator API",
     "version": "0.1.0",
     "status": "running",
     "docs": "/docs",
     "health": "/api/health"
   }
   ```

### Using API Documentation

1. Open http://127.0.0.1:8000/docs (Swagger UI)
2. Try the `/api/gemini/health` endpoint
3. Test `/api/gemini/generate` with a sample prompt

### Using curl

```bash
# Health check
curl http://127.0.0.1:8000/api/gemini/health

# Generate text
curl -X POST http://127.0.0.1:8000/api/gemini/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain microservices architecture in 3 sentences",
    "temperature": 0.7
  }'
```

### Using Python

```python
import requests

# Health check
response = requests.get("http://127.0.0.1:8000/api/gemini/health")
print(response.json())

# Generate text
response = requests.post(
    "http://127.0.0.1:8000/api/gemini/generate",
    json={
        "prompt": "What is REST API?",
        "system_prompt": "You are a technical expert",
        "temperature": 0.7
    }
)
print(response.json()["content"])
```

## Folder Structure

After setup, your folder structure should look like:

```
backend/
├── .env                    # Your environment variables (DO NOT COMMIT)
├── .env.example           # Example environment file
├── .gitignore            # Git ignore file
├── requirements.txt      # Python dependencies
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   ├── gemini.py     # Gemini API endpoints
│   │   ├── health.py     # Health check endpoints
│   │   └── user.py       # User endpoints
│   ├── config/
│   │   ├── __init__.py
│   │   ├── gemini_config.py     # Gemini configuration
│   │   └── logging_config.py    # Logging setup
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── gemini_exceptions.py # Custom exceptions
│   ├── services/
│   │   ├── __init__.py
│   │   └── gemini_service.py    # Gemini service
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── api_key_manager.py   # API key management
│   │   └── retry_handler.py     # Retry logic
│   └── tests/
│       ├── test_gemini_service.py
│       ├── test_api_key_manager.py
│       └── test_retry_handler.py
├── docs/
│   └── gemini_integration.md    # Integration documentation
└── scripts/
    └── validate_setup.py         # Setup validation script
```

## Troubleshooting

### Issue: "Import pydantic_settings could not be resolved"

**Solution:**
```bash
pip install pydantic-settings
```

### Issue: "GOOGLE_API_KEY environment variable is not set"

**Solution:**
1. Check if `.env` file exists in backend directory
2. Verify `GOOGLE_API_KEY` is set in `.env`
3. Make sure the key starts with `AIzaSy`

### Issue: "Authentication failed"

**Solution:**
1. Verify your API key is correct
2. Check if the API key is enabled in Google AI Studio
3. Ensure you haven't exceeded the quota

### Issue: "Module not found" errors

**Solution:**
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

## Next Steps

1. **Read the full documentation:** `docs/gemini_integration.md`
2. **Explore the API:** http://127.0.0.1:8000/docs
3. **Run tests:** `pytest`
4. **Integrate with your frontend**

## Best Practices

1. **Never commit `.env` file** - It contains sensitive API keys
2. **Use virtual environments** - Isolate project dependencies
3. **Pin dependency versions** - Ensure reproducible builds
4. **Check logs** - Monitor for errors and rate limits
5. **Test thoroughly** - Use validation script before deploying

## Support

If you encounter issues:

1. Run the validation script: `python scripts/validate_setup.py`
2. Check logs for detailed error messages
3. Verify your API key in Google AI Studio
4. Review the troubleshooting section above

## Security Notes

⚠️ **Important:**
- Never commit your `.env` file to version control
- Never share your API key publicly
- Rotate API keys regularly
- Use environment-specific configurations
- Enable rate limiting in production
- Monitor API usage in Google AI Studio

## References

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
