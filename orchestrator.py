import sys

# --- Tool Imports ---
from tools.memory_tools import add_memory, read_recent_memories, search_memories
from tools.web_tools import get_weather, tavily_search
from tools.communication_tools import send_email

# --- Local Imports ---
import config

def print_commands():
    """Prints the list of available commands."""
    print("\n--- Umbra Command List ---")
    print("'log'              - Allows you to log a new memory.")
    print("'recall [keyword]' - Searches your memory for a keyword.")
    print("'briefing'         - Gathers and sends your daily briefing email.")
    print("'weather'          - Get the current weather for your home city.")
    print("'weather [city]'   - Get weather for a specific city.")
    print("'search [query]'   - Perform a web search.")
    print("'help'             - Shows this list of commands.")
    print("'exit'             - Quits the application.")
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
            elif command == "log":
                memory_to_log = input("Enter memory to log: ")
                add_memory(memory_to_log)
            elif command == "recall":
                if not argument:
                    print("Please provide a keyword to search for. e.g., 'recall fish sticks'")
                else:
                    result = search_memories(argument)
                    print(f"\n{result}")
            elif command == "weather":
                result = get_weather(argument)
                print(result)
            elif command == "search":
                if not argument:
                    print("Please provide a web search query. e.g., 'search what is python'")
                else:
                    result = tavily_search(argument)
                    print(result)
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