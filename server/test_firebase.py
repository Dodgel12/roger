#!/usr/bin/env python3
"""
Firebase Integration Test Script
Tests that Firebase Cloud Messaging is properly configured for Roger AI
"""

import sys
import os

def test_firebase_setup():
    """Test Firebase setup step by step"""
    
    print("=" * 60)
    print("🔥 FIREBASE INTEGRATION TEST")
    print("=" * 60)
    print()
    
    # Test 1: Check if firebase-admin package is installed
    print("1️⃣  Checking firebase-admin installation...")
    try:
        import firebase_admin
        print("   ✅ firebase-admin is installed")
        print(f"   Version: {firebase_admin.__version__ if hasattr(firebase_admin, '__version__') else 'unknown'}")
    except ImportError as e:
        print(f"   ❌ firebase-admin not found: {e}")
        print("   → Run: pip install firebase-admin")
        return False
    print()
    
    # Test 2: Check if firebase_service.py exists
    print("2️⃣  Checking firebase_service.py...")
    if os.path.exists("firebase_service.py"):
        print("   ✅ firebase_service.py found")
    else:
        print("   ❌ firebase_service.py not found in current directory")
        print(f"   Current directory: {os.getcwd()}")
        return False
    print()
    
    # Test 3: Try to import firebase_service
    print("3️⃣  Importing firebase_service module...")
    try:
        from firebase_service import get_firebase_service
        print("   ✅ firebase_service imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import firebase_service: {e}")
        return False
    print()
    
    # Test 4: Check if firebase-key.json exists
    print("4️⃣  Checking firebase-key.json credentials...")
    if os.path.exists("firebase-key.json"):
        print("   ✅ firebase-key.json found")
        try:
            import json
            with open("firebase-key.json", "r") as f:
                creds = json.load(f)
                print(f"   Project ID: {creds.get('project_id', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️  Could not read firebase-key.json: {e}")
    else:
        print("   ⚠️  firebase-key.json not found")
        print("   → Download from Firebase Console:")
        print("   → https://console.firebase.google.com/")
        print("   → Project Settings → Service Accounts → Generate New Private Key")
    print()
    
    # Test 5: Initialize Firebase service
    print("5️⃣  Initializing Firebase service...")
    try:
        firebase = get_firebase_service()
        if firebase.initialized:
            print("   ✅ Firebase initialized successfully!")
            print("   🎉 Firebase is ready for push notifications")
        else:
            print("   ⚠️  Firebase service created but not initialized")
            print("   → This usually means firebase-key.json is missing")
            print("   → Place your credentials file in the server directory")
    except Exception as e:
        print(f"   ❌ Error initializing Firebase: {e}")
        return False
    print()
    
    # Test 6: Test send_notification method exists
    print("6️⃣  Checking Firebase methods...")
    try:
        firebase = get_firebase_service()
        if hasattr(firebase, 'send_notification'):
            print("   ✅ send_notification() method available")
        if hasattr(firebase, 'send_multicast'):
            print("   ✅ send_multicast() method available")
    except Exception as e:
        print(f"   ❌ Error checking methods: {e}")
        return False
    print()
    
    # Summary
    print("=" * 60)
    print("✅ FIREBASE SETUP TEST COMPLETE")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. If Firebase is initialized: Your server is ready!")
    print("2. If firebase-key.json is missing:")
    print("   - Download credentials from Firebase Console")
    print("   - Place in server/ directory")
    print("   - Run this test again")
    print()
    print("To start the server:")
    print("  python -m uvicorn main:app --reload")
    print()
    
    return True

if __name__ == "__main__":
    success = test_firebase_setup()
    sys.exit(0 if success else 1)
