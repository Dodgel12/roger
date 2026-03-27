"""
Firebase Cloud Messaging Service for Roger AI
Handles push notifications via Firebase instead of Exponent SDK
"""

import firebase_admin
from firebase_admin import credentials, messaging
import os

class FirebaseService:
    """Singleton Firebase service for push notifications"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        try:
            # Check if credentials file exists
            if not os.path.exists("firebase-key.json"):
                print("⚠️  firebase-key.json not found. Push notifications disabled.")
                self.initialized = False
                self._initialized = True
                return
            
            # Initialize Firebase if not already done
            if not firebase_admin._apps:
                cred = credentials.Certificate("firebase-key.json")
                firebase_admin.initialize_app(cred)
            
            self.initialized = True
            print("✅ Firebase initialized successfully")
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            self.initialized = False
        
        self._initialized = True
    
    def send_notification(self, device_token: str, title: str, body: str, data: dict = None):
        """
        Send push notification to a single device via Firebase Cloud Messaging
        
        Args:
            device_token: FCM device token from client
            title: Notification title
            body: Notification body/message
            data: Optional data payload (dict)
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.initialized or not device_token:
            print(f"Cannot send notification: Firebase initialized={self.initialized}, token exists={bool(device_token)}")
            return False
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=device_token,
            )
            
            response = messaging.send(message)
            print(f"✅ Notification sent: {response}")
            return True
        except Exception as e:
            print(f"❌ Failed to send notification: {e}")
            return False
    
    def send_multicast(self, tokens: list, title: str, body: str, data: dict = None):
        """
        Send notification to multiple devices at once
        
        Args:
            tokens: List of FCM device tokens
            title: Notification title
            body: Notification body/message
            data: Optional data payload (dict)
        
        Returns:
            dict: Response with success_count and failure_count
        """
        if not self.initialized or not tokens:
            return {"success_count": 0, "failure_count": len(tokens or [])}
        
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=tokens,
            )
            
            response = messaging.send_multicast(message)
            print(f"✅ Multicast sent: {response.success_count} succeeded, {response.failure_count} failed")
            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }
        except Exception as e:
            print(f"❌ Failed to send multicast: {e}")
            return {"success_count": 0, "failure_count": len(tokens)}

def get_firebase_service():
    """Get singleton Firebase service instance"""
    return FirebaseService()
