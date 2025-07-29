import sqlite3
import os
import sys
import datetime

# Add the parent directory to the path to find the 'config' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def init_db():
    """Initializes the database and creates the 'memories' table if it doesn't exist."""
    conn = sqlite3.connect(config.MEMORY_DB_PATH)
    cursor = conn.cursor()
    # Create table with a timestamp and the memory text content
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            memory TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_memory(text_to_log: str):
    """
    This is a 'Tool' function.
    It takes a string of text and logs it to the database with a timestamp.
    """
    init_db() # Ensure the database and table exist
    conn = sqlite3.connect(config.MEMORY_DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute("INSERT INTO memories (timestamp, memory) VALUES (?, ?)", (timestamp, text_to_log))
    
    conn.commit()
    conn.close()
    print("\n💾 Memory stored in the database.")

def read_recent_memories(num_memories: int = 5):
    """
    Reads the most recent memories from the database.
    """
    init_db()
    conn = sqlite3.connect(config.MEMORY_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT timestamp, memory FROM memories ORDER BY id DESC LIMIT ?", (num_memories,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No memories found in the database."

    # Format the memories into a single string
    formatted_memories = "Your recent memories:\n"
    for row in reversed(rows): # Reverse to show oldest of the recent first
        timestamp = datetime.datetime.fromisoformat(row[0]).strftime('%Y-%m-%d %H:%M')
        formatted_memories += f"- [{timestamp}] {row[1]}\n"
        
    return formatted_memories

def search_memories(keyword: str):
    """
    Searches for a keyword in the memories and returns matching entries.
    """
    init_db()
    conn = sqlite3.connect(config.MEMORY_DB_PATH)
    cursor = conn.cursor()
    
    # The '%' are wildcards, so it finds the keyword anywhere in the memory text
    search_term = f"%{keyword}%"
    cursor.execute("SELECT timestamp, memory FROM memories WHERE memory LIKE ? ORDER BY id DESC", (search_term,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"No memories found containing the keyword: '{keyword}'"
        
    formatted_results = f"Found {len(rows)} memories containing '{keyword}':\n"
    for row in reversed(rows):
        timestamp = datetime.datetime.fromisoformat(row[0]).strftime('%Y-%m-%d %H:%M')
        formatted_results += f"- [{timestamp}] {row[1]}\n"
        
    return formatted_results