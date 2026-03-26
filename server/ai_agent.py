import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from database import get_all_tasks, get_today_stats, get_recent_reflections, get_weekly_stats

TZ = timezone(timedelta(hours=1))  # CET is UTC+1

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

def build_reflections_string(user_id: int) -> str:
    """Build a string from recent reflections for AI context."""
    reflections = get_recent_reflections(user_id, 3)
    if not reflections:
        return "No past reflections available yet."
    
    parts = []
    for r in reflections:
        parts.append(f"- On {r['timestamp']}: 'Went well: {r['went_well']}', 'Slowed down: {r['slowed_down']}'")
    return "\n".join(parts)

def ask_roger(user_id: int, message: str) -> str:
    now = datetime.now(TZ).strftime("%A, %d %B %Y %H:%M %Z")

    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY not found in environment."

    # Build live schedule from DB
    schedule = build_schedule_string(user_id)
    stats_str = build_stats_string(user_id)
    reflections_str = build_reflections_string(user_id)

    prompt = f"""
You are Roger, a strict accountability coach.

RULES:
- Only output the final answer. NOTHING ELSE.
- Max 4 sentences. Be concise, motivating, strict.
- Base your advice on the current time and user's schedule.
- Use the user's past reflections to give highly personalized, targeted advice.

Current time: {now}
{stats_str}

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
    now = datetime.now(TZ).strftime("%A, %d %B %Y")

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

