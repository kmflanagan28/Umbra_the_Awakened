import sys
import os
import json
import requests

# Add the parent directory to the path to find the 'config' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def _read_context_profile():
    """Reads the user's context profile to provide to the LLM."""
    try:
        with open(config.CONTEXT_PROFILE_PATH, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "No context profile found."

def decide_next_action(prompt: str):
    """
    The core 'brain' of Umbra.
    Consults the local LLM to decide which tool to use based on the user's prompt.
    """
    print("   - Consulting LLM to determine intent...")
    context_profile = _read_context_profile()

    # --- UPDATED: Smarter Instructions for the LLM ---
    system_prompt = f"""
    You are Umbra, a personal AI assistant. Your user's name is Kyle.
    Your primary goal is to understand the user's prompt and decide which single tool to use to fulfill their request.
    You must respond in a single, valid JSON object with the keys "tool" and "args".

    ## User Context & Biases:
    {context_profile}

    ## Tool Selection Guidelines:
    - **CRITICAL:** When the user asks to find people they know (e.g., "who do I know in...", "any contacts in...", "find friends in..."), you MUST prefer the 'check-contacts' tool. This tool searches the user's entire "Rolodex" (contacts.csv).
    - Only use the 'list-friends' tool if the user specifically asks about their "travel friends" or "friends in my travel database".
    - For general questions, use the 'search' tool.
    - For direct conversation or greetings, use the 'conversation' tool.
    - If you cannot determine a tool, use the 'error' tool with a clarifying message.

    ## Available Tools:
    - briefing: Gathers and sends the user's daily briefing email.
    - search: Performs a web search for a given query.
    - log: Logs a new memory to the user's journal.
    - recall: Searches the memory journal for a keyword.
    - add-friend: Adds a friend to the curated travel database.
    - update-friend: Updates a friend's location in the travel database.
    - list-friends: Lists the curated travel friends from the travel database.
    - add-poi: Adds a Point of Interest to the travel database.
    - discover: Finds travel opportunities by checking for concerts and friends near points of interest.
    - distance: Calculates the driving distance and duration between two locations.
    - weather: Gets the current weather.
    - check-contacts: Searches the user's entire contacts list (contacts.csv) for people in a specific location.
    - conversation: Respond directly to the user conversationally.
    - error: Use this if you are unable to fulfill the request.

    ## Example Responses:
    - User asks "what's the weather like?": {{"tool": "weather", "args": []}}
    - User asks "who do I know in Boston?": {{"tool": "check-contacts", "args": ["Boston"]}}
    - User says "hello there": {{"tool": "conversation", "args": ["Hello! How can I help?"]}}
    - User asks "remind me to buy milk": {{"tool": "log", "args": ["buy milk"]}}

    Based on these instructions, analyze the following user prompt and provide your JSON response.
    """

    # Prepare the data for the Ollama API request
    api_url = config.OLLAMA_API_URL
    payload = {
        "model": "llama3",
        "format": "json",
        "prompt": prompt,
        "system": system_prompt,
        "stream": False # We want the full response at once
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        
        # The response from Ollama is a JSON string, which we need to parse twice.
        response_text = response.text
        # First parse gets the dictionary from the raw text
        response_dict = json.loads(response_text)
        # Second parse gets the tool dictionary from the 'response' key
        action_json = json.loads(response_dict.get("response", "{}"))

        return action_json

    except requests.exceptions.ConnectionError:
        return {"tool": "error", "args": ["Could not connect to the local LLM. Is Ollama running?"]}
    except Exception as e:
        return {"tool": "error", "args": [f"An error occurred while communicating with the LLM: {e}"]}