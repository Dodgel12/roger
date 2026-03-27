#!/usr/bin/env python3
"""
Test Firebase Push Notification Sending
Sends a test notification to test the Firebase integration end-to-end
"""

import sys
from firebase_service import get_firebase_service
from database import get_push_token, get_db_connection

def test_send_notification():
    """Test sending a push notification"""
    
    print("=" * 60)
    print("🔥 FIREBASE PUSH NOTIFICATION TEST")
    print("=" * 60)
    print()
    
    # Initialize Firebase
    print("1️⃣  Initializing Firebase...")
    firebase = get_firebase_service()
    if not firebase.initialized:
        print("   ❌ Firebase not initialized")
        print("   Make sure firebase-key.json is in the server directory")
        return False
    print("   ✅ Firebase initialized")
    print()
    
    # Get user 1's push token
    print("2️⃣  Getting push token for user 1...")
    token = get_push_token(1)
    
    if not token:
        print("   ⚠️  No push token found for user 1")
        print("   → User needs to register a Firebase token from the mobile app")
        print("   → Endpoint: POST /register-push-token")
        print("   → Or: POST /firebase/register-token")
        print()
        print("   For testing, you can:")
        print("   a) Get FCM token from React Native app")
        print("   b) Use a test token from Firebase Console")
        print()
        
        # Show how to manually test with a token
        print("3️⃣  Testing with a custom FCM token...")
        print("   Enter a test FCM token (or press Enter to skip):")
        test_token = input("   Token: ").strip()
        
        if not test_token:
            print("   ⏭️  Skipping notification test")
            return True
        
        token = test_token
    else:
        print(f"   ✅ Token found: {token[:50]}...")
    print()
    
    # Send test notification
    print("4️⃣  Sending test notification...")
    try:
        success = firebase.send_notification(
            token,
            "🔥 Test Notification",
            "Firebase push notifications are working! 🎉"
        )
        
        if success:
            print("   ✅ Notification sent successfully!")
            print()
            print("   📱 Check your phone/emulator for the notification")
            print()
            return True
        else:
            print("   ❌ Notification send failed")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_send_notification()
    
    print("=" * 60)
    if success:
        print("✅ FIREBASE PUSH TEST COMPLETE")
        print()
        print("Your app is ready to receive push notifications from:")
        print("  • Scheduler jobs (Focus Mode, Burnout Detection, etc.)")
        print("  • Chat responses")
        print("  • Weekly reports")
        print("  • Manual notifications")
    else:
        print("❌ FIREBASE PUSH TEST FAILED")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
