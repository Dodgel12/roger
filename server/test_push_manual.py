from database import get_push_token
from exponent_server_sdk import PushClient, PushMessage, PushServerError
from requests.exceptions import ConnectionError, HTTPError
import sys

def send_test_push():
    token = get_push_token()
    if not token:
        print("Error: No push token found in database. Please run the mobile app first to register.")
        sys.exit(1)

    print(f"Sending test notification to token: {token}")
    
    try:
        response = PushClient().publish(
            PushMessage(to=token, title="Test Notification", body="Roger is testing your push setup!")
        )
        print("Push sent successfully!")
        print(f"Response: {response}")
    except (PushServerError, ConnectionError, HTTPError) as exc:
        print(f"Failed to send push notification: {exc}")

if __name__ == "__main__":
    send_test_push()
