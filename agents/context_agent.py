import sys
import os

# Add parent directory to path to find other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.memory_agent import get_recent_conversations
from agents.llm_agent import decide_tool # We use the core LLM to summarize
import config

def update_context_from_chat(num_messages: int = 20):
    """
    Summarizes the recent web chat history and appends the insights
    to the main context_profile.md file.
    """
    print("   - Accessing recent conversation history from memory...")
    # 1. Get recent chat history from the Memory Agent
    recent_chats = get_recent_conversations("WebApp Conversation", num_messages)

    if "No memories found" in recent_chats:
        print("   - No recent web conversations to analyze.")
        return "No recent web conversations to analyze."

    print("   - Summarizing conversation with LLM...")
    # 2. Create a prompt for the LLM to summarize the conversation
    summarization_prompt = (
        f"You are a context analysis engine. Your task is to read the following conversation "
        f"between Kyle and Umbra and extract any new, meaningful information that should be permanently "
        f"added to Umbra's core context profile. Focus on new goals, preferences, philosophies, or direct instructions. "
        f"Summarize these key takeaways as a few concise bullet points. If no new context is revealed, respond with 'No new context learned.'\n\n"
        f"--- CONVERSATION LOG ---\n{recent_chats}"
    )

    # 3. Use the LLM to get the summary
    # We call decide_tool here as a way to directly interface with the LLM
    llm_response = decide_tool(summarization_prompt)
    
    # The actual summary will be in the 'thought' or a 'conversation' arg
    summary = llm_response.get("thought")
    if not summary or "No new context" in summary:
        decision = llm_response.get("decision")
        if decision and decision.get("tool") == "conversation":
            summary = " ".join(decision.get("args", []))

    if "No new context" in summary:
        print("   - LLM determined no new context was learned.")
        return "Analyzed conversation, but no new context was learned."

    print("   - Appending summary to context profile...")
    # 4. Append the summary to the context_profile.md file
    try:
        with open(config.CONTEXT_PROFILE_PATH, "a") as f:
            f.write("\n\n---\n")
            f.write(f"## Learned from Conversation ({config.get_current_timestamp('%Y-%m-%d')})\n")
            f.write(summary)
        
        success_message = "Successfully analyzed conversation and updated my context profile."
        print(f"   - {success_message}")
        return success_message
    except Exception as e:
        error_message = f"Error writing to context profile: {e}"
        print(f"   - {error_message}")
        return error_message
