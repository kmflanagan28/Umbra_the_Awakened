import requests
import json
import config

# This global variable will hold the combined system prompt after being loaded once.
_SYSTEM_PROMPT = None

def initialize_llm_system():
    """
    Loads the persona and context files into a persistent system prompt.
    """
    global _SYSTEM_PROMPT
    if _SYSTEM_PROMPT is not None:
        print("   - LLM system already initialized.")
        return True

    print("   - LLM is putting on its glasses...")
    try:
        with open('personas/llm_agent_persona.md', 'r', encoding='utf-8') as f:
            persona = f.read()
        with open('context_profile.md', 'r', encoding='utf-8') as f:
            context = f.read()

        _SYSTEM_PROMPT = f"{persona}\n\n--- PRIME DIRECTIVE CONTEXT ---\n{context}"
        print("   - LLM glasses are on. System prompt initialized.")
        return True
    except FileNotFoundError as e:
        print(f"\n[CRITICAL ERROR] Could not initialize LLM. Missing file: {e.filename}")
        _SYSTEM_PROMPT = "You are a helpful assistant." # Fallback
        return False

def decide_tool(user_prompt: str):
    """
    Consults the LLM to get a "thought" process and a final "decision" JSON.
    """
    if _SYSTEM_PROMPT is None:
        if not initialize_llm_system():
            return {"thought": "Critical system error.", "decision": {"tool": "conversation", "args": ["My core systems are not configured correctly."]}}

    full_prompt = f"{_SYSTEM_PROMPT}\n\nUser Prompt: \"{user_prompt}\"\n\nJSON Response:"

    try:
        payload = {
            "model": "llama3",
            "prompt": full_prompt,
            "format": "json", # Tell Ollama to enforce JSON output
            "stream": False,
            "options": {"temperature": 0.0}
        }
        response = requests.post(config.OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        # The entire response from Ollama is now expected to be a single JSON string
        response_json_str = response.json().get('response', '{}')
        # We parse this string to get the dictionary inside
        return json.loads(response_json_str)

    except requests.exceptions.RequestException as e:
        return {"thought": f"Connection error: {e}", "decision": {"tool": "conversation", "args": ["I can't connect to my core intelligence (Ollama)."]}}
    except json.JSONDecodeError:
         return {"thought": "The LLM provided a malformed response.", "decision": {"tool": "conversation", "args": ["My thought process was interrupted. Could you rephrase that?"]}}
    except Exception as e:
        return {"thought": f"An unexpected error occurred: {e}", "decision": {"tool": "conversation", "args": ["I encountered an unexpected internal error."]} }
