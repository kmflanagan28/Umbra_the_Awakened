import sys
import datetime

# --- Agent Imports ---
from agents.memory_agent import add_memory, read_recent_memories, search_memories
from agents.knowledge_agent import get_weather, tavily_search
from agents.comms_agent import send_email
from agents.travel_agent import add_friend, add_poi, update_friend_location, list_friends
from agents.contacts_agent import find_contact 

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
            elif command == "help":
                print_commands()
            # Memory Agent
            elif command == "log":
                memory_to_log = input("Enter memory to log: ")
                add_memory(memory_to_log)
            elif command == "recall":
                if not argument:
                    print("Please provide a keyword. e.g., 'recall fish sticks'")
                else:
                    result = search_memories(argument)
                    print(f"\n{result}")
            # Travel Agent
            elif command == "add-friend":
                name_to_find = input("Friend's name: ")
                
                print(f"Checking your contacts for '{name_to_find}'...")
                contact_info = find_contact(name_to_find)
                
                if contact_info and contact_info.get('name'):
                    print(f"\n✅ Found a match in your contacts: {contact_info.get('name')}")
                    location = contact_info.get('location', '')
                    if location:
                        use_contact = input(f"   Their location is '{location}'. Use this info? (y/n): ").lower()
                        if use_contact == 'y':
                            notes = input("Notes (e.g., has a guest room): ")
                            add_friend(contact_info.get('name'), location, notes)
                        else:
                            print("Ok, proceeding with manual entry.")
                            location_manual = input("Their city/state: ")
                            notes_manual = input("Notes (e.g., has a guest room): ")
                            add_friend(name_to_find, location_manual, notes_manual)
                    else:
                        print("   No location found in contacts. Proceeding with manual entry.")
                        location_manual = input("Their city/state: ")
                        notes_manual = input("Notes (e.g., has a guest room): ")
                        add_friend(name_to_find, location_manual, notes_manual)
                else:
                    print(f"   No match found for '{name_to_find}'. Proceeding with manual entry.")
                    location_manual = input("Their city/state: ")
                    notes_manual = input("Notes (e.g., has a guest room): ")
                    add_friend(name_to_find, location_manual, notes_manual)
            
            elif command == "update-friend":
                name = input("Name of the friend to update: ")
                new_location = input(f"Enter the new location for {name}: ")
                update_friend_location(name, new_location)
                
            elif command == "list-friends":
                list_friends()
                
            elif command == "add-poi":
                name = input("Name of POI (e.g., 'Yosemite' or 'New York City'): ")
                poi_type = input("Type (e.g., National Park, City, Landmark): ")
                location = input("Location (e.g., California or NY): ")
                notes = input("Notes (e.g., 'good pizza' or 'love the hiking'): ")
                add_poi(name, poi_type, location, notes)
            # Knowledge Agent
            elif command == "weather":
                result = get_weather(argument)
                print(result)
            elif command == "search":
                if not argument:
                    print("Please provide a web search query.")
                else:
                    result = tavily_search(argument)
                    print(result)
            # Comms Agent
            elif command == "briefing":
                print("\n⚙️  Assembling your briefing...")
                weather_report = get_weather()
                print("   - Got weather report.")
                recent_memories = read_recent_memories()
                print("   - Read recent memories.")
                subject = f"Umbra's Daily Briefing - {datetime.date.today().strftime('%A, %B %d')}"
                body = (
                    f"Good morning.\n\n"
                    f"Here is your daily briefing:\n\n"
                    f"--- Weather ---\n{weather_report}\n\n"
                    f"--- Memory Log ---\n{recent_memories}\n\n"
                    f"Have a productive day.\n- Umbra"
                )
                print("   - Assembled email body.")
                print("   - Sending email...")
                email_status = send_email(subject, body)
                print(f"\n{email_status}")
            else:
                print(f"Unknown command: '{command}'. Type 'help' for a list of commands.")

        except KeyboardInterrupt:
            print("\n\nDeactivating Umbra. Goodbye.")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

