import sqlite3
import os
import sys
import datetime
import random

# Add the parent directory to the path to find the 'config' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def initialize_memory():
    """Ensures the database and the memories table with the new category column exist."""
    with sqlite3.connect(config.MEMORY_DB_PATH) as conn:
        cursor = conn.cursor()
        # Check if the 'category' column exists
        cursor.execute("PRAGMA table_info(memories)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'category' not in columns:
            print("Upgrading memories database to include 'category' column...")
            # More robust upgrade: create a new table and copy data
            cursor.execute("ALTER TABLE memories RENAME TO memories_old")
            cursor.execute('''
                CREATE TABLE memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    category TEXT NOT NULL,
                    memory TEXT NOT NULL
                )
            ''')
            # Copy old data, providing a default category
            cursor.execute("""
                INSERT INTO memories (timestamp, category, memory)
                SELECT timestamp, 'Legacy Log', memory FROM memories_old
            """)
            cursor.execute("DROP TABLE memories_old")
            print("Database upgrade complete.")
        conn.commit()

# Run initialization when the module is loaded
initialize_memory()


def add_memory(text_to_log: str, category: str = "Manual Log"):
    """
    Logs a string of text to the database with a timestamp and a category.
    """
    with sqlite3.connect(config.MEMORY_DB_PATH) as conn:
        timestamp = datetime.datetime.now().isoformat()
        conn.execute(
            'INSERT INTO memories (timestamp, category, memory) VALUES (?, ?, ?)',
            (timestamp, category, text_to_log)
        )
        conn.commit()
    print("\n💾 Memory stored in the database.")


def get_daily_memory_insight():
    """
    Retrieves a single, interesting memory from the past for the daily briefing.
    It prioritizes more thoughtful logs over simple system interactions.
    """
    with sqlite3.connect(config.MEMORY_DB_PATH) as conn:
        cursor = conn.cursor()
        # Prioritize categories that are more likely to be interesting
        priority_categories = ('Manual Log', 'User Insight', 'System Learning')
        cursor.execute(
            f"SELECT timestamp, memory FROM memories WHERE category IN {priority_categories} ORDER BY RANDOM() LIMIT 1"
        )
        result = cursor.fetchone()
        if result:
            timestamp, memory = result
            date_obj = datetime.datetime.fromisoformat(timestamp)
            date_str = date_obj.strftime('%A, %B %d, %Y')
            return f"On {date_str}, you were thinking about:\n- \"{memory}\""
        else:
            return "No insightful memories found in the archives yet."


def search_memories(keyword: str):
    """Searches the memory database for a specific keyword."""
    with sqlite3.connect(config.MEMORY_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, memory FROM memories WHERE memory LIKE ?",
            (f'%{keyword}%',)
        )
        results = cursor.fetchall()
        if not results:
            return f"No memories found containing the keyword: '{keyword}'"

        response = f"Found {len(results)} memories containing '{keyword}':\n"
        for timestamp, memory in results:
            date_str = datetime.datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M')
            response += f"- [{date_str}] {memory}\n"
        return response

def review_memories(category_filter: str = None):
    """
    Lists memories from the database. Can be filtered by category.
    """
    with sqlite3.connect(config.MEMORY_DB_PATH) as conn:
        cursor = conn.cursor()
        if category_filter:
            cursor.execute(
                "SELECT category, timestamp, memory FROM memories WHERE category LIKE ? ORDER BY timestamp DESC",
                (f'%{category_filter}%',)
            )
        else:
            cursor.execute("SELECT category, timestamp, memory FROM memories ORDER BY timestamp DESC")
        
        results = cursor.fetchall()
        if not results:
            return f"No memories found matching the filter: '{category_filter}'"
        
        response = f"\n--- Memory Review ({len(results)} entries) ---\n"
        for category, timestamp, memory in results:
            date_str = datetime.datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M')
            response += f"[{date_str}] [{category}] {memory}\n"
        return response