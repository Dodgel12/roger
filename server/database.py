import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "roger.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create all tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            day_of_week TEXT NOT NULL,
            start_time TEXT,
            duration TEXT,
            completed INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            completed_date TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weeks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            completion_pct REAL,
            best_habit TEXT,
            weakest_habit TEXT,
            ai_advice TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            went_well TEXT NOT NULL,
            slowed_down TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# --------------------------
# Tasks
# --------------------------
def get_tasks_for_day(day):
    """Returns (name, start_time, duration) for incomplete tasks on a given day."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, start_time, duration FROM tasks WHERE day_of_week = ? AND completed = 0", (day,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_tasks_for_today():
    """Return all of today's tasks with IDs and completion status."""
    day = datetime.now().strftime("%A")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, start_time, duration, completed FROM tasks WHERE day_of_week = ? ORDER BY start_time",
        (day,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "start_time": r["start_time"],
            "duration": r["duration"],
            "completed": bool(r["completed"])
        }
        for r in rows
    ]

def complete_task(task_id: int):
    """Mark a task as completed and log it in the completions table."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()
    # Get task name first
    cursor.execute("SELECT name FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    cursor.execute(
        "INSERT INTO completions (task_id, task_name, completed_date) VALUES (?, ?, ?)",
        (task_id, row["name"], today)
    )
    conn.commit()
    conn.close()
    return True

def get_today_stats():
    """Return planned/completed counts and discipline score for today."""
    day = datetime.now().strftime("%A")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM tasks WHERE day_of_week = ?", (day,))
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) as done FROM tasks WHERE day_of_week = ? AND completed = 1", (day,))
    done = cursor.fetchone()["done"]
    conn.close()
    score = round(done / total, 2) if total > 0 else 0.0
    return {"planned": total, "completed": done, "score": score}

def reset_daily_tasks():
    """Reset all tasks to incomplete each day at midnight."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET completed = 0")
    conn.commit()
    conn.close()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Daily tasks reset.")

def get_all_tasks():
    """Return all tasks grouped by day, ordered by start_time."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    conn = get_db_connection()
    cursor = conn.cursor()
    schedule = {}
    for day in days:
        cursor.execute(
            "SELECT name, start_time, duration FROM tasks WHERE day_of_week = ? ORDER BY start_time",
            (day,)
        )
        rows = cursor.fetchall()
        if rows:
            schedule[day] = [(r["name"], r["start_time"], r["duration"]) for r in rows]
    conn.close()
    return schedule

def add_task(name, day_of_week, start_time, duration):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (name, day_of_week, start_time, duration) VALUES (?, ?, ?, ?)",
        (name, day_of_week, start_time, duration)
    )
    conn.commit()
    conn.close()

# --------------------------
# Messages
# --------------------------
def save_message(role: str, content: str):
    """Persist a chat message. role is 'user' or 'roger'."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (role, content, timestamp) VALUES (?, ?, ?)",
        (role, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_messages(limit: int = 100):
    """Return the last N messages ordered oldest-first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, timestamp FROM messages ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    # Reverse so oldest is first (chronological order for the UI)
    return [{"role": r["role"], "content": r["content"], "time": r["timestamp"]} for r in reversed(rows)]

# --------------------------
# Push token
# --------------------------
def save_push_token(token):
    """Saves the Expo push token."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('push_token', ?)", (token,))
    conn.commit()
    conn.close()

def get_push_token():
    """Retrieves the Expo push token."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'push_token'")
    result = cursor.fetchone()
    conn.close()
    return result["value"] if result else None

# --------------------------
# Weekly Reports
# --------------------------
def get_weekly_stats():
    """Return aggregated stats for the past 7 days."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Total scheduled per habit per week (from tasks table)
    cursor.execute("SELECT name, COUNT(*) as scheduled FROM tasks GROUP BY name")
    scheduled_rows = cursor.fetchall()
    scheduled_map = {r["name"]: r["scheduled"] for r in scheduled_rows}
    
    # 2. Total completed per habit in the last 7 days
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    cursor.execute(
        "SELECT task_name, COUNT(*) as completed FROM completions WHERE completed_date >= ? GROUP BY task_name",
        (seven_days_ago,)
    )
    completed_rows = cursor.fetchall()
    completed_map = {r["task_name"]: r["completed"] for r in completed_rows}
    
    conn.close()
    
    total_scheduled = sum(scheduled_map.values())
    total_completed = 0
    best_habit = ("None", -1.0) # name, pct
    weakest_habit = ("None", 2.0) # name, pct
    
    for name, sched in scheduled_map.items():
        comp = completed_map.get(name, 0)
        total_completed += comp
        pct = comp / sched if sched > 0 else 0.0
        
        if pct > best_habit[1]:
            best_habit = (name, pct)
        if pct < weakest_habit[1]:
            weakest_habit = (name, pct)
            
    overall_pct = total_completed / total_scheduled if total_scheduled > 0 else 0.0
    
    return {
        "start_date": seven_days_ago,
        "end_date": datetime.now().strftime("%Y-%m-%d"),
        "completion_pct": overall_pct,
        "best_habit": best_habit[0] if total_scheduled > 0 else "None",
        "weakest_habit": weakest_habit[0] if total_scheduled > 0 else "None",
    }

def save_weekly_report(start_date, end_date, completion_pct, best_habit, weakest_habit, ai_advice):
    """Persist a weekly report to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO weeks (start_date, end_date, completion_pct, best_habit, weakest_habit, ai_advice) VALUES (?, ?, ?, ?, ?, ?)",
        (start_date, end_date, completion_pct, best_habit, weakest_habit, ai_advice)
    )
    conn.commit()
    conn.close()

# --------------------------
# Reflections
# --------------------------
def save_reflection(went_well: str, slowed_down: str):
    """Save a weekly reflection."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reflections (went_well, slowed_down, timestamp) VALUES (?, ?, ?)",
        (went_well, slowed_down, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_recent_reflections(limit: int = 3):
    """Get the most recent reflections to provide context to the AI."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT went_well, slowed_down, timestamp FROM reflections ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

