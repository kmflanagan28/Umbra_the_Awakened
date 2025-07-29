import sys
import os
import sqlite3
import datetime
import random

# Add the parent directory to the path to find the 'config' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def _ensure_db_and_table_exist():
    """Ensures the database and the memories table exist."""
    conn = sqlite3.connect(config.MEMORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            memory TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_memory(text_to_log: str):
    """
    This is a 'Tool' function.
    It takes a string of text and logs it to the database with a timestamp.
    """
    _ensure_db_and_table_exist()
    conn = sqlite3.connect(config.MEMORY_DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO memories (timestamp, memory) VALUES (?, ?)", (timestamp, text_to_log))
    conn.commit()
    conn.close()
    print("\n💾 Memory stored in the database.")


def get_daily_memory_insight():
    """
    Pulls a single, random memory from the entire history to include in the briefing.
    """
    _ensure_db_and_table_exist()
    conn = sqlite3.connect(config.MEMORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, memory FROM memories")
    all_memories = cursor.fetchall()
    conn.close()

    if not all_memories:
        return "The memory archives are currently empty."

    # Select one random memory
    random_memory = random.choice(all_memories)
    timestamp_str, memory_text = random_memory
    
    # Format the timestamp for readability
    timestamp_obj = datetime.datetime.fromisoformat(timestamp_str)
    formatted_date = timestamp_obj.strftime('%A, %B %d, %Y')

    return f"On {formatted_date}, you were thinking about:\n- \"{memory_text}\""


def search_memories(keyword: str):
    """
    This is a 'Tool' function.
    It searches the database for memories containing a specific keyword.
    """
    _ensure_db_and_table_exist()
    conn = sqlite3.connect(config.MEMORY_DB_PATH)
    cursor = conn.cursor()
    # Use the LIKE operator for partial matching, case-insensitive
    cursor.execute("SELECT timestamp, memory FROM memories WHERE memory LIKE ?", (f'%{keyword}%',))
    results = cursor.fetchall()
    conn.close()

    if not results:
        return f"No memories found containing the keyword: '{keyword}'"

    formatted_results = f"Found {len(results)} memories containing '{keyword}':\n"
    for timestamp, memory in results:
        date_obj = datetime.datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M')
        formatted_results += f"- [{date_obj}] {memory}\n"
    
    return formatted_results