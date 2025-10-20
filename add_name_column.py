"""
Simple migration to add name column to users table
Run this once to update the database schema
"""

import sqlite3
import os

def add_name_column():
    """Add name column to users table if it doesn't exist"""
    db_path = "inventory.db"
    
    if not os.path.exists(db_path):
        print("Database file not found. Please run the main application first.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if name column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'name' not in columns:
            print("Adding name column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")
            conn.commit()
            print("✅ Successfully added name column to users table")
        else:
            print("✅ name column already exists in users table")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_name_column()
