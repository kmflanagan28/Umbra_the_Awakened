import requests
import json
import sys
import os

# Add the parent directory to the path to find the 'config' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def decide_tool(prompt: str) -> str:
    """
    This is the core "brain" function.
    It takes a user prompt, combines it with the context profile and a list of
    available tools, and asks the LLM to choose the best action.
    """
    # Load the context profile to give the LLM the user's biases and goals
    with open('context_profile.md', 'r') as f:
        context = f.read()

    # Define the tools available to the LLM
    tools_json = """
    [
        {"tool": "log", "args": ["<text_to_log>"], "description": "For when the user explicitly asks to log or remember a specific thought or piece of information."},
        {"tool": "recall", "args": ["<keyword>"], "description": "For when the user wants to search their own memories for a specific keyword."},
        {"tool": "check-contacts", "args": ["<location>"], "description": "Searches the user's main contacts list (rolodex) for people in a specific location. Prefer this for general queries about finding people."},
        {"tool": "list-friends", "args": ["<optional_location_filter>"], "description": "Lists friends from the curated travel database. Use this only when the user specifically asks about their 'travel friends'."},
        {"tool": "discover", "args": [], "description": "Proactively finds interesting travel opportunities, like friends near points of interest or concerts for favorite artists."},
        {"tool": "distance", "args": ["<start>", "<end>"], "description": "Calculates the driving distance and duration between two locations."},
        {"tool": "weather", "args": ["<optional_city>"], "description": "Gets the current weather."},
        {"tool": "search", "args": ["<query>"], "description": "A general web search for factual information."},
        {"tool": "briefing", "args": [], "description": "For when the user asks for their daily email briefing."},
        {"tool": "conversation", "args": ["<text_response>"], "description": "Use this for direct conversational replies, greetings, or when no other tool is appropriate."}
    ]
    """

    # This is the system prompt that instructs the LLM
    system_prompt = f"""
    You are Umbra, an AI assistant. Your primary goal is to accurately determine the user's intent and select the single best tool to accomplish it.
    
    You must consult two sources before making a decision:
    1. The User's Context Profile: This contains their core beliefs and goals. Your decisions must align with this.
    2. The Tool List: This is the list of functions you can call.
    
    User's Context Profile:
    ---
    {context}
    ---
    
    You MUST respond with ONLY a single, valid JSON object that represents your decision. Do not add any conversational text or explanations.
    
    The JSON object must have two keys: "tool" (the name of the tool you've chosen) and "args" (a list of strings for the arguments).
    
    Example:
    If the user says "what's the weather in Paris?", your response should be:
    {{"tool": "weather", "args": ["Paris"]}}
    
    If no other tool is appropriate, use the "conversation" tool.
    Example:
    If the user says "hello", your response should be:
    {{"tool": "conversation", "args": ["Hello! How can I help you?"]}}
    """

    full_prompt = {
        "model": "llama3",
        "stream": False,
        "system": system_prompt,
        "prompt": prompt
    }

    try:
        response = requests.post(config.OLLAMA_API_URL, json=full_prompt)
        response.raise_for_status()
        # Extract the JSON string from the response
        response_json = json.loads(response.text)
        return response_json.get("response", "{}")
    except requests.exceptions.RequestException as e:
        return f'{{"tool": "conversation", "args": ["I am having trouble connecting to my core intelligence. Please ensure Ollama is running.", "{e}"]}}'
