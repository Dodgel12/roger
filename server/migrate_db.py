#!/usr/bin/env python3
"""
Database Migration Script
Updates the database schema to include the settings table with user_id column
"""

import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), "roger.db")

def migrate_database():
    """Migrate database to add missing settings table"""
    
    print("=" * 60)
    print("🔧 DATABASE MIGRATION")
    print("=" * 60)
    print()
    
    if not os.path.exists(DB_PATH):
        print("❌ Database file not found at:", DB_PATH)
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if settings table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='settings'
        """)
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Check if user_id column exists
            cursor.execute("PRAGMA table_info(settings)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'user_id' in columns:
                print("✅ Settings table is already up to date")
                conn.close()
                return True
            else:
                print("⚠️  Settings table exists but is missing user_id column")
                print("🔨 Recreating settings table...")
                
                # Backup old data
                cursor.execute("SELECT * FROM settings")
                old_data = cursor.fetchall()
                
                # Drop and recreate
                cursor.execute("DROP TABLE settings")
                cursor.execute("""
                    CREATE TABLE settings (
                        user_id INTEGER NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT,
                        PRIMARY KEY (user_id, key),
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """)
                
                print("   ✅ Settings table recreated")
        else:
            print("⚠️  Settings table does not exist")
            print("🔨 Creating settings table...")
            
            cursor.execute("""
                CREATE TABLE settings (
                    user_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    PRIMARY KEY (user_id, key),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            print("   ✅ Settings table created")
        
        conn.commit()
        conn.close()
        print()
        print("✅ DATABASE MIGRATION COMPLETE")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
