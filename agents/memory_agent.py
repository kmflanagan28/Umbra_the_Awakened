import sqlite3
import datetime
import random
import os
import sys

# Add the parent directory to the path to find the 'config' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def _get_db_connection():
    """Helper function to get a database connection."""
    conn = sqlite3.connect(config.MEMORY_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    """Sets up the database tables if they don't exist."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    # Check if the 'category' column exists
    cursor.execute("PRAGMA table_info(memories)")
    columns = [row['name'] for row in cursor.fetchall()]
    
    if 'category' not in columns:
        print("Upgrading memories database to include 'category' column...")
        # To keep old data, we would need a more complex migration.
        # For simplicity in this project, we'll recreate the table.
        cursor.execute("DROP TABLE IF EXISTS memories")
        cursor.execute('''
            CREATE TABLE memories (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                category TEXT NOT NULL,
                memory TEXT NOT NULL
            )
        ''')
    else:
         cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                category TEXT NOT NULL,
                memory TEXT NOT NULL
            )
        ''')
    
    conn.commit()
    conn.close()

# Ensure the database is set up when the module is imported
setup_database()

def add_memory(text_to_log: str, category: str):
    """
    This is a 'Tool' function.
    It takes a string of text and a category and logs it to the database.
    This version is updated to explicitly add the timestamp.
    """
    conn = _get_db_connection()
    try:
        current_timestamp = datetime.datetime.now().isoformat()
        conn.execute(
            'INSERT INTO memories (timestamp, category, memory) VALUES (?, ?, ?)',
            (current_timestamp, category, text_to_log)
        )
        conn.commit()
        print("\n💾 Memory stored in the database.")
    except Exception as e:
        print(f"\nError adding memory to database: {e}")
    finally:
        conn.close()


def search_memories(keyword: str):
    """
    This is a 'Tool' function.
    It searches the memory database for a specific keyword.
    """
    conn = _get_db_connection()
    cursor = conn.execute('SELECT * FROM memories WHERE memory LIKE ? ORDER BY timestamp DESC', (f'%{keyword}%',))
    memories = cursor.fetchall()
    conn.close()

    if not memories:
        return f"No memories found containing the keyword: '{keyword}'"
    
    result = f"Found {len(memories)} memories containing '{keyword}':\n"
    for row in memories:
        timestamp = datetime.datetime.fromisoformat(row['timestamp']).strftime('%Y-%m-%d %H:%M')
        result += f"- [{timestamp}] {row['memory']}\n"
    return result

def get_daily_memory_insight():
    """
    Gets a random, insightful memory from the database for the daily briefing.
    It prioritizes user thoughts and system learnings over simple interactions.
    """
    conn = _get_db_connection()
    # Prioritize more "thoughtful" categories
    cursor = conn.execute(
        "SELECT * FROM memories WHERE category IN ('Manual Log', 'System Learning', 'User Conversation') ORDER BY RANDOM() LIMIT 1"
    )
    thoughtful_memory = cursor.fetchone()

    if thoughtful_memory:
        memory_row = thoughtful_memory
    else:
        # Fallback to any random memory if no "thoughtful" ones are found
        cursor = conn.execute("SELECT * FROM memories ORDER BY RANDOM() LIMIT 1")
        memory_row = cursor.fetchone()

    conn.close()

    if not memory_row:
        return "No memories in the archives yet."

    timestamp = datetime.datetime.fromisoformat(memory_row['timestamp'])
    day_of_week = timestamp.strftime('%A, %B %d, %Y')
    memory_text = memory_row['memory']

    # Clean up the memory text for the briefing
    if memory_text.startswith("User Prompt:"):
        parts = memory_text.split('|')
        memory_text = parts[0].strip()

    return f"On {day_of_week}, you were thinking about:\n- \"{memory_text}\""