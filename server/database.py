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
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Authentication tokens table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            day_of_week TEXT NOT NULL,
            start_time TEXT,
            duration TEXT,
            completed INTEGER DEFAULT 0,
            is_recurring INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            user_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            PRIMARY KEY (user_id, key),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            completed_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weeks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            completion_pct REAL,
            best_habit TEXT,
            weakest_habit TEXT,
            ai_advice TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            went_well TEXT NOT NULL,
            slowed_down TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            hours_practiced REAL DEFAULT 0.0,
            sessions_completed INTEGER DEFAULT 0,
            created_date TEXT NOT NULL,
            UNIQUE (user_id, name),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_id INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (skill_id) REFERENCES skills(id)
        )
    """)
    conn.commit()
    conn.close()

# --------------------------
# Tasks
# --------------------------
def get_tasks_for_day(user_id: int, day: str):
    """Returns (name, start_time, duration) for incomplete tasks on a given day."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, start_time, duration FROM tasks WHERE user_id = ? AND day_of_week = ? AND completed = 0",
        (user_id, day)
    )
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_tasks_for_today(user_id: int):
    """Return all of today's tasks with IDs and completion status."""
    day = datetime.now().strftime("%A")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, start_time, duration, completed FROM tasks WHERE user_id = ? AND day_of_week = ? ORDER BY start_time",
        (user_id, day)
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

def complete_task(user_id: int, task_id: int):
    """Mark a task as completed and log it in the completions table. Also update skill progress."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()
    # Get task name first (verify it belongs to user)
    cursor.execute("SELECT name FROM tasks WHERE user_id = ? AND id = ?", (user_id, task_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    
    task_name = row["name"]
    
    # Auto-link skill by name matching (extract keyword from task name)
    cursor.execute("SELECT id FROM skills WHERE user_id = ?", (user_id,))
    skills = cursor.fetchall()
    for skill_row in skills:
        skill_id = skill_row["id"]
        cursor.execute("SELECT name FROM skills WHERE id = ?", (skill_id,))
        skill_name_row = cursor.fetchone()
        if skill_name_row and skill_name_row["name"].lower() in task_name.lower():
            # Auto-link this skill
            cursor.execute(
                "INSERT OR IGNORE INTO task_skills (user_id, task_id, skill_id) VALUES (?, ?, ?)",
                (user_id, task_id, skill_id)
            )
    
    cursor.execute("UPDATE tasks SET completed = 1 WHERE user_id = ? AND id = ?", (user_id, task_id))
    cursor.execute(
        "INSERT INTO completions (user_id, task_id, task_name, completed_date) VALUES (?, ?, ?, ?)",
        (user_id, task_id, task_name, today)
    )
    conn.commit()
    conn.close()
    
    # Update skill progress (default 1 hour per task completion)
    update_skill_on_completion(user_id, task_id, hours=1.0)
    
    return True

def delete_task(user_id: int, task_id: int) -> bool:
    """Delete a task and its associated skill links. Returns True if successful, False if task not found."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify task belongs to user
    cursor.execute("SELECT id FROM tasks WHERE user_id = ? AND id = ?", (user_id, task_id))
    if not cursor.fetchone():
        conn.close()
        return False
    
    # Delete task and associated skill links
    cursor.execute("DELETE FROM task_skills WHERE task_id = ?", (task_id,))
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    
    conn.commit()
    conn.close()
    return True

def get_today_stats(user_id: int):
    """Return planned/completed counts and discipline score for today."""
    day = datetime.now().strftime("%A")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM tasks WHERE user_id = ? AND day_of_week = ?", (user_id, day))
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) as done FROM tasks WHERE user_id = ? AND day_of_week = ? AND completed = 1", (user_id, day))
    done = cursor.fetchone()["done"]
    conn.close()
    score = round(done / total, 2) if total > 0 else 0.0
    return {"planned": total, "completed": done, "score": score}

def reset_daily_tasks(user_id: int):
    """Reset all tasks to incomplete each day at midnight."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET completed = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Daily tasks reset for user {user_id}.")

def get_all_tasks(user_id: int):
    """Return all tasks grouped by day, ordered by start_time."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    conn = get_db_connection()
    cursor = conn.cursor()
    schedule = {}
    for day in days:
        cursor.execute(
            "SELECT name, start_time, duration FROM tasks WHERE user_id = ? AND day_of_week = ? ORDER BY start_time",
            (user_id, day)
        )
        rows = cursor.fetchall()
        if rows:
            schedule[day] = [(r["name"], r["start_time"], r["duration"]) for r in rows]
    conn.close()
    return schedule

