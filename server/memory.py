import json
import os

MEMORY_FILE = "memory.json"

def load_memory():

    if not os.path.exists(MEMORY_FILE):

        memory = {
            "streak": 0,
            "missed_tasks": []
        }

        save_memory(memory)

        return memory

    with open(MEMORY_FILE) as f:
        return json.load(f)


def save_memory(memory):

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def add_missed_task(task):

    memory = load_memory()

    memory["missed_tasks"].append(task)

    save_memory(memory)


def increase_streak():

    memory = load_memory()

    memory["streak"] += 1

    save_memory(memory)


def reset_streak():

    memory = load_memory()

    memory["streak"] = 0

    save_memory(memory)
