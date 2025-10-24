#!/usr/bin/env python3
"""
Docker Setup Validation Script

This script validates that the Docker Compose setup is working correctly.
It checks:
1. MongoDB connection
2. Backend API health
3. Database initialization
4. API endpoints
"""

import sys
import time
import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


def print_header(message):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")


def print_success(message):
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message):
    """Print an error message."""
    print(f"✗ {message}")


def print_warning(message):
    """Print a warning message."""
    print(f"⚠ {message}")


def test_mongodb_connection():
    """Test MongoDB connection."""
    print_header("Testing MongoDB Connection")
    
    try:
        # Try to connect to MongoDB
        client = MongoClient(
            "mongodb://admin:admin123@localhost:27017/system_architect_generator?authSource=admin",
            serverSelectionTimeoutMS=5000
        )
        
        # Force connection
        client.admin.command('ping')
        print_success("MongoDB is accessible")
        
        # Check database
        db = client.system_architect_generator
        print_success(f"Connected to database: {db.name}")
        
        # Check collections
        collections = db.list_collection_names()
        expected_collections = ['users', 'projects', 'designs', 'feedback']
        
        print(f"\nExpected collections: {', '.join(expected_collections)}")
        print(f"Found collections: {', '.join(collections) if collections else 'None'}")
        
        for collection in expected_collections:
            if collection in collections:
                print_success(f"Collection '{collection}' exists")
            else:
                print_warning(f"Collection '{collection}' not found (will be created on first use)")
        
        # Check indexes
        for collection_name in collections:
            collection = db[collection_name]
            indexes = list(collection.list_indexes())
            print(f"\nIndexes for '{collection_name}': {len(indexes)} index(es)")
            for idx in indexes:
                print(f"  - {idx['name']}")
        
        client.close()
        return True
        
    except ConnectionFailure as e:
        print_error(f"Could not connect to MongoDB: {e}")
        print_warning("Make sure MongoDB container is running: docker compose ps")
        return False
    except Exception as e:
        print_error(f"MongoDB test failed: {e}")
        return False


def test_backend_health():
    """Test backend API health."""
    print_header("Testing Backend API")
    
    try:
        # Test root endpoint
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success("Root endpoint accessible")
            print(f"  Name: {data.get('name')}")
            print(f"  Version: {data.get('version')}")
            print(f"  Status: {data.get('status')}")
        else:
            print_error(f"Root endpoint returned status {response.status_code}")
            return False
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success("Health endpoint accessible")
            print(f"  Status: {data.get('status')}")
            print(f"  MongoDB: {data.get('mongodb_status')}")
            print(f"  Gemini: {data.get('gemini_configured')}")
        else:
            print_error(f"Health endpoint returned status {response.status_code}")
            return False
        
        # Test API docs
        response = requests.get("http://localhost:8000/docs", timeout=10)
        if response.status_code == 200:
            print_success("API documentation accessible at http://localhost:8000/docs")
        else:
            print_warning("API documentation not accessible")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to backend API")
        print_warning("Make sure backend container is running: docker compose ps")
        return False
    except Exception as e:
        print_error(f"Backend test failed: {e}")
        return False


def test_api_endpoints():
    """Test various API endpoints."""
    print_header("Testing API Endpoints")
    
    try:
        # Test user endpoints
        print("\nTesting User API...")
        
        # Create a test user
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User"
        }
        
        response = requests.post(
            "http://localhost:8000/api/users",
            json=test_user,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            user_data = response.json()
            print_success("User creation successful")
            print(f"  User ID: {user_data.get('user_id')}")
            
            # Try to get the user
            user_id = user_data.get('user_id')
            response = requests.get(
                f"http://localhost:8000/api/users/{user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                print_success("User retrieval successful")
            else:
                print_warning(f"User retrieval returned status {response.status_code}")
        else:
            print_warning(f"User creation returned status {response.status_code}")
            if response.status_code == 409:
                print_warning("User might already exist from previous test")
        
        return True
        
    except Exception as e:
        print_error(f"API endpoint test failed: {e}")
        return False


def main():
    """Main validation function."""
    print_header("Docker Setup Validation")
    print("This script validates the Docker Compose setup.")
    print("Make sure Docker containers are running before proceeding.")
    print("\nPress Ctrl+C to cancel...")
    
    try:
        time.sleep(2)
    except KeyboardInterrupt:
        print("\n\nValidation cancelled.")
        sys.exit(0)
    
    results = {
        "mongodb": False,
        "backend": False,
        "api_endpoints": False
    }
    
    # Run tests
    results["mongodb"] = test_mongodb_connection()
    time.sleep(1)
    
    results["backend"] = test_backend_health()
    time.sleep(1)
    
    results["api_endpoints"] = test_api_endpoints()
    
    # Print summary
    print_header("Validation Summary")
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! Your Docker setup is working correctly.")
        print("\nYou can now:")
        print("  • Access the API at http://localhost:8000")
        print("  • View API docs at http://localhost:8000/docs")
        print("  • Connect to MongoDB at mongodb://admin:admin123@localhost:27017")
        return 0
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("  • Check container status: docker compose ps")
        print("  • View logs: docker compose logs -f")
        print("  • Restart services: docker compose restart")
        print("  • Clean restart: docker compose down && docker compose up -d")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nValidation interrupted.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
