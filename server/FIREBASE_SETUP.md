# Firebase Push Notifications Setup Guide

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Add project"
3. Name it "Roger AI" (or your preference)
4. Click "Create project"
5. Wait for project creation to complete

## Step 2: Get Firebase Credentials

1. In Firebase Console, click the **gear icon** → **Project Settings**
2. Go to **Service Accounts** tab
3. Click **Generate New Private Key**
4. Save the JSON file as `firebase-key.json` in your `server/` directory
5. **⚠️ IMPORTANT:** Add `firebase-key.json` to `.gitignore` to keep it secret

## Step 3: Enable Cloud Messaging

1. In Firebase Console, go to **Cloud Messaging**
2. Copy your **Server API Key** (you'll need this for the client)

## Step 4: Update Python Dependencies

Add to `requirements.txt`:
```
firebase-admin==6.2.0
```

Then run:
```bash
pip install -r requirements.txt
```

## Step 5: Create Firebase Service Module

Create `server/firebase_service.py`:

```python
import firebase_admin
from firebase_admin import credentials, messaging
import os
import json

class FirebaseService:
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
        """Send push notification to a device via Firebase"""
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
        """Send notification to multiple devices"""
        if not self.initialized or not tokens:
            return False
        
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
            print(f"✅ Multicast sent: {response.success} succeeded, {response.failure_count} failed")
            return True
        except Exception as e:
            print(f"❌ Failed to send multicast: {e}")
            return False

def get_firebase_service():
    """Get singleton Firebase service instance"""
    return FirebaseService()
```

## Step 6: Update main.py

Replace the push notification imports and functions in `main.py`:

### Remove these imports:
```python
# DELETE:
from exponent_server_sdk import PushClient, PushMessage, PushServerError
```

### Add this import:
```python
# ADD:
from firebase_service import get_firebase_service
```

### Replace the push notification function:
```python
# REPLACE the old send_push_notification function with:

def send_push_notification(user_id: int, title: str, message: str):
    """Send push notification to user via Firebase."""
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT device_token FROM users WHERE id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row["device_token"]:
        print(f"No device token found for user {user_id}.")
        return
    
    firebase_service = get_firebase_service()
    firebase_service.send_notification(
        row["device_token"],
        title=title,
        body=message,
        data={"type": "reminder"}
    )
```

## Step 7: Update Frontend (React Native)

In your mobile app, install Firebase:

```bash
cd roger-app
npm install @react-native-firebase/app @react-native-firebase/messaging
```

Register for push notifications:

```javascript
import messaging from '@react-native-firebase/messaging';

// Request permission
messaging().requestPermission();

// Get device token and send to server
messaging().getToken().then(token => {
  // Send this token to your server's /register-push-token endpoint
  await client.post("/register-push-token", { token });
});
```

## Step 8: Update Database (Optional)

If you're storing tokens in a `users` table, make sure it has a `device_token` column:

```sql
ALTER TABLE users ADD COLUMN device_token TEXT;
```

## Testing

Send a test notification:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

## Troubleshooting

- **firebase-key.json not found:** Download it again from Firebase Console → Project Settings → Service Accounts
- **Notification not received:** Check device token is correctly registered on `/register-push-token`
- **Import errors:** Make sure `firebase-admin` is installed: `pip install firebase-admin`

## Reference

- [Firebase Admin Python Documentation](https://firebase.google.com/docs/admin/setup)
- [Cloud Messaging Guide](https://firebase.google.com/docs/cloud-messaging)
