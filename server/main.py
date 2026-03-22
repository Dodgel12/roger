from fastapi import FastAPI, HTTPException
from ai_agent import ask_roger
from database import init_db, get_tasks_for_day, save_push_token, get_push_token, save_message, get_messages, get_tasks_for_today, complete_task, get_today_stats, reset_daily_tasks, get_weekly_stats, save_weekly_report, save_reflection
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

# Initialise DB tables on startup
init_db()

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
            PushMessage(
                to=token, 
                title=title, 
                body=message,
                data={"experienceId": "@anonymous/roger-app"}
            )
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

    # Persist user message
    save_message("user", user_message)

    # Ask Roger (Groq API agent)
    response = ask_roger(user_message)

    # Persist Roger's response
    save_message("roger", response)

    return {"response": response}

@app.get("/messages")
async def get_all_messages(limit: int = 100):
    """Return persisted chat history from DB."""
    return get_messages(limit=limit)

@app.get("/tasks/today")
async def tasks_today():
    """Return today's tasks with completion status."""
    return get_tasks_for_today()

@app.post("/tasks/{task_id}/complete")
async def mark_task_complete(task_id: int):
    """Mark a specific task as done."""
    success = complete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    stats = get_today_stats()
    return {"status": "completed", "stats": stats}

@app.get("/stats/today")
async def stats_today():
    """Return today's discipline score."""
    return get_today_stats()

@app.post("/register-push-token")
async def register_push_token(data: dict):
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
    
    save_push_token(token)
    print(f"Push token registered: {token}")
    return {"status": "success"}

# --------------------------
# Reflections
# --------------------------
@app.post("/reflect")
async def handle_reflection(data: dict):
    went_well = data.get("went_well", "")
    slowed_down = data.get("slowed_down", "")
    
    if not went_well or not slowed_down:
        raise HTTPException(status_code=400, detail="Both reflection fields are required.")
        
    save_reflection(went_well, slowed_down)
    
    prompt = f"I just completed my weekly reflection.\nWhat went well: {went_well}\nWhat slowed me down: {slowed_down}\nGive me a 3-4 sentence hard-hitting, strict coaching analysis. Do NOT use bullet points or numbered lists. Tell me exactly what I need to fix to eliminate distractions, and how to double down on what went well."
    
    response = ask_roger(prompt)
    
    # Save the feedback into chat messages
    save_message("user", f"Reflected: Went well: {went_well}. Slowed down: {slowed_down}")
    save_message("roger", response)
    
    return {"status": "success", "response": response}

# --------------------------
# Daily lock-in / tasks
# --------------------------
def generate_daily_lockin():
    """Send daily tasks overview at scheduled times."""

    day_name = datetime.now().strftime("%A")
    tasks = get_tasks_for_day(day_name)

    prompt_message = (
        f"Give me a strict, motivating message to keep the user accountable "
        f"for their tasks today {tasks}. Max 4 sentences."
    )

    answer = ask_roger(prompt_message)

    full_msg = f"Daily lock-in ({datetime.now().strftime('%H:%M:%S')}): {answer}"

    save_message("roger", full_msg)

    send_push_notification(
        "Roger: Daily Focus",
        full_msg
    )

    save_message("roger", answer)

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

    save_message("roger", full_msg)
    send_push_notification("Roger: Morning Motivation", quote)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Morning quote sent.")
# --------------------------
# Weekly report
# --------------------------
def generate_weekly_report():
    """Send a weekly performance report and AI analysis."""
    stats = get_weekly_stats()
    start_date = stats["start_date"]
    end_date = stats["end_date"]
    pct = int(stats["completion_pct"] * 100)
    best = stats["best_habit"]
    weakest = stats["weakest_habit"]
    
    prompt = f"User's weekly completion is {pct}%. Best habit: {best}. Weakest habit: {weakest}. Give a 4-sentence strict, motivating weekly reflection and improvement advice."
    
    ai_advice = ask_roger(prompt)
    
    save_weekly_report(start_date, end_date, stats["completion_pct"], best, weakest, ai_advice)
    
    full_msg = f"Weekly Report ({start_date} to {end_date}):\nOverall Completion: {pct}%\nBest Habit: {best}\nWeakest Habit: {weakest}\n\nRoger's Analysis:\n{ai_advice}"
    
    save_message("roger", full_msg)
    send_push_notification("Roger: Your Weekly Review is ready", full_msg)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Weekly report sent.")

# --------------------------
# Reflection reminder
# --------------------------
def generate_reflection_reminder():
    """Remind user to reflect every Sunday."""
    msg = "It's time for your weekly reflection. Head to the Reflect tab to track your thoughts."
    save_message("roger", msg)
    send_push_notification("Roger: Weekly Reflection", msg)

# --------------------------
# Scheduler setup
# --------------------------
scheduler = BackgroundScheduler()

# Daily lock-ins at 07:30, 14:50, 19:30, 17:15, 20:30
scheduler.add_job(generate_daily_lockin, 'cron', hour=7, minute=30)
scheduler.add_job(generate_daily_lockin, 'cron', hour=14, minute=50)
scheduler.add_job(generate_daily_lockin, 'cron', hour=19, minute=30)
scheduler.add_job(generate_daily_lockin, 'cron', hour=17, minute=15)
scheduler.add_job(generate_daily_lockin, 'cron', hour=20, minute=30)
scheduler.add_job(generate_daily_lockin, 'cron', hour=21, minute=5)

# Morning motivational quotes
scheduler.add_job(generate_morning_quote, 'cron', hour=6, minute=15)  # Mon-Sat
scheduler.add_job(generate_morning_quote, 'cron', day_of_week='sun', hour=9, minute=0)  # Sunday

# Weekly Report
scheduler.add_job(generate_weekly_report, 'cron', day_of_week='sun', hour=18, minute=0)

# Reflection Reminder
scheduler.add_job(generate_reflection_reminder, 'cron', day_of_week='sun', hour=10, minute=0)

# Reset tasks completion at midnight every day
scheduler.add_job(reset_daily_tasks, 'cron', hour=0, minute=0)

scheduler.start()
