import sys
import datetime
import json

# --- Agent Imports ---
from agents import (
    memory_agent, 
    knowledge_agent, 
    comms_agent, 
    travel_agent, 
    contacts_agent, 
    inspiration_agent, 
    llm_agent,
    logistics_agent
)

# --- Helper Functions for Complex Tools ---

def _run_briefing():
    """Helper function to assemble and send the daily briefing."""
    # ... (this function is unchanged) ...
    print("\n⚙️  Assembling your briefing...")
    daily_quote = inspiration_agent.get_daily_quote()
    weather_report = knowledge_agent.get_weather()
    memory_insight = memory_agent.get_daily_memory_insight() 
    
    subject = f"Umbra's Daily Briefing - {datetime.date.today().strftime('%A, %B %d')}"
    body = (
        f"Good morning.\n\n"
        f"Here is your daily briefing:\n\n"
        f"--- Thought for the Day ---\n{daily_quote}\n\n"
        f"--- Weather ---\n{weather_report}\n\n"
        f"--- From the Archives ---\n{memory_insight}\n\n"
        f"Have a productive day.\n- Umbra"
    )
    print("   - Assembled email body.")
    print("   - Sending email...")
    return comms_agent.send_email(subject, body)


def _run_discovery():
    """Helper function to run the discovery tools and format a report."""
    # ... (this function is unchanged) ...
    print("\n🔎 Discovering potential opportunities...")
    friend_ops = travel_agent.find_friend_poi_opportunities()
    concert_ops = travel_agent.find_concerts()
    
    report = (
        f"\n--- Discovery Report ---\n"
        f"\n[ Friendly Opportunities ]\n{friend_ops}\n"
        f"\n[ Concerts & Events ]\n{concert_ops}\n"
        f"------------------------"
    )
    return report

# --- Core Execution Logic ---

def execute_action(action: dict):
    """Executes the action decided by the LLM by looking up the tool in a map."""
    tool_name = action.get("tool")
    args = action.get("args", [])

    print(f"   - LLM decided to use tool: '{tool_name}' with args: {args}")

    # A complete dictionary mapping all tool names to the actual functions
    tool_map = {
        "briefing": _run_briefing,
        "search": knowledge_agent.tavily_search,
        "log": memory_agent.add_memory,
        "recall": memory_agent.search_memories,
        "add-friend": travel_agent.add_friend,
        "update-friend": travel_agent.update_friend_location,
        "list-friends": travel_agent.list_friends,
        "add-poi": travel_agent.add_poi,
        "discover": _run_discovery,
        "distance": logistics_agent.get_distance,
        "weather": knowledge_agent.get_weather,
        # *** NEW: Add the check-contacts tool ***
        "check-contacts": contacts_agent.check_contacts, 
        "conversation": lambda *messages: print(f"\nUmbra: {' '.join(messages)}"),
        "error": lambda message: print(f"\nError from LLM: {message}")
    }
    
    if tool_name in tool_map:
        try:
            result = tool_map[tool_name](*args)
            if result:
                print(f"\n{result}")
        except TypeError as e:
            print(f"\nError executing tool '{tool_name}': {e}. Check number of arguments.")
    else:
        print(f"\nError: LLM chose an unknown tool: '{tool_name}'.")

# --- Main Program Loop ---

def main():
    """The main function where the program runs."""
    # Add a new line to the help prompt
    print("--- Umbra OS v2.2 (Rolodex-Enabled) Activated ---")
    print("Ask me anything, check your contacts with 'check-contacts [location]', or type 'exit'.")
    
    while True:
        try:
            prompt = input("\nKyle ▶ ")

            if prompt.lower() == "exit":
                print("\nDeactivating Umbra. Goodbye.")
                break
            
            if not prompt:
                continue

            # 1. Let the LLM decide what to do
            action_to_take = llm_agent.decide_next_action(prompt)

            # 2. Execute the decided action
            execute_action(action_to_take)

            # 3. Automatically log the interaction
            log_entry = f"User Prompt: '{prompt}' | Umbra's Action: {json.dumps(action_to_take)}"
            memory_agent.add_memory(log_entry)

        except KeyboardInterrupt:
            print("\n\nDeactivating Umbra. Goodbye.")
            break
        except Exception as e:
            print(f"\nAn unexpected critical error occurred: {e}")

if __name__ == "__main__":
    main()

