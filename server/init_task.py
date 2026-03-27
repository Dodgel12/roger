from database import add_task

# System user ID (single user setup)
USER_ID = 1

# MONDAY
add_task(USER_ID, "Bus Morning - Music Theory (Il manuale di teoria musicale, read 1-2 pages + mentally apply on guitar)", "Monday", "06:15", "1H", "Guitar")
add_task(USER_ID, "School", "Monday", "08:00", "5H 20m")
add_task(USER_ID, "Bus Afternoon - Startup microthinking (ideas, features, reflections, write 5 lines)", "Monday", "13:26", "1H", "Coding")
add_task(USER_ID, "Workout", "Monday", "17:15", "1.5H", "Fitness")
add_task(USER_ID, "CS Reading - Clean Code (read + apply 1 concept to your project)", "Monday", "19:00", "1H", "Coding")
add_task(USER_ID, "Guitar - Practice + music theory application (scales/chords)", "Monday", "20:30", "1H", "Guitar")
add_task(USER_ID, "Blender - Modeling fundamentals (create 1-2 props, focus on topology)", "Monday", "21:30", "1H", "Blender")

# TUESDAY
add_task(USER_ID, "Bus Morning - CS review (A Common-Sense Guide to DS & Algorithms, skim 1 topic)", "Tuesday", "06:15", "1H", "Coding")
add_task(USER_ID, "School", "Tuesday", "08:00", "5H 20m")
add_task(USER_ID, "Bus Afternoon - Mental problem solving (think through 1 algorithm problem)", "Tuesday", "13:26", "1H", "Coding")
add_task(USER_ID, "Startup - Market research / planning", "Tuesday", "16:30", "1H", "Coding")
add_task(USER_ID, "Workout", "Tuesday", "17:30", "1.5H", "Fitness")
add_task(USER_ID, "Guitar - Technique & creative practice (no theory)", "Tuesday", "19:00", "1H", "Guitar")
add_task(USER_ID, "Blender - Prop refinement (improve yesterday's models, focus on scale & proportions)", "Tuesday", "20:30", "1H", "Blender")

# WEDNESDAY
add_task(USER_ID, "Bus Morning - Music Theory (Il manuale di teoria musicale, read 1-2 pages + mentally apply)", "Wednesday", "06:15", "1H", "Guitar")
add_task(USER_ID, "School", "Wednesday", "08:00", "5H 20m")
add_task(USER_ID, "Bus Afternoon - Quick notes (write 5-10 lines about morning CS/music theory)", "Wednesday", "13:26", "1H", "Coding")
add_task(USER_ID, "Startup - Feature development", "Wednesday", "15:00", "2H", "Coding")
add_task(USER_ID, "Workout", "Wednesday", "17:15", "1.5H", "Fitness")
add_task(USER_ID, "CS Reading - A Common-Sense Guide to DS & Algorithms (read + implement 1 structure)", "Wednesday", "19:00", "1H", "Coding")
add_task(USER_ID, "Guitar - Practice + Music Theory application", "Wednesday", "20:30", "1H", "Guitar")
add_task(USER_ID, "Blender - Scene building (create room/outdoor scene, focus on scale & placement)", "Wednesday", "21:30", "1H", "Blender")

# THURSDAY
add_task(USER_ID, "Bus Morning - CS Concepts (review data structures / complexity mentally)", "Thursday", "06:15", "1H", "Coding")
add_task(USER_ID, "School", "Thursday", "08:00", "5H 20m")
add_task(USER_ID, "Bus Afternoon - Startup micro-tasks (messages, planning, reflections)", "Thursday", "13:26", "1H", "Coding")
add_task(USER_ID, "CS Learning - Data Structures (book, implement + test)", "Thursday", "15:00", "1.5H", "Coding")
add_task(USER_ID, "Startup - Outreach / networking", "Thursday", "16:30", "1H", "Coding")
add_task(USER_ID, "Workout", "Thursday", "17:30", "1.5H", "Fitness")
add_task(USER_ID, "Guitar - Practice (no theory)", "Thursday", "19:00", "1H", "Guitar")
add_task(USER_ID, "Blender - Lighting & materials (apply basic lighting + realistic materials)", "Thursday", "20:30", "1H", "Blender")

# FRIDAY
add_task(USER_ID, "Bus Morning - Light review (music theory or CS notes, easy 20-30 min)", "Friday", "06:15", "1H", "Coding")
add_task(USER_ID, "School", "Friday", "08:00", "5H 20m")
add_task(USER_ID, "Bus Afternoon - Free thinking / reflection", "Friday", "13:26", "1H", "Coding")
add_task(USER_ID, "Startup - Code / prototype", "Friday", "15:00", "2H", "Coding")
add_task(USER_ID, "Workout", "Friday", "17:15", "1.5H", "Fitness")
add_task(USER_ID, "CS Reading - Clean Code / Design Patterns (read + apply 1 concept)", "Friday", "19:00", "1H", "Coding")
add_task(USER_ID, "Guitar - Play + Enjoy (songs, creativity)", "Friday", "20:30", "1H", "Guitar")
add_task(USER_ID, "Blender - Animation basics (animate 1 simple action, 5-10s)", "Friday", "21:30", "1H", "Blender")

# SATURDAY
add_task(USER_ID, "Bus Morning - Music theory or CS light reading (optional if traveling)", "Saturday", "06:15", "1H", "Coding")
add_task(USER_ID, "School", "Saturday", "08:00", "0H")
add_task(USER_ID, "Bus Afternoon - Reflection / planning", "Saturday", "13:26", "1H", "Coding")
add_task(USER_ID, "Startup - Deep project build", "Saturday", "10:00", "2H", "Coding")
add_task(USER_ID, "CS Reading - Design Patterns (read + apply 1 pattern)", "Saturday", "12:00", "1H", "Coding")
add_task(USER_ID, "Startup - Product refinement (UI/UX + usability)", "Saturday", "15:00", "1.5H", "Coding")
add_task(USER_ID, "Workout", "Saturday", "16:30", "1.5H", "Fitness")
add_task(USER_ID, "Guitar - Creative + Music Theory (apply teoria musicale)", "Saturday", "18:00", "1H", "Guitar")
add_task(USER_ID, "Blender - Creative project (combine models + scene + animation)", "Saturday", "19:00", "1H", "Blender")

# SUNDAY
add_task(USER_ID, "CS Learning - System design / architecture", "Sunday", "10:00", "2H", "Coding")
add_task(USER_ID, "Startup - Weekly planning & goals", "Sunday", "12:00", "1H", "Coding")
add_task(USER_ID, "Workout", "Sunday", "14:00", "1.5H", "Fitness")
add_task(USER_ID, "Singing (optional creative)", "Sunday", "15:30", "45m", "Singing")
add_task(USER_ID, "Guitar - Light practice + theory review", "Sunday", "16:30", "1H", "Guitar")
add_task(USER_ID, "Blender - Review + improvement (focus on weakest skill: modeling/lighting/animation)", "Sunday", "17:30", "1H", "Blender")