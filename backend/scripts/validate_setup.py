#!/usr/bin/env python3
"""
Validation script to check Google Gemini API configuration.
Run this before starting the application to ensure everything is set up correctly.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'pydantic_settings',
        'langchain',
        'langchain_google_genai',
        'google.generativeai',
        'python-dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print("\n❌ Missing dependencies. Install with:")
        print("   pip install -r requirements.txt\n")
        return False
    
    print("✓ All dependencies installed\n")
    return True


def check_env_file():
    """Check if .env file exists."""
    print("Checking .env file...")
    env_path = Path(__file__).parent.parent / '.env'
    
    if not env_path.exists():
        print("  ✗ .env file not found")
        print("\n❌ Create .env file from .env.example:")
        print("   cp .env.example .env")
        print("   Then edit .env and add your GOOGLE_API_KEY\n")
        return False
    
    print("  ✓ .env file exists\n")
    return True


def check_api_key():
    """Check if API key is configured."""
    print("Checking API key configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY', '')
    
    if not api_key:
        print("  ✗ GOOGLE_API_KEY not set in .env file")
        print("\n❌ Add your Google Gemini API key to .env file:")
        print("   GOOGLE_API_KEY=your_actual_key_here")
        print("\nGet your API key from: https://aistudio.google.com/app/apikey\n")
        return False
    
    if api_key == 'your_api_key_here' or len(api_key) < 20:
        print("  ✗ GOOGLE_API_KEY appears to be invalid")
        print("\n❌ Set a valid Google Gemini API key in .env file")
        print("   Current value looks like placeholder or is too short")
        print("\nGet your API key from: https://aistudio.google.com/app/apikey\n")
        return False
    
    print(f"  ✓ API key configured (length: {len(api_key)})\n")
    return True


def check_config():
    """Check if configuration can be loaded."""
    print("Checking configuration...")
    
    try:
        from app.config.gemini_config import get_config
        config = get_config()
        
        print(f"  ✓ Configuration loaded successfully")
        print(f"    - Default model: {config.DEFAULT_MODEL}")
        print(f"    - Temperature: {config.TEMPERATURE_DEFAULT}")
        print(f"    - Max tokens: {config.MAX_TOKENS_DEFAULT}")
        print(f"    - Request timeout: {config.REQUEST_TIMEOUT_SECONDS}s")
        print(f"    - Max retries: {config.MAX_RETRIES}\n")
        
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}\n")
        return False


def test_service_initialization():
    """Test if Gemini service can be initialized."""
    print("Testing Gemini service initialization...")
    
    try:
        from app.services import get_gemini_service
        service = get_gemini_service()
        
        model_info = service.get_model_info()
        print(f"  ✓ Service initialized successfully")
        print(f"    - Model: {model_info['model']}")
        print(f"    - Type: {'Flash' if model_info['is_flash'] else 'Pro'}")
        print()
        
        return True
    except Exception as e:
        print(f"  ✗ Service initialization failed: {e}\n")
        return False


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("Google Gemini API Configuration Validation")
    print("=" * 60)
    print()
    
    checks = [
        ("Dependencies", check_dependencies),
        (".env file", check_env_file),
        ("API key", check_api_key),
        ("Configuration", check_config),
        ("Service initialization", test_service_initialization),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Unexpected error in {name}: {e}\n")
            results.append((name, False))
    
    print("=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {name}")
    
    print()
    
    if all(result for _, result in results):
        print("✅ All checks passed! Your Gemini API integration is ready.")
        print("\nStart the server with:")
        print("   python -m app.main")
        print("\nAPI documentation will be available at:")
        print("   http://127.0.0.1:8000/docs")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
