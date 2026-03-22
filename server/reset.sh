#!/bin/bash

#Go to the roger-server directory
cd ~/roger/server

#DELETES all rows from messages!
sqlite3 roger.db "DELETE FROM messages;"

#DELETES all rows from reflections!
sqlite3 roger.db "DELETE FROM reflections;"

#DELETES all rows from completions!
sqlite3 roger.db "DELETE FROM completions;"

#DELETES all rows from weeks!
sqlite3 roger.db "DELETE FROM weeks;"

#DELETE all rows from tasks!
sqlite3 roger.db "DELETE FROM tasks;"

