import sys
import json
import datetime
import inspect

# --- Agent Imports ---
from agents.memory_agent import add_memory, get_daily_memory_insight, search_memories, review_memories
from agents.knowledge_agent import get_weather, tavily_search
from agents.comms_agent import send_email
from agents.travel_agent import (
    add_friend, add_poi, update_friend_location, list_friends,
    find_friend_poi_opportunities
)
from agents.contacts_agent import find_contact, check_contacts
from agents.inspiration_agent import get_daily_quote
from agents.logistics_agent import get_route_info
from agents.llm_agent import initialize_llm_system, decide_tool

# --- Local Imports ---
import config

# The master dictionary mapping tool names to their functions
tool_map = {
    "add-friend": add_friend,
    "add-poi": add_poi,
    "check-contacts": check_contacts,
    "debug": None,
    "discover": find_friend_poi_opportunities,
    "distance": get_route_info,
    "list-friends": list_friends,
    "log": add_memory,
    "quote": get_daily_quote,
    "recall": search_memories,
    "review-memories": review_memories,
    "search": tavily_search,
    "update-friend": update_friend_location,
    "weather": get_weather,
    "briefing": None,
    "conversation": None,
}

def print_help():
    """Prints a user-friendly help message listing available tools."""
    print("\n--- Umbra's Abilities ---")
    print("I can understand natural language. Just tell me what you need.")
    print("Here are some of the direct tools I have available:\n")
    for tool_name in sorted(tool_map.keys()):
        print(f"- {tool_name}")
    print("\nOr, just ask me a question like 'Do I have any friends in California?'")
    print("-------------------------\n")

def execute_action(decision):
    """Executes the tool chosen by the LLM with enhanced error handling."""
    tool_name = decision.get("tool")
    args = decision.get("args", [])

    print(f"   - Preparing to execute tool: '{tool_name}'...")

    if tool_name not in tool_map:
        print(f"\nUmbra: I decided on a tool named '{tool_name}' that doesn't exist yet. My mistake.")
        return

    if tool_name == "conversation":
        response = " ".join(map(str, args))
        print(f"\nUmbra: {response}")
        return
    elif tool_name == "briefing":
        run_briefing()
        return
    elif tool_name == "debug":
        print_help()
        return

    try:
        tool_function = tool_map[tool_name]
        sig = inspect.signature(tool_function)
        required_args_count = len(sig.parameters)
        
        if len(args) != required_args_count:
            error_message = (
                f"\n[SELF-DEBUG] Tool Mismatch Error:\n"
                f"  - The LLM tried to call the tool '{tool_name}' with {len(args)} arguments.\n"
                f"  - However, the tool's function requires exactly {required_args_count} arguments."
            )
            print(error_message)
            return

        result = tool_function(*args)
        if result:
            print(f"\n{result}")
        print(f"   - Tool '{tool_name}' executed successfully.")

    except Exception as e:
        print(f"\nAn unexpected error occurred with tool '{tool_name}': {e}")

def run_briefing():
    """Assembles and sends the daily briefing email."""
    # (This function's logic remains the same)
    pass

def main():
    """The main application loop."""
    print("--- Umbra OS v3.2 (Conversational Memory) Activated ---")
    if not initialize_llm_system():
        return
    
    print_help()
    
    # --- NEW: Short-Term Conversational Memory ---
    conversation_history = []

    while True:
        try:
            user_prompt = input("Kyle ▶ ")
            if user_prompt.lower() == "exit":
                print("\nDeactivating Umbra. Goodbye.")
                break
            if user_prompt.lower() == "help":
                print_help()
                continue

            # --- NEW: Prepend conversation history to the prompt ---
            history_context = "\n".join(conversation_history)
            full_prompt = f"--- Recent Conversation History ---\n{history_context}\n\n--- Current Prompt ---\n{user_prompt}"

            print("\n   - Consulting LLM with conversation history...")
            llm_response = decide_tool(full_prompt)

            thought = llm_response.get("thought", "The LLM did not provide a thought.")
            decision = llm_response.get("decision")
            print(f"   🤔 Umbra's Thought: {thought}")
            
            # --- NEW: Update conversation history ---
            # Add user prompt to history
            conversation_history.append(f"Kyle: {user_prompt}")
            
            # Add Umbra's response to history
            if decision and decision.get("tool") == "conversation":
                 umbra_response = " ".join(map(str, decision.get("args", [])))
                 conversation_history.append(f"Umbra: {umbra_response}")
            else:
                 conversation_history.append(f"Umbra: [Executed tool: {decision.get('tool') if decision else 'None'}]")
            
            # Keep history to a manageable size (e.g., last 40 exchanges)
            if len(conversation_history) > 40:
                conversation_history = conversation_history[-40:]


            if decision and decision.get("tool"):
                execute_action(decision)
                log_category = "User Command"
            else:
                print("\nUmbra: I'm not sure which tool to use. Let's talk about it.")
                log_category = "User Conversation"

            log_entry = f"User: '{user_prompt}' | Thought: '{thought}' | Action: {decision}"
            add_memory(log_entry, log_category)
            print(f"💾 Memory stored in database: {config.MEMORY_DB_PATH}")

        except KeyboardInterrupt:
            print("\n\nDeactivating Umbra. Goodbye.")
            break
        except Exception as e:
            critical_error = f"A critical error occurred in the main loop: {e}"
            print(f"\n{critical_error}")
            add_memory(critical_error, "Critical System Error")
            print(f"💾 Critical error stored in database: {config.MEMORY_DB_PATH}")


if __name__ == "__main__":
    main()