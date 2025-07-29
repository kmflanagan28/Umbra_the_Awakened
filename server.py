from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json
import inspect

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Import all of Umbra's agents and tools ---
from agents.llm_agent import initialize_llm_system, decide_tool
from agents import memory_agent 
from agents.knowledge_agent import get_weather, tavily_search
from agents.travel_agent import add_friend, add_poi, update_friend_location, list_friends, find_friend_poi_opportunities
from agents.contacts_agent import check_contacts
from agents.logistics_agent import get_route_info
from agents.inspiration_agent import get_daily_quote
from agents.learning_agent import research_market_trends
import config

# Initialize Flask App and Umbra's "Brain"
app = Flask(__name__)
CORS(app)
initialize_llm_system()

# --- The Complete Tool Map for the Web Server ---
tool_map = {
    "add-friend": add_friend,
    "add-poi": add_poi,
    "check-contacts": check_contacts,
    "discover": find_friend_poi_opportunities,
    "distance": get_route_info,
    "list-friends": list_friends,
    "log": lambda *args: memory_agent.add_memory(args[0], "Manual Log from Web"),
    "quote": get_daily_quote,
    "recall": memory_agent.search_memories,
    "research": research_market_trends,
    "search": tavily_search,
    "update-friend": update_friend_location,
    "weather": get_weather,
    "conversation": lambda *args: " ".join(map(str, args)),
}

def execute_tool(tool_name, args):
    """Finds and executes the correct tool from the tool_map."""
    if tool_name not in tool_map:
        return f"I decided on a tool named '{tool_name}' that doesn't exist yet. My mistake."

    tool_function = tool_map[tool_name]
    
    try:
        sig = inspect.signature(tool_function)
        required_args_count = len(sig.parameters)
        
        # --- ENHANCED SELF-DEBUGGING ---
        # If the LLM provides the wrong number of arguments, catch it and respond gracefully.
        if len(args) != required_args_count:
            # Formulate a helpful, conversational error message from Umbra's perspective.
            return (f"I tried to use my '{tool_name}' tool, but I didn't have all the information I needed. "
                    f"That tool requires {required_args_count} pieces of information, but I only found {len(args)}. "
                    f"Could you please rephrase your request with all the necessary details?")

        result = tool_function(*args)
        return result if result else f"Successfully executed: {tool_name}"

    except Exception as e:
        return f"An error occurred while executing '{tool_name}': {e}"


@app.route('/status', methods=['GET'])
def status():
    """A simple endpoint to check if the server is running."""
    return jsonify({"status": "ok"})

@app.route('/chat', methods=['POST'])
def chat():
    """Handles chat messages from the UI, now including history."""
    data = request.json
    user_prompt = data.get('prompt')
    history = data.get('history', [])

    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    print(f"\n[Server] Received prompt: {user_prompt}")
    
    history_str = "\n".join(history)
    full_prompt_with_history = f"--- Recent Conversation History ---\n{history_str}\n\n--- Current Prompt ---\n{user_prompt}"

    print("   - Consulting LLM with conversation history...")
    llm_response = decide_tool(full_prompt_with_history)
    
    thought = llm_response.get("thought", "No thought provided.")
    decision = llm_response.get("decision")
    print(f"   - LLM Thought: {thought}")
    print(f"   - LLM Decision: {decision}")

    umbra_response = "I'm not sure how to respond to that."
    if decision and decision.get("tool"):
        umbra_response = execute_tool(decision.get("tool"), decision.get("args", []))

    log_entry = f"WebApp User: '{user_prompt}' | Thought: '{thought}' | Action: {decision}"
    memory_agent.add_memory(log_entry, "WebApp Conversation")
    print("   - Memory logged.")

    return jsonify({"response": umbra_response})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
