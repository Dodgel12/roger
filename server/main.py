from fastapi import FastAPI
from ai_agent import ask_roger
from database import get_tasks_for_day
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

messages = []

# --------------------------
# Chat endpoints
# --------------------------
@app.get("/")
def root():
    return {"roger": "online"}

@app.post("/chat")
def chat(data: dict):
    user_message = data.get("message", "")
    if not user_message:
        return {"response": "Please send a message."}

    # Ask Roger (Ollama LFM)
    response = ask_roger(user_message)

    messages.append({"user": user_message, "time": datetime.now().strftime("%H:%M")})
    messages.append({"roger": response, "time": datetime.now().strftime("%H:%M")})

    return {"response": response}

@app.get("/messages")
def get_messages():
    return messages

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
            msg += f"• {t[1]} ({t[2]} - {t[3]})\n"
        msg += "\nLock in!"

    messages.append({"roger": msg, "time": datetime.now().strftime("%H:%M")})
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

    messages.append({"roger": f"Morning motivation ({scheduled_time}): {quote}", "time": datetime.now().strftime("%H:%M")})
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