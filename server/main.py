"""
Roger AI Server - FastAPI backend (Single User Mode)
Secure API with token-based authentication for personal use.
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta  
from apscheduler.schedulers.background import BackgroundScheduler
from exponent_server_sdk import PushClient, PushMessage, PushServerError
from requests.exceptions import ConnectionError, HTTPError
from typing import Optional
import os

from ai_agent import ask_roger, generate_weekly_analysis
from database import (
    init_db, get_tasks_for_day, save_push_token, get_push_token,
    save_message, get_messages, get_tasks_for_today, complete_task,
    get_today_stats, reset_daily_tasks, get_weekly_stats, save_weekly_report,
    save_reflection, get_recent_reflections, get_all_reflections, add_task,
    create_or_get_skill, link_task_to_skill, get_user_skills, get_skill_stats,
    init_core_skills, get_user_skills_list, create_task
)
from auth import (
    create_user, authenticate_user, verify_token, revoke_token,
    extract_token_from_header
)

app = FastAPI(title="Roger AI", version="1.0.0")

# CORS middleware - allow local development and ngrok
import re

ALLOWED_ORIGINS = [
    "http://localhost:19000",      # Expo Metro
    "http://localhost:8000",       # Dev server
    "http://127.0.0.1:19000",
    "http://127.0.0.1:8000",
    "https://subporphyritic-venomless-delores.ngrok-free.dev",  # Current ngrok
]

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^(http://localhost:19000|http://localhost:8000|http://127\.0\.0\.1:19000|http://127\.0\.0\.1:8000|https://.*\.ngrok(?:-free)?\.dev)$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Initialize database
init_db()

# --------------------------
# Pydantic Models
# --------------------------
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    message: str

class RegisterPushTokenRequest(BaseModel):
    token: str

class ReflectionRequest(BaseModel):
    went_well: str
    slowed_down: str

class AddTaskRequest(BaseModel):
    name: str
    day_of_week: str
    start_time: Optional[str] = None
    duration: Optional[str] = None

class SkillRequest(BaseModel):
    name: str

class LinkSkillRequest(BaseModel):
    skill_id: int

class CreateTaskRequest(BaseModel):
    name: str
    day_of_week: str
    start_time: Optional[str] = None
    duration: Optional[str] = None
    skill_id: Optional[int] = None
# Authentication Dependency
# --------------------------
async def get_current_user_id(authorization: str = Header(None)) -> int:
    """
    Dependency to extract and verify user from Authorization header.
    Raise 401 if invalid or missing.
    """
    token = extract_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    is_valid, user_id = verify_token(token)
    if not is_valid or user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_id

# --------------------------
# Authentication Endpoints (Public)
# --------------------------
@app.post("/auth/register")
async def register(request: RegisterRequest):
    """Register a new user account."""
    if len(request.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    success, message, token = create_user(request.username, request.password)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"status": "success", "message": message, "token": token}

@app.post("/auth/login")
async def login(request: LoginRequest):
    """Authenticate user and return token."""
    success, message, token = authenticate_user(request.username, request.password)
    
    if not success:
        raise HTTPException(status_code=401, detail=message)
    
    return {"status": "success", "message": message, "token": token}

@app.post("/auth/logout")
async def logout(user_id: int = Depends(get_current_user_id), authorization: str = Header(None)):
    """Logout user and revoke token."""
    token = extract_token_from_header(authorization)
    revoke_token(token)
    return {"status": "success", "message": "Logged out successfully"}

# --------------------------
# Health Check
# --------------------------
@app.get("/")
async def root():
    return {"roger": "online", "version": "1.0.0"}

# --------------------------
# Chat Endpoints (Authenticated)
# --------------------------
@app.post("/chat")
async def chat(request: ChatRequest, user_id: int = Depends(get_current_user_id)):
    """Chat with Roger AI."""
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Persist user message
    save_message(user_id, "user", message)

    # Ask Roger with user context
    response = ask_roger(user_id, message)

    # Persist Roger's response
    save_message(user_id, "roger", response)

    return {"response": response}

@app.get("/messages")
async def get_all_messages(limit: int = 100, user_id: int = Depends(get_current_user_id)):
    """Get user's chat history."""
    if limit < 1 or limit > 500:
        limit = 100
    return {"messages": get_messages(user_id, limit=limit)}