def add_task(user_id: int, name: str, day_of_week: str, start_time: str, duration: str, skill_name: str = None, is_recurring: bool = True):
    """Add a task for a user, optionally linking it to a skill. is_recurring=True repeats weekly, False is one-time only."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, name, day_of_week, start_time, duration, is_recurring) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, name, day_of_week, start_time, duration, 1 if is_recurring else 0)
    )
    conn.commit()
    task_id = cursor.lastrowid
    
    # Link to skill if provided
    if skill_name:
        cursor.execute(
            "SELECT id FROM skills WHERE user_id = ? AND LOWER(name) = LOWER(?)",
            (user_id, skill_name)
        )
        skill_row = cursor.fetchone()
        if skill_row:
            skill_id = skill_row["id"]
            cursor.execute(
                "INSERT INTO task_skills (user_id, task_id, skill_id) VALUES (?, ?, ?)",
                (user_id, task_id, skill_id)
            )
            conn.commit()
    
    conn.close()

# --------------------------
# Messages
# --------------------------
def save_message(user_id: int, role: str, content: str):
    """Persist a chat message. role is 'user' or 'roger'."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, role, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_messages(user_id: int, limit: int = 100):
    """Return the last N messages ordered oldest-first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, timestamp FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    # Reverse so oldest is first (chronological order for the UI)
    return [{"role": r["role"], "content": r["content"], "time": r["timestamp"]} for r in reversed(rows)]

# --------------------------
# Push token
# --------------------------
def save_push_token(user_id: int, token: str):
    """Saves the Expo push token for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO settings (user_id, key, value) VALUES (?, 'push_token', ?)",
        (user_id, token)
    )
    conn.commit()
    conn.close()

def get_push_token(user_id: int):
    """Retrieves the Expo push token for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE user_id = ? AND key = 'push_token'", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result["value"] if result else None

# --------------------------
# Weekly Reports
# --------------------------
def get_weekly_stats(user_id: int):
    """Return aggregated stats for the past 7 days."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Total scheduled per habit per week (from tasks table)
    cursor.execute("SELECT name, COUNT(*) as scheduled FROM tasks WHERE user_id = ? GROUP BY name", (user_id,))
    scheduled_rows = cursor.fetchall()
    scheduled_map = {r["name"]: r["scheduled"] for r in scheduled_rows}
    
    # 2. Total completed per habit in the last 7 days
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    cursor.execute(
        "SELECT task_name, COUNT(*) as completed FROM completions WHERE user_id = ? AND completed_date >= ? GROUP BY task_name",
        (user_id, seven_days_ago)
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

def save_weekly_report(user_id: int, start_date: str, end_date: str, completion_pct: float, best_habit: str, weakest_habit: str, ai_advice: str):
    """Persist a weekly report to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO weeks (user_id, start_date, end_date, completion_pct, best_habit, weakest_habit, ai_advice) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, start_date, end_date, completion_pct, best_habit, weakest_habit, ai_advice)
    )
    conn.commit()
    conn.close()

# --------------------------
# Reflections
# --------------------------
def save_reflection(user_id: int, went_well: str, slowed_down: str):
    """Save a weekly reflection."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reflections (user_id, went_well, slowed_down, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, went_well, slowed_down, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_recent_reflections(user_id: int, limit: int = 3):
    """Get the most recent reflections to provide context to the AI."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT went_well, slowed_down, timestamp FROM reflections WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_reflections(user_id: int, limit: int = 10):
    """Get reflection history for user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT went_well, slowed_down, timestamp FROM reflections WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --------------------------
# Skills Tracking
# --------------------------
def create_or_get_skill(user_id: int, skill_name: str):
    """Create a skill if it doesn't exist, return its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM skills WHERE user_id = ? AND name = ?", (user_id, skill_name))
    row = cursor.fetchone()
    
    if row:
        conn.close()
        return row["id"]
    
    # Create new skill
    cursor.execute(
        "INSERT INTO skills (user_id, name, created_date) VALUES (?, ?, ?)",
        (user_id, skill_name, datetime.now().strftime("%Y-%m-%d"))
    )
    conn.commit()
    skill_id = cursor.lastrowid
    conn.close()
    return skill_id

def link_task_to_skill(user_id: int, task_id: int, skill_id: int):
    """Link a task to a skill."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if already linked
    cursor.execute(
        "SELECT id FROM task_skills WHERE user_id = ? AND task_id = ? AND skill_id = ?",
        (user_id, task_id, skill_id)
    )
    if cursor.fetchone():
        conn.close()
        return  # Already linked
    
    cursor.execute(
        "INSERT INTO task_skills (user_id, task_id, skill_id) VALUES (?, ?, ?)",
        (user_id, task_id, skill_id)
    )
    conn.commit()
    conn.close()

def update_skill_on_completion(user_id: int, task_id: int, hours: float = 1.0):
    """Update skill progress when task is completed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get skills linked to this task
    cursor.execute(
        "SELECT skill_id FROM task_skills WHERE user_id = ? AND task_id = ?",
        (user_id, task_id)
    )
    skill_rows = cursor.fetchall()
    
    # Update each linked skill
    for skill_row in skill_rows:
        skill_id = skill_row["skill_id"]
        cursor.execute(
            "UPDATE skills SET hours_practiced = hours_practiced + ?, sessions_completed = sessions_completed + 1 WHERE id = ?",
            (hours, skill_id)
        )
    
    conn.commit()
    conn.close()

def get_user_skills(user_id: int):
    """Get all skills and their progress for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, name, hours_practiced, sessions_completed, created_date FROM skills WHERE user_id = ? ORDER BY hours_practiced DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(r) for r in rows]

