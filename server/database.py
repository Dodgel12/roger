schedule = {
    "Monday": [
        ("Coding", "15:00", "17:00"),
        ("Workout", "17:15", "18:45")
    ],
    "Tuesday": [
        ("Coding", "15:00", "17:00"),
        ("Workout", "17:15", "18:45")
    ]
}

def get_tasks_for_day(day):

    return schedule.get(day, [])
