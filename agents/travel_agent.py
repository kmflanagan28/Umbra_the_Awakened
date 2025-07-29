import sqlite3
import os
import sys

# Add the parent directory to the path to find the 'config' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

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

def update_friend_location(name: str, new_location: str):
    """
    Updates the location for a specific friend in the database.
    """
    conn = sqlite3.connect(config.TRAVEL_DB_PATH)
    cursor = conn.cursor()
    # First, check if the friend exists
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
        print("\nYour friends list is currently empty.")
        return

    print("\n--- Umbra's Friends List ---")
    for friend in all_friends:
        print(f"- Name: {friend[0]}\n  Location: {friend[1]}\n  Notes: {friend[2]}\n")