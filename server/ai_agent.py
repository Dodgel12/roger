import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from database import get_all_tasks, get_tasks_for_day, get_today_stats, get_recent_reflections, get_weekly_stats

try:
    from database import get_app_now
except ImportError:
    def get_app_now():
        """Fallback for older database.py versions that do not expose get_app_now."""
        return datetime.now().astimezone()

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "allam-2-7b"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def build_schedule_string(user_id: int) -> str:
    """Build a compact schedule string from live DB data."""
    schedule = get_all_tasks(user_id)
    if not schedule:
        return "No tasks currently scheduled."

    lines = []
    day_abbr = {
        "Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed",
        "Thursday": "Thu", "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"
    }
    for day, tasks in schedule.items():
        task_parts = [f"{name} {start} {dur}" for name, start, dur in tasks]
        lines.append(f"{day_abbr.get(day, day)}: {', '.join(task_parts)}")
    return "\n".join(lines)

def build_stats_string(user_id: int) -> str:
    """Build a string showing today's task discipline score."""
    stats = get_today_stats(user_id)
    planned = stats["planned"]
    completed = stats["completed"]
    if planned == 0:
        return "No tasks scheduled for today."
    
    percent = int(stats["score"] * 100)
    return f"Today's completion: {completed}/{planned} tasks ({percent}%)"


def build_today_tasks_string(user_id: int, today_name: str) -> str:
    """Build explicit today-only task list to avoid day confusion in model responses."""
    tasks = get_tasks_for_day(user_id, today_name)
    if not tasks:
        return f"No tasks scheduled for {today_name}."

    items = [f"- {name} at {start or 'unspecified time'} for {dur or 'unspecified duration'}" for name, start, dur in tasks]
    return "\n".join(items)

def build_reflections_string(user_id: int) -> str:
    """Build a string from recent reflections for AI context."""
    reflections = get_recent_reflections(user_id, 3)
    if not reflections:
        return "No past reflections available yet."
    
    parts = []
    for r in reflections:
        parts.append(f"- On {r['timestamp']}: 'Went well: {r['went_well']}', 'Slowed down: {r['slowed_down']}'")
    return "\n".join(parts)


def _is_today_tasks_query(message: str) -> bool:
    """Detect user intents asking for today's/remaining tasks."""
    msg = message.lower()
    today_words = ("today", "todays", "today's")
    task_words = ("task", "tasks", "schedule", "remaining", "remain", "left")
    return any(w in msg for w in today_words) and any(w in msg for w in task_words)


def build_remaining_tasks_reply(user_id: int, today_name: str) -> str:
    """Generate deterministic reply for today's remaining tasks from DB."""
    tasks = get_tasks_for_day(user_id, today_name)
    if not tasks:
        return f"You have no remaining tasks for {today_name}. Use this time intentionally and plan your next win."

    lines = [f"Remaining tasks for {today_name}:\n"]
    for name, start, dur in tasks:
        start_txt = start if start else "unspecified time"
        dur_txt = dur if dur else "unspecified duration"
        lines.append(f"- {name} at {start_txt} for {dur_txt}")
    lines.append("Stay sharp: finish these one by one.")
    return "\n".join(lines)

def ask_roger(user_id: int, message: str) -> str:
    now_dt = get_app_now()
    now = now_dt.strftime("%A, %d %B %Y %H:%M %Z")
    today_name = now_dt.strftime("%A")

    if _is_today_tasks_query(message):
        return build_remaining_tasks_reply(user_id, today_name)

    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY not found in environment."

    # Build live schedule from DB
    schedule = build_schedule_string(user_id)
    stats_str = build_stats_string(user_id)
    today_tasks_str = build_today_tasks_string(user_id, today_name)
    reflections_str = build_reflections_string(user_id)

    prompt = f"""
You are Roger, an accountability coach.

RULES:
- Only output the final answer. NOTHING ELSE.
- Be concise, motivating.
- Base your advice on the current time and user's schedule.
- Use the user's past reflections to give highly personalized, targeted advice.
- If the user asks for "today" or "today's tasks", use ONLY the explicit Today's Tasks list below.

Current time: {now}
Today is: {today_name}
{stats_str}

Today's Tasks:
{today_tasks_str}

User's past reflections:
{reflections_str}

User routine:
{schedule}

User message: {message}
"""


    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are Roger, a strict accountability coach."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=12)
        response.raise_for_status()
        result = response.json()
        response_text = result['choices'][0]['message']['content'].strip()

        # Remove filler text
        cleaned_lines = [
            line.strip() for line in response_text.split("\n")
            if line.strip() and not line.lower().startswith(("okay", "first", "then", "<think>"))
        ]

        if not cleaned_lines:
            return "Roger returned an empty response."

        return " ".join(cleaned_lines)

    except requests.exceptions.Timeout:
        return "Roger is taking too long to think (API Timeout)."
    except requests.exceptions.HTTPError as e:
        return f"Roger is unavailable (API Error {response.status_code})."
    except Exception as e:
        return f"Roger is unavailable right now. Unexpected Error: {str(e)}"


def generate_weekly_analysis(user_id: int) -> str:
    """Generate AI-powered weekly analysis and advice."""
    now = get_app_now().strftime("%A, %d %B %Y")

    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY not found in environment."

    # Get weekly stats
    weekly_stats = get_weekly_stats(user_id)
    completion_pct = int(weekly_stats["completion_pct"] * 100)
    best_habit = weekly_stats["best_habit"]
    weakest_habit = weekly_stats["weakest_habit"]

    # Get recent reflections for context
    reflections_str = build_reflections_string(user_id)

    prompt = f"""
You are Roger, a strict accountability coach providing WEEKLY ANALYSIS.

RULES:
- Output ONLY the final analysis. NOTHING ELSE.
- Exactly 3 short sentences.
- Be honest, motivating, and actionable.
- Reference the completion %, best habit, and weakest habit.
- Provide specific, tactical advice for next week.

Weekly Report:
- Overall Completion: {completion_pct}%
- Best Habit: {best_habit}
- Weakest Habit: {weakest_habit}

Recent Reflections:
{reflections_str}

Generate a weekly analysis with praise, constructive feedback, and 1 specific action for next week.
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are Roger, a strict accountability coach."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=12)
        response.raise_for_status()
        result = response.json()
        response_text = result['choices'][0]['message']['content'].strip()

        return response_text

    except requests.exceptions.Timeout:
        return "Roger is taking too long to analyze the week."
    except requests.exceptions.HTTPError as e:
        return f"Roger is unavailable (API Error {response.status_code})."
    except Exception as e:
        return f"Error generating analysis: {str(e)}"

