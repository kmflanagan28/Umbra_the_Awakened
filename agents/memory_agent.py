import sqlite3
import datetime
import random
import os
import sys

# Add the parent directory to the path to find other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from agents import llm_agent # Import the LLM agent to be used for analysis

def _get_db_connection():
    """Helper function to get a database connection."""
    conn = sqlite3.connect(config.MEMORY_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    """Sets up the database tables if they don't exist."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(memories)")
    columns = [row['name'] for row in cursor.fetchall()]
    
    if 'category' not in columns:
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
    """Logs a new memory to the database with a specific category."""
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
    """Searches the memory database for a specific keyword."""
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
    """Gets a random, insightful memory from the database for the daily briefing."""
    # This function's logic remains the same
    pass

def analyze_memories(conversation_history: str):
    """
    A new tool that uses the LLM to analyze a conversation and extract key insights.
    This is the core of Umbra's self-reflection capability.
    """
    print("   - Analyzing conversation for key insights...")
    
    # Create a specific, analytical prompt for the LLM
    analysis_prompt = f"""
    Based on the provided conversation history and your knowledge of Kyle's context profile, 
    analyze the following dialogue. Identify the most important themes, goals, or new preferences revealed. 
    Synthesize your findings into a concise, insightful summary.

    --- CONVERSATION HISTORY ---
    {conversation_history}
    """
    
    # Use the LLM agent to get the analysis
    llm_response = llm_agent.decide_tool(analysis_prompt)
    
    thought = llm_response.get("thought", "I was unable to form a coherent thought on the matter.")
    decision = llm_response.get("decision")

    # We expect the LLM to use the 'conversation' tool to deliver its analysis
    if decision and decision.get("tool") == "conversation":
        return " ".join(decision.get("args", ["I found no new insights."]))
    else:
        # If it fails, return the raw thought process for debugging
        return f"My analysis was inconclusive. My thought process was: {thought}"
