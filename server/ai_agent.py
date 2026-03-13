import os
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

TZ = timezone(timedelta(hours=1))  # CET is UTC+1

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "allam-2-7b"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def ask_roger(message: str) -> str:
    now = datetime.now(TZ).strftime("%A, %d %B %Y %H:%M %Z")

    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY not found in environment."

    # Full routine included
    prompt = f"""
You are Roger, a strict accountability coach.

RULES:
- Only output the final answer. NOTHING ELSE.
- Max 4 sentences. Be concise, motivating, strict.
- Base your advice on the current time and user's schedule.

Current time: {now}

User routine:
Mon: Coding 15:00-17:00 2H, Workout 17:15-18:45 1.5H, Content 19:00-19:30 30m, Guitar 20:30-21:30 1H, Blender 21:30-22:30 1H
Tue: Coding 15:00-17:00 2H, Workout 17:15-18:45 1.5H, Content 19:00-19:30 30m, Guitar 20:30-21:30 1H, Blender 21:30-22:30 1H
Wed: Coding 15:00-17:00 2H, Workout 17:15-18:45 1.5H, Content 19:00-19:45 45m, Guitar 20:30-21:30 1H, Blender 21:30-22:30 1H
Thu: Baking 15:30-16:45 1H15, Coding 17:00-19:00 2H, Workout 19:15-20:45 1.5H, Guitar 20:30-21:30 1H, Blender 21:30-22:30 1H
Fri: Coding 15:00-17:00 2H, Workout 17:15-18:45 1.5H, Content 19:00-19:30 30m, Guitar 20:30-21:30 1H, Blender 21:30-22:30 1H
Sat: Coding 15:00-17:00 2H, Workout 17:15-18:45 1.5H, Singing 18:45-19:30 45m, Guitar 20:30-21:30 1H, Blender 21:30-22:30 1H, Content 22:30-22:50 20m
Sun: Coding 10:00-12:00 2H, Workout 14:00-15:30 1.5H, Singing 15:30-16:15 45m, Baking/Cooking 16:30-17:45 1H15, Content 18:00-18:45 45m, Guitar 20:30-21:30 1H, Blender 21:30-22:30 1H

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
        "temperature": 0.5,
        "max_tokens": 200  # limit output length to reduce token usage
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

if __name__ == "__main__":
    print(ask_roger("Hello Roger, what's our focus now?"))