# --------------------------
# Tasks Endpoints (Authenticated)
# --------------------------
@app.get("/tasks/today")
async def tasks_today(user_id: int = Depends(get_current_user_id)):
    """Get today's tasks."""
    return {"tasks": get_tasks_for_today(user_id)}

@app.post("/tasks")
async def add_new_task(request: AddTaskRequest, user_id: int = Depends(get_current_user_id)):
    """Add a new task."""
    if not request.name or not request.day_of_week:
        raise HTTPException(status_code=400, detail="name and day_of_week are required")
    
    add_task(user_id, request.name, request.day_of_week, request.start_time or "", request.duration or "")
    return {"status": "success", "message": "Task added"}

@app.post("/tasks/{task_id}/complete")
async def mark_task_complete(task_id: int, user_id: int = Depends(get_current_user_id)):
    """Mark a task as completed."""
    success = complete_task(user_id, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    stats = get_today_stats(user_id)
    return {"status": "completed", "stats": stats}

# --------------------------
# Stats Endpoints (Authenticated)
# --------------------------
@app.get("/stats/today")
async def stats_today(user_id: int = Depends(get_current_user_id)):
    """Get today's discipline score."""
    return get_today_stats(user_id)

@app.get("/stats/weekly")
async def stats_weekly(user_id: int = Depends(get_current_user_id)):
    """Get weekly stats."""
    return get_weekly_stats(user_id)

# --------------------------
# Push Notifications (Authenticated)
# --------------------------
def send_push_notification(user_id: int, title: str, message: str):
    """Send push notification to user."""
    token = get_push_token(user_id)
    if not token:
        print(f"No push token found for user {user_id}. Skipping notification.")
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
        print(f"Failed to send push notification to user {user_id}: {exc}")

@app.post("/register-push-token")
async def register_push_token(request: RegisterPushTokenRequest, user_id: int = Depends(get_current_user_id)):
    """Register push notification token."""
    if not request.token:
        raise HTTPException(status_code=400, detail="Token is required")
    
    save_push_token(user_id, request.token)
    print(f"Push token registered for user {user_id}")
    return {"status": "success"}

# --------------------------
# Reflections (Authenticated)
# --------------------------
@app.post("/reflect")
async def handle_reflection(request: ReflectionRequest, user_id: int = Depends(get_current_user_id)):
    """Save user reflection and get AI feedback."""
    if not request.went_well or not request.slowed_down:
        raise HTTPException(status_code=400, detail="Both reflection fields are required")
        
    save_reflection(user_id, request.went_well, request.slowed_down)
    
    prompt = f"I just completed my weekly reflection.\nWhat went well: {request.went_well}\nWhat slowed me down: {request.slowed_down}\nGive me a 3-4 sentence hard-hitting, strict coaching analysis. Do NOT use bullet points or numbered lists. Tell me exactly what I need to fix to eliminate distractions, and how to double down on what went well."
    
    response = ask_roger(user_id, prompt)
    
    # Save the feedback into chat messages
    save_message(user_id, "user", f"Reflected: Went well: {request.went_well}. Slowed down: {request.slowed_down}")
    save_message(user_id, "roger", response)
    
    return {"status": "success", "response": response}

@app.get("/reflections/history")
async def get_reflection_history(limit: int = 10, user_id: int = Depends(get_current_user_id)):
    """Get user's reflection history."""
    if limit < 1 or limit > 100:
        limit = 10
    
    reflections = get_all_reflections(user_id, limit)
    
    return {
        "status": "success",
        "reflections": reflections,
        "total": len(reflections)
    }

# --------------------------
# Weekly Reports (Authenticated)
# --------------------------
@app.post("/reports/weekly-generate")
async def generate_weekly_report_endpoint(user_id: int = Depends(get_current_user_id)):
    """Generate and save a weekly report."""
    from datetime import datetime
    
    # Get weekly stats
    stats = get_weekly_stats(user_id)
    
    # Generate AI analysis
    ai_advice = generate_weekly_analysis(user_id)
    
    # Save report to database
    save_weekly_report(
        user_id,
        stats["start_date"],
        stats["end_date"],
        stats["completion_pct"],
        stats["best_habit"],
        stats["weakest_habit"],
        ai_advice
    )
    
    # Save as a chat message so it appears in history
    report_summary = f"📊 Weekly Report ({stats['start_date']} to {stats['end_date']}):\n✅ Completion: {int(stats['completion_pct']*100)}%\n🏆 Best: {stats['best_habit']}\n📉 Weakest: {stats['weakest_habit']}\n\nRoger's Analysis:\n{ai_advice}"
    save_message(user_id, "roger", report_summary)
    
    return {
        "status": "success",
        "report": {
            "start_date": stats["start_date"],
            "end_date": stats["end_date"],
            "completion_pct": int(stats["completion_pct"] * 100),
            "best_habit": stats["best_habit"],
            "weakest_habit": stats["weakest_habit"],
            "ai_advice": ai_advice
        }
    }

@app.get("/reports/weekly")
async def get_latest_weekly_report(user_id: int = Depends(get_current_user_id)):
    """Get the latest weekly report for user."""
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT start_date, end_date, completion_pct, best_habit, weakest_habit, ai_advice FROM weeks WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"status": "no_report", "message": "No weekly reports available yet"}
    
    return {
        "status": "success",
        "report": {
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "completion_pct": int(row["completion_pct"] * 100),
            "best_habit": row["best_habit"],
            "weakest_habit": row["weakest_habit"],
            "ai_advice": row["ai_advice"]
        }
    }

