import sys
import os
import requests
import json

# Add the parent directory to the path to find other modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def read_context_profile():
    """Reads the user's context profile."""
    try:
        with open(config.CONTEXT_PROFILE_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "No context profile found."

def get_tool_manifest():
    """
    Returns a string describing the available tools.
    This acts as a 'manual' for the LLM.
    """
    return """
    Available Tools:
    - `briefing`: Gathers and sends the daily briefing email.
    - `search [query]`: Performs a web search.
    - `log [memory_text]`: Logs a new memory.
    - `recall [keyword]`: Searches memory for a keyword.
    - `add-friend`: Adds a friend to the travel database.
    - `update-friend`: Updates a friend's location.
    - `list-friends`: Shows all friends in the travel database.
    - `add-poi`: Adds a Point of Interest.
    - `discover`: Finds travel opportunities (concerts, friends near POIs).
    - `weather [city]`: Gets the current weather.
    - `distance [origin] [destination]`: Calculates driving distance and time.
    """

def decide_next_action(prompt: str):
    """
    Uses the local LLM to decide which tool to use based on the user's prompt.
    """
    print("   - Consulting LLM to determine intent...")
    context = read_context_profile()
    tool_manifest = get_tool_manifest()
    
    # The system prompt that instructs the LLM
    # The double curly braces {{ and }} are used to escape the braces so the f-string
    # treats them as literal characters instead of trying to format them.
    system_prompt = f"""
    You are Umbra, a highly intelligent orchestrator for a personal AI assistant.
    Your user, Kyle, has given you a prompt. Your job is to understand the prompt,
    consult the user's context profile, and decide which single tool to use to
    fulfill the request.

    Respond ONLY with a JSON object in the following format:
    {{ "tool": "tool_name", "args": ["arg1", "arg2", ...] }}
    or if the prompt is conversational and requires no tool:
    {{ "tool": "conversation", "args": ["A direct response to the user."] }}

    USER CONTEXT PROFILE:
    ---
    {context}
    ---

    AVAILABLE TOOLS:
    ---
    {tool_manifest}
    ---

    Analyze the following user prompt and return the single, best tool to use in the specified JSON format.
    Do not add any extra commentary or explanation.
    """

    # The data payload for the Ollama API
    payload = {
        "model": config.LLM_MODEL_NAME,
        "system": system_prompt,
        "prompt": prompt,
        "format": "json",
        "stream": False # We want the full response at once
    }

    try:
        response = requests.post(config.LLM_API_URL, json=payload)
        response.raise_for_status()
        
        # The actual response from Ollama is a string inside a JSON object,
        # so we need to parse it twice.
        response_data = response.json()
        action_json_str = response_data.get('response', '{}')
        action = json.loads(action_json_str)
        
        return action
        
    except requests.exceptions.RequestException as e:
        return {"tool": "error", "args": [f"Could not connect to local LLM: {e}"]}
    except (json.JSONDecodeError, KeyError) as e:
        return {"tool": "error", "args": [f"Error parsing LLM response: {e}"]}