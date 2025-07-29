import sys
import json
import datetime

# --- Agent Imports ---
from agents import (
    memory_agent,
    knowledge_agent,
    comms_agent,
    travel_agent,
    contacts_agent,
    inspiration_agent,
    logistics_agent,
    llm_agent
)

# --- The Tool Map ---
# This dictionary maps the tool names the LLM can choose to the actual Python functions.
tool_map = {
    "log": lambda args: memory_agent.add_memory(args[0], "Manual Log"),
    "recall": memory_agent.search_memories,
    "list-friends": travel_agent.list_friends,
    "add-friend": travel_agent.add_friend,
    "update-friend": travel_agent.update_friend_location,
    "add-poi": travel_agent.add_poi,
    "discover": lambda args: (
        travel_agent.find_friend_poi_opportunities(),
        travel_agent.find_concerts()
    ),
    "check-contacts": contacts_agent.check_contacts,
    "distance": logistics_agent.get_route_info,
    "weather": knowledge_agent.get_weather,
    "search": knowledge_agent.tavily_search,
    "briefing": lambda args: send_daily_briefing(),
    "conversation": lambda args: print(f"\nUmbra: {' '.join(args)}"),
    # --- NEW DEBUG TOOL ---
    "debug": lambda args: print(f"\n[DEBUG] Available tools: {list(tool_map.keys())}")
}

def execute_action(decision: dict):
    """Executes the tool chosen by the LLM."""
    tool_name = decision.get("tool")
    args = decision.get("args", [])
    
    if tool_name in tool_map:
        try:
            result = tool_map[tool_name](args)
            if result:
                print(result)
            return "Action executed successfully."
        except Exception as e:
            error_message = f"Error executing tool '{tool_name}': {e}. Check number of arguments."
            print(error_message)
            memory_agent.add_memory(error_message, "System Error")
            return error_message
    else:
        not_found_message = f"I'm sorry, I don't have a tool named '{tool_name}' yet, but I'm learning. Please try a different command."
        print(f"\nUmbra: {not_found_message}")
        memory_agent.add_memory(f"LLM tried to use non-existent tool: {tool_name}", "System Learning")
        return not_found_message


def send_daily_briefing():
    """Gathers all information and sends the daily briefing email."""
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
    email_status = comms_agent.send_email(subject, body)
    print(f"\n{email_status}")


def main():
    """The main loop for the LLM-powered orchestrator."""
    memory_agent.setup_database()

    print("--- Umbra OS v2.5 (Intelligent Parsing) Activated ---")
    print("Ask me anything, or type 'exit' to quit.")

    while True:
        try:
            user_prompt = input("\nKyle ▶ ")
            if user_prompt.lower() == "exit":
                print("\nDeactivating Umbra. Goodbye.")
                break

            print("   - Consulting LLM to determine intent...")
            llm_response = llm_agent.decide_tool(user_prompt)
            cleaned_response = llm_response.strip()

            tool_decision = None
            try:
                # First, assume it MIGHT be JSON and try to parse it
                potential_json = json.loads(cleaned_response)
                # If it parses AND has a 'tool' key, treat it as a tool decision
                if isinstance(potential_json, dict) and 'tool' in potential_json:
                    tool_decision = potential_json
                    print(f"   - LLM decided to use tool: '{tool_decision.get('tool')}' with args: {tool_decision.get('args')}")
                else:
                    # It parsed to JSON but wasn't a valid tool format (e.g. {"key": "value"}), so it's a conversation
                    raise json.JSONDecodeError("Not a tool format", cleaned_response, 0)
            except (json.JSONDecodeError, TypeError):
                # If it fails parsing or isn't a dictionary, it's a direct conversational response
                print(f"   - LLM provided a direct conversational response.")
                tool_decision = {"tool": "conversation", "args": [cleaned_response]}

            # Execute the chosen action
            execute_action(tool_decision)
            
            # Log the entire interaction as a memory
            log_entry = f"User Prompt: '{user_prompt}' | Umbra's Action: {tool_decision}"
            memory_agent.add_memory(log_entry, "User Interaction")

        except KeyboardInterrupt:
            print("\n\nDeactivating Umbra. Goodbye.")
            break
        except Exception as e:
            critical_error = f"A critical error occurred in the main loop: {e}"
            print(critical_error)
            memory_agent.add_memory(critical_error, "Critical System Error")


if __name__ == "__main__":
    main()