# --------------------------
# Skills Tracking (Authenticated)
# --------------------------
@app.post("/skills")
async def create_skill(request: SkillRequest, user_id: int = Depends(get_current_user_id)):
    """Create or get a skill."""
    if not request.name or len(request.name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Skill name must be at least 2 characters")
    
    skill_id = create_or_get_skill(user_id, request.name)
    return {"status": "success", "skill_id": skill_id, "skill_name": request.name}

@app.get("/skills")
async def get_skills(user_id: int = Depends(get_current_user_id)):
    """Get all skills for user with progress."""
    skills = get_user_skills(user_id)
    
    return {
        "status": "success",
        "skills": [
            {
                "id": s["id"],
                "name": s["name"],
                "hours_practiced": s["hours_practiced"],
                "sessions_completed": s["sessions_completed"],
                "created_date": s["created_date"]
            }
            for s in skills
        ],
        "total_skills": len(skills)
    }

@app.get("/skills/{skill_id}")
async def get_skill(skill_id: int, user_id: int = Depends(get_current_user_id)):
    """Get detailed stats for a specific skill."""
    skill = get_skill_stats(user_id, skill_id)
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return {
        "status": "success",
        "skill": skill
    }

@app.post("/tasks/{task_id}/link-skill")
async def link_skill_to_task(task_id: int, request: LinkSkillRequest, user_id: int = Depends(get_current_user_id)):
    """Link a task to a skill."""
    if not request.skill_id:
        raise HTTPException(status_code=400, detail="skill_id is required")
    
    try:
        link_task_to_skill(user_id, task_id, request.skill_id)
        return {"status": "success", "message": "Task linked to skill"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --------------------------
# Scheduled Tasks (Single User - user_id = 1)
# --------------------------
SYSTEM_USER_ID = 1  # Single user setup

scheduler = BackgroundScheduler()

def generate_daily_lockin():
    """Send daily lock-in reminder."""
    from database import get_db_connection
    token = get_push_token(SYSTEM_USER_ID)
    if token:
        send_push_notification(SYSTEM_USER_ID, "🔒 Daily Lock-In", "Time to lock in and crush it!")

def generate_morning_quote():
    """Send morning motivational quote."""
    from database import get_db_connection
    token = get_push_token(SYSTEM_USER_ID)
    if token:
        send_push_notification(SYSTEM_USER_ID, "🌅 Good Morning!", "Rise up, it's time to win the day!")

def generate_wind_down_quote():
    """Send wind down quote at night."""
    from database import get_db_connection
    token = get_push_token(SYSTEM_USER_ID)
    if token:
        send_push_notification(SYSTEM_USER_ID, "🌙 Wind Down", "Reflect on your wins today and rest well!")

def generate_weekly_report():
    """Generate weekly report for user."""
    try:
        stats = get_weekly_stats(SYSTEM_USER_ID)
        ai_advice = generate_weekly_analysis(SYSTEM_USER_ID)
        
        save_weekly_report(
            SYSTEM_USER_ID,
            stats["start_date"],
            stats["end_date"],
            stats["completion_pct"],
            stats["best_habit"],
            stats["weakest_habit"],
            ai_advice
        )
        
        # Send notification
        send_push_notification(
            SYSTEM_USER_ID,
            "📊 Weekly Report Ready",
            f"Check your performance: {int(stats['completion_pct']*100)}% completion"
        )
        print(f"[Weekly Report] Generated for user {SYSTEM_USER_ID}")
    except Exception as e:
        print(f"[Weekly Report] Error: {e}")

def generate_reflection_reminder():
    """Remind user to reflect."""
    token = get_push_token(SYSTEM_USER_ID)
    if token:
        send_push_notification(
            SYSTEM_USER_ID,
            "🧠 Weekly Reflection",
            "Take 5 minutes to reflect on your week. What went well?"
        )

# Add jobs to scheduler
scheduler.add_job(generate_daily_lockin, 'cron', hour=7, minute=30, id='daily_lockin_730')
scheduler.add_job(generate_daily_lockin, 'cron', hour=14, minute=50, id='daily_lockin_1450')
scheduler.add_job(generate_daily_lockin, 'cron', hour=19, minute=30, id='daily_lockin_1930')
scheduler.add_job(generate_daily_lockin, 'cron', hour=17, minute=15, id='daily_lockin_1715')
scheduler.add_job(generate_daily_lockin, 'cron', hour=20, minute=30, id='daily_lockin_2030')
scheduler.add_job(generate_daily_lockin, 'cron', hour=21, minute=5, id='daily_lockin_2105')

scheduler.add_job(generate_morning_quote, 'cron', hour=6, minute=15, id='morning_quote')
scheduler.add_job(generate_wind_down_quote, 'cron', hour=22, minute=30, id='wind_down_quote')
scheduler.add_job(generate_weekly_report, 'cron', day_of_week='sun', hour=18, minute=0, id='weekly_report')
scheduler.add_job(generate_reflection_reminder, 'cron', day_of_week='sun', hour=10, minute=0, id='reflection_reminder')

scheduler.start()

# --------------------------
# New Skill Endpoints
# --------------------------
@app.post("/skills/init")
async def init_skills(user_id: int = Depends(get_current_user_id)):
    """Initialize 4 core skills for the user."""
    init_core_skills(user_id)
    return {"status": "success", "message": "Core skills initialized"}

@app.get("/skills/all")
async def get_all_skills(user_id: int = Depends(get_current_user_id)):
    """Get all skills for user as a simple list for dropdown."""
    skills = get_user_skills_list(user_id)
    return {"status": "success", "skills": skills}

# --------------------------
# New Task Creation Endpoint
# --------------------------
@app.post("/tasks/create")
async def create_new_task(request: CreateTaskRequest, user_id: int = Depends(get_current_user_id)):
    """Create a new task with optional skill linking."""
    if not request.name or not request.day_of_week:
        raise HTTPException(status_code=400, detail="name and day_of_week are required")
    
    task_id = create_task(
        user_id,
        request.name,
        request.day_of_week,
        request.start_time or "",
        request.duration or "",
        request.skill_id
    )
    
    return {
        "status": "success",
        "message": "Task created successfully",
        "task_id": task_id
    }

# --------------------------
# Startup/Shutdown
# --------------------------
@app.on_event("startup")
async def startup_event():
    print("🚀 Roger AI Server Starting...")
    print(f"✅ Database initialized")
    print(f"✅ Single-user mode (user_id = {SYSTEM_USER_ID})")
    print(f"✅ Scheduler started with {len(scheduler.get_jobs())} daily jobs")
    print("✅ Ready to receive connections")

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Roger AI Server Shutting Down...")
    scheduler.shutdown()


