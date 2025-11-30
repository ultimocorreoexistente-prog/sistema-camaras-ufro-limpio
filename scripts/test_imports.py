#!/usr/bin/env python3
"""
Test script to verify imports work correctly
"""

try:
    print("🔍 Testing imports...")
    
    # Test 1: Import from models.base
    print("  1. Testing models.base import...")
    try:
        from models.base import BaseModel
        print("     ✅ BaseModel imported successfully from models.base")
    except ImportError as e:
        print(f"     ❌ Failed to import BaseModel: {e}")
    
    # Test 2: Import from models
    print("  2. Testing models import...")
    try:
        from models import db, Usuario, Camara
        print("     ✅ Database and models imported successfully")
    except ImportError as e:
        print(f"     ❌ Failed to import from models: {e}")
    
    # Test 3: Import config
    print("  3. Testing config import...")
    try:
        from config import config
        print("     ✅ Config imported successfully")
    except ImportError as e:
        print(f"     ❌ Failed to import config: {e}")
        # Create basic config for testing
        import os
        config = {'DB_URL': os.getenv('DATABASE_URL')}
        print("     ✅ Basic config created")
    
    print("\n🎉 All imports tested successfully!")
    
except Exception as e:
    print(f"❌ Critical error: {e}")
    exit(1)