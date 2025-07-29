import sqlite3
import os
import sys
import random

# Add the parent directory to the path to find other modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config
from agents.knowledge_agent import tavily_search

def _initialize_travel_db():
    """Ensures the travel database and its tables exist."""
    conn = sqlite3.connect(config.TRAVEL_DB_PATH)
    cursor = conn.cursor()
    # Create friends table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            location TEXT,
            notes TEXT
        )
    ''')
    # Create points_of_interest table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS points_of_interest (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            type TEXT,
            location TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the DB when the agent is first loaded
_initialize_travel_db()

# --- Functions to add data ---
def add_friend(name: str, location: str, notes: str):
    """Adds a friend to the travel database."""
    try:
        conn = sqlite3.connect(config.TRAVEL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO friends (name, location, notes) VALUES (?, ?, ?)", (name, location, notes))
        conn.commit()
        conn.close()
        print(f"\n✅ Friend '{name}' added to the database.")
    except sqlite3.IntegrityError:
        print(f"\n⚠️  Error: A friend named '{name}' already exists in the database.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

def add_poi(name: str, poi_type: str, location: str, notes: str):
    """Adds a point of interest to the travel database."""
    try:
        conn = sqlite3.connect(config.TRAVEL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO points_of_interest (name, type, location, notes) VALUES (?, ?, ?, ?)", (name, poi_type, location, notes))
        conn.commit()
        conn.close()
        print(f"\n✅ POI '{name}' added to the database.")
    except sqlite3.IntegrityError:
        print(f"\n⚠️  Error: A POI named '{name}' already exists in the database.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

# --- Functions to manage data ---
def update_friend_location(name: str, new_location: str):
    """Updates the location for a specific friend in the database."""
    conn = sqlite3.connect(config.TRAVEL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM friends WHERE name LIKE ?", (f'%{name}%',))
    friend = cursor.fetchone()
    if friend:
        cursor.execute("UPDATE friends SET location = ? WHERE id = ?", (new_location, friend[0]))
        conn.commit()
        print(f"\n✅ Updated location for '{name}' to '{new_location}'.")
    else:
        print(f"\n⚠️  Could not find a friend named '{name}' to update.")
    conn.close()

def list_friends():
    """Lists all friends currently stored in the database."""
    conn = sqlite3.connect(config.TRAVEL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, location, notes FROM friends")
    all_friends = cursor.fetchall()
    conn.close()
    if not all_friends:
        return "\nYour friends list is currently empty."
    output = "\n--- Umbra's Friends List ---\n"
    for friend in all_friends:
        output += f"- Name: {friend[0]}\n  Location: {friend[1]}\n  Notes: {friend[2]}\n"
    return output

# --- NEW: Functions to discover opportunities ---
def find_friend_poi_opportunities():
    """Finds friends who are located in the same area as a point of interest."""
    conn = sqlite3.connect(config.TRAVEL_DB_PATH)
    cursor = conn.cursor()
    # This SQL query joins the two tables on the location field
    cursor.execute('''
        SELECT f.name, f.location, p.name, p.type
        FROM friends f
        JOIN points_of_interest p ON f.location = p.location
    ''')
    opportunities = cursor.fetchall()
    conn.close()
    if not opportunities:
        return "No friendly opportunities found near your points of interest right now."
    
    output = "Found the following opportunities:\n"
    for op in opportunities:
        output += f"- You could visit your friend **{op[0]}** in **{op[1]}** and also check out the {op[3]}: **{op[2]}**.\n"
    return output

def find_concerts():
    """Searches for concert dates for a random favorite artist."""
    if not config.FAVORITE_ARTISTS:
        return "You have not defined any favorite artists in config.py."
    
    artist = random.choice(config.FAVORITE_ARTISTS)
    print(f"   - Searching for tour dates for {artist}...")
    query = f"upcoming tour dates for {artist} in the US"
    
    # Use the knowledge agent's search tool
    results = tavily_search(query)
    
    if "No search results found" in results:
        return f"No upcoming tour dates found for {artist} at this time."
    
    return f"Concert Info for {artist}:\n{results}"
