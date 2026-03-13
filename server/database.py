import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "roger.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def get_tasks_for_day(day):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, start_time, duration FROM tasks WHERE day_of_week = ? AND completed = 0", (day,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def add_task(name, day_of_week, start_time, duration):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (name, day_of_week, start_time, duration) VALUES (?, ?, ?, ?)",
        (name, day_of_week, start_time, duration)
    )
    conn.commit()
    conn.close()

def save_push_token(token):
    """Saves the Expo push token to a simple table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('push_token', ?)", (token,))
    conn.commit()
    conn.close()

def get_push_token():
    """Retrieves the Expo push token."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("SELECT value FROM settings WHERE key = 'push_token'")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
