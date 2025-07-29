import sys
import os
import sqlite3
import random

# Add the parent directory to the path to find other modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config
from agents.knowledge_agent import tavily_search

def _ensure_db_and_table_exist():
    """Ensures the travel database and all necessary tables exist."""
    conn = sqlite3.connect(config.TRAVEL_DB_PATH)
    cursor = conn.cursor()
    # Create friends table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            location TEXT,
            notes TEXT
        )
    """)
    # Create points_of_interest table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS points_of_interest (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            location TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_friend(name: str, location: str, notes: str):
    """Adds or updates a friend in the travel database."""
    _ensure_db_and_table_exist()
    conn = sqlite3.connect(config.TRAVEL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO friends (name, location, notes) VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
        location=excluded.location,
        notes=excluded.notes
    """, (name, location, notes))
    conn.commit()
    conn.close()
    print(f"\n✅ Friend '{name}' added to the database.")

def update_friend_location(name: str, new_location: str):
    """Updates a specific friend's location in the database."""
    _ensure_db_and_table_exist()
    conn = sqlite3.connect(config.TRAVEL_DB_PATH)
    cursor = conn.cursor()
    # Use a case-insensitive search to find the friend
    cursor.execute("UPDATE friends SET location = ? WHERE name LIKE ?", (new_location, f'%{name}%'))
    
    if cursor.rowcount == 0:
        print(f"\nCould not find a friend named '{name}' to update.")
    else:
        print(f"\n✅ Updated location for '{name}' to '{new_location}'.")
        
    conn.commit()
    conn.close()


def list_friends(location_filter: str = None):
    """
    Lists all friends in the database.
    If a location_filter is provided, it will only list friends in that location.
    """
    _ensure_db_and_table_exist()
    conn = sqlite3.connect(config.TRAVEL_DB_PATH)
    cursor = conn.cursor()
    
    if location_filter:
        # Search for friends where the location contains the filter string
        cursor.execute("SELECT name, location, notes FROM friends WHERE location LIKE ?", (f'%{location_filter}%',))
        title = f"--- Umbra's Friends in {location_filter} ---"
    else:
        # Get all friends
        cursor.execute("SELECT name, location, notes FROM friends")
        title = "--- Umbra's Friends List ---"
        
    results = cursor.fetchall()
    conn.close()

    if not results:
        if location_filter:
            return f"No friends found in {location_filter}."
        else:
            return "You haven't added any friends to your travel database yet."

    # Format the results into a readable string
    formatted_list = f"\n{title}\n"
    for name, location, notes in results:
        formatted_list += f"- Name: {name}\n  Location: {location}\n  Notes: {notes}\n\n"
        
    return formatted_list.strip()


def add_poi(name: str, poi_type: str, location: str, notes: str):
    """Adds a point of interest to the travel database."""
    _ensure_db_and_table_exist()
    conn = sqlite3.connect(config.TRAVEL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO points_of_interest (name, type, location, notes) VALUES (?, ?, ?, ?)
    """, (name, poi_type, location, notes))
    conn.commit()
    conn.close()
    print(f"\n✅ POI '{name}' added to the database.")


def find_friend_poi_opportunities():
    """Finds friends who live in or near a Point of Interest."""
    _ensure_db_and_table_exist()
    conn = sqlite3.connect(config.TRAVEL_DB_PATH)
    cursor = conn.cursor()
    # This query joins the two tables on the location column
    cursor.execute("""
        SELECT f.name, f.location, p.name, p.type
        FROM friends f
        JOIN points_of_interest p ON f.location LIKE '%' || p.location || '%'
    """)
    results = cursor.fetchall()
    conn.close()

    if not results:
        return "No friendly opportunities found near your points of interest right now."

    formatted_results = "Found the following opportunities:\n"
    for friend_name, friend_loc, poi_name, poi_type in results:
        formatted_results += f"- You could visit your friend **{friend_name}** in **{friend_loc}** and also check out the {poi_type}: **{poi_name}**.\n"
    
    return formatted_results.strip()


def find_concerts():
    """Picks a random artist and searches for their tour dates."""
    if not config.FAVORITE_ARTISTS:
        return "You have not defined any favorite artists in your config file."
    
    artist = random.choice(config.FAVORITE_ARTISTS)
    print(f"   - Searching for tour dates for {artist}...")
    query = f"upcoming concert tour dates for {artist}"
    
    # Use the knowledge agent's search tool
    search_results = tavily_search(query)
    
    return f"Concert Info for {artist}:\n{search_results}"