def get_skill_stats(user_id: int, skill_id: int):
    """Get detailed stats for a specific skill."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, name, hours_practiced, sessions_completed, created_date FROM skills WHERE user_id = ? AND id = ?",
        (user_id, skill_id)
    )
    skill_row = cursor.fetchone()
    
    if not skill_row:
        conn.close()
        return None
    
    skill = dict(skill_row)
    
    # Get related tasks
    cursor.execute(
        "SELECT DISTINCT t.name FROM tasks t WHERE id IN (SELECT task_id FROM task_skills WHERE skill_id = ? AND user_id = ?)",
        (skill_id, user_id)
    )
    related_tasks = [row["name"] for row in cursor.fetchall()]
    skill["related_tasks"] = related_tasks
    
    conn.close()
    return skill

def init_core_skills(user_id: int):
    """Initialize 6 core skills for a new user: Coding, Guitar, Blender, Fitness, Singing, Content Creation."""
    core_skills = ["Coding", "Guitar", "Blender", "Fitness", "Singing", "Content Creation"]
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for skill_name in core_skills:
        cursor.execute(
            "INSERT OR IGNORE INTO skills (user_id, name, hours_practiced, sessions_completed, created_date) VALUES (?, ?, 0.0, 0, ?)",
            (user_id, skill_name, datetime.now().strftime("%Y-%m-%d"))
        )
    
    conn.commit()
    conn.close()

def get_user_skills_list(user_id: int):
    """Get all skills for user as a simple list with id and name. Auto-initializes if missing."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user has any skills
    cursor.execute("SELECT COUNT(*) as count FROM skills WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()["count"]
    
    # If no skills exist, initialize them
    if count == 0:
        conn.close()
        init_core_skills(user_id)
        conn = get_db_connection()
        cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, name FROM skills WHERE user_id = ? ORDER BY name",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(r) for r in rows]

def create_task(user_id: int, name: str, day_of_week: str, start_time: str = "", duration: str = "", skill_id: int = None, is_recurring: bool = True):
    """Create a new task with optional skill linking. is_recurring=True repeats weekly, False is one-time only."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO tasks (user_id, name, day_of_week, start_time, duration, is_recurring) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, name, day_of_week, start_time, duration, 1 if is_recurring else 0)
    )
    conn.commit()
    task_id = cursor.lastrowid
    
    # Link to skill if provided
    if skill_id:
        cursor.execute(
            "INSERT INTO task_skills (user_id, task_id, skill_id) VALUES (?, ?, ?)",
            (user_id, task_id, skill_id)
        )
        conn.commit()
    
    conn.close()
    return task_id


