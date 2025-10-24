#!/usr/bin/env python3
"""
MongoDB Connection Validation Script

This script validates the MongoDB setup and configuration.
Run this before starting the application to ensure everything is configured correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.mongodb_config import (
    get_mongodb_config,
    connect_to_mongodb,
    close_mongodb_connection,
    check_mongodb_health
)


async def validate_mongodb():
    """Validate MongoDB configuration and connection."""
    print("=" * 60)
    print("MongoDB Connection Validation")
    print("=" * 60)
    
    # Step 1: Check configuration
    print("\n1. Checking MongoDB configuration...")
    try:
        config = get_mongodb_config()
        print(f"   ✓ Configuration loaded")
        print(f"   - Database: {config.MONGODB_DB_NAME}")
        print(f"   - URL: {config.MONGODB_URL.split('@')[-1] if '@' in config.MONGODB_URL else config.MONGODB_URL}")
        print(f"   - Min Pool Size: {config.MONGODB_MIN_POOL_SIZE}")
        print(f"   - Max Pool Size: {config.MONGODB_MAX_POOL_SIZE}")
    except Exception as e:
        print(f"   ✗ Configuration error: {e}")
        return False
    
    # Step 2: Test connection
    print("\n2. Testing MongoDB connection...")
    try:
        database = await connect_to_mongodb()
        print("   ✓ Successfully connected to MongoDB")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        print("\n   Troubleshooting tips:")
        print("   - Ensure MongoDB is running (brew services start mongodb-community)")
        print("   - Check MONGODB_URL in .env file")
        print("   - Verify network connectivity")
        return False
    
    # Step 3: Check health
    print("\n3. Checking MongoDB health...")
    try:
        health = await check_mongodb_health()
        print(f"   ✓ Health check passed")
        print(f"   - Status: {health['status']}")
        if health['status'] == 'connected':
            print(f"   - MongoDB Version: {health.get('mongodb_version', 'unknown')}")
            print(f"   - Database: {health.get('database', 'unknown')}")
    except Exception as e:
        print(f"   ✗ Health check failed: {e}")
        return False
    
    # Step 4: List collections
    print("\n4. Checking collections...")
    try:
        collections = await database.list_collection_names()
        if collections:
            print(f"   ✓ Found {len(collections)} collections:")
            for coll in collections:
                print(f"     - {coll}")
        else:
            print("   ℹ No collections found (this is normal for a new database)")
    except Exception as e:
        print(f"   ⚠ Could not list collections: {e}")
    
    # Step 5: Test operations
    print("\n5. Testing basic operations...")
    try:
        # Try to get collection
        test_collection = database[config.MONGODB_USERS_COLLECTION]
        
        # Count documents
        count = await test_collection.count_documents({})
        print(f"   ✓ Can access collections")
        print(f"   - Users collection has {count} documents")
        
    except Exception as e:
        print(f"   ✗ Operation test failed: {e}")
        return False
    
    # Step 6: Close connection
    print("\n6. Closing connection...")
    try:
        await close_mongodb_connection()
        print("   ✓ Connection closed successfully")
    except Exception as e:
        print(f"   ⚠ Error closing connection: {e}")
    
    # Success
    print("\n" + "=" * 60)
    print("✓ All validations passed!")
    print("=" * 60)
    print("\nMongoDB is configured correctly and ready to use.")
    print("You can now start the application with: uvicorn app.main:app --reload")
    return True


async def main():
    """Main entry point."""
    try:
        success = await validate_mongodb()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
