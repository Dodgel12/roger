from fastapi import FastAPI, HTTPException
from ai_agent import ask_roger
from database import get_tasks_for_day, save_push_token, get_push_token
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from exponent_server_sdk import PushClient, PushMessage, PushServerError
from requests.exceptions import ConnectionError, HTTPError
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

messages = []

# --------------------------
# Push Notifications Helper
# --------------------------
def send_push_notification(title, message):
    token = get_push_token()
    if not token:
        print("No push token found. Skipping notification.")
        return

    try:
        response = PushClient().publish(
            PushMessage(to=token, title=title, body=message)
        )
    except (PushServerError, ConnectionError, HTTPError) as exc:
        print(f"Failed to send push notification: {exc}")

# --------------------------
# Chat endpoints
# --------------------------
@app.get("/")
async def root():
    return {"roger": "online"}

@app.post("/chat")
async def chat(data: dict):
    user_message = data.get("message", "")
    if not user_message:
        return {"response": "Please send a message."}

    # Ask Roger (Ollama LFM)
    response = ask_roger(user_message)

    messages.append({"user": user_message, "time": datetime.now().strftime("%H:%M")})
    messages.append({"roger": response, "time": datetime.now().strftime("%H:%M")})

    return {"response": response}

@app.get("/messages")
async def get_messages():
    return messages

@app.post("/register-push-token")
async def register_push_token(data: dict):
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
    
    save_push_token(token)
    print(f"Push token registered: {token}")
    return {"status": "success"}

# --------------------------
# Daily lock-in / tasks
# --------------------------
def generate_daily_lockin():
    """Send daily tasks overview at scheduled times."""
    day_name = datetime.now().strftime("%A")
    tasks = get_tasks_for_day(day_name)

    if not tasks:
        msg = "No tasks for today."
    else:
        msg = "Good morning.\n\nToday's focus:\n"
        for t in tasks:
            msg += f"• {t[0]} ({t[1]})\n"
        msg += "\nLock in!"

    messages.append({"roger": msg, "time": datetime.now().strftime("%H:%M")})
    send_push_notification("Roger: Daily Focus", msg)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Daily lock-in sent.")

# --------------------------
# Morning motivational quote
# --------------------------
def generate_morning_quote():
    """Send a motivational quote using Roger."""
    now = datetime.now()
    weekday = now.weekday()  # Monday=0 ... Sunday=6

    # Sunday 9:00, other days 6:15
    scheduled_time = "9:00" if weekday == 6 else "6:15"

    prompt_message = "Give me a short, strict, motivating quote to start the day. Max 2 sentences."

    quote = ask_roger(prompt_message)
    full_msg = f"Morning motivation ({scheduled_time}): {quote}"

    messages.append({"roger": full_msg, "time": datetime.now().strftime("%H:%M")})
    send_push_notification("Roger: Morning Motivation", quote)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Morning quote sent.")

# --------------------------
# Scheduler setup
# --------------------------
scheduler = BackgroundScheduler()

# Daily lock-ins at 07:30, 14:50, 19:30
scheduler.add_job(generate_daily_lockin, 'cron', hour=7, minute=30)
scheduler.add_job(generate_daily_lockin, 'cron', hour=14, minute=50)
scheduler.add_job(generate_daily_lockin, 'cron', hour=19, minute=30)

# Morning motivational quotes
scheduler.add_job(generate_morning_quote, 'cron', hour=6, minute=15)  # Mon-Sat
scheduler.add_job(generate_morning_quote, 'cron', day_of_week='sun', hour=9, minute=0)  # Sunday

scheduler.start()
print("Scheduler started. Roger is ready.")