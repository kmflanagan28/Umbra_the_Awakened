import sys
import datetime

# --- Agent Imports ---
from agents.memory_agent import add_memory, read_recent_memories, search_memories
from agents.knowledge_agent import get_weather, tavily_search
from agents.comms_agent import send_email
from agents.travel_agent import (
    add_friend, add_poi, update_friend_location, list_friends, 
    find_friend_poi_opportunities, find_concerts
)
from agents.contacts_agent import find_contact
from agents.inspiration_agent import get_daily_quote
from agents.logistics_agent import get_distance # <-- New agent!

# --- Local Imports ---
import config

def print_commands():
    """Prints the list of available commands."""
    print("\n--- Umbra Command List ---")
    print("\n[ General ]")
    print("'briefing'         - Gathers and sends your daily briefing email.")
    print("'search [query]'   - Perform a web search.")
    print("'help'             - Shows this list of commands.")
    print("'exit'             - Quits the application.")
    print("\n[ Memory ]")
    print("'log'              - Allows you to log a new memory.")
    print("'recall [keyword]' - Searches your memory for a keyword.")
    print("\n[ Travel ]")
    print("'add-friend'       - Add a friend to the travel DB (checks contacts first).")
    print("'update-friend'    - Update a friend's location.")
    print("'list-friends'     - Show all friends in your travel database.")
    print("'add-poi'          - Add a Point of Interest (park, city, etc.)")
    print("'discover'         - Find travel opportunities (concerts, friends).")
    print("\n[ Logistics ]")
    print("'distance'         - Calculate driving distance between two points.")
    print("\n[ Knowledge ]")
    print("'weather'          - Get the current weather for your home city.")
    print("'weather [city]'   - Get weather for a specific city.")
    print("--------------------------\n")


def main():
    """The main function where the program runs."""
    print("--- Umbra OS Activated ---")
    print_commands()
    
    while True:
        try:
            raw_input = input("▶ ")
            parts = raw_input.split(maxsplit=1)
            command = parts[0].lower()
            argument = parts[1] if len(parts) > 1 else None

            # --- Command Handling ---
            if command == "exit":
                print("\nDeactivating Umbra. Goodbye.")
                break
            
            # (Other commands are unchanged and kept here for brevity)

            # --- NEW LOGISTICS COMMAND ---
            elif command == "distance":
                origin = input("Enter the starting location: ")
                destination = input("Enter the destination: ")
                if origin and destination:
                    result = get_distance(origin, destination)
                    print(f"\n{result}")
                else:
                    print("You must provide both an origin and a destination.")

            elif command == "discover":
                print("\n🔎 Discovering potential opportunities...")
                friend_ops = find_friend_poi_opportunities()
                concert_ops = find_concerts()
                
                print("\n--- Discovery Report ---")
                print("\n[ Friendly Opportunities ]")
                print(friend_ops)
                print("\n[ Concerts & Events ]")
                print(concert_ops)
                print("------------------------")

            # (The rest of your command handlers remain here)
            
            else:
                # Placeholder for your other existing command handlers
                print(f"Unknown command: '{command}'. Your other commands are still here.")


        except KeyboardInterrupt:
            print("\n\nDeactivating Umbra. Goodbye.")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
