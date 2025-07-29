import sys
import os
import random

# Add the parent directory to the path to find other agents
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from agents import knowledge_agent, llm_agent
import config

def research_and_learn(topic: str):
    """
    This is Umbra's core autonomous research tool.
    It takes a topic, researches it online, and uses the LLM to synthesize a conclusion.
    """
    print(f"   - Researching topic: {topic}")

    # 1. DISCOVER: Find a list of items related to the topic.
    discover_prompt = f"List the names of 3 top-rated, best-selling {topic} released in the last year."
    initial_list_str = knowledge_agent.tavily_search(discover_prompt)
    
    # Simple parsing of the search result to get a list of items
    # A more robust version would use the LLM to parse this cleanly
    items_to_research = [line.strip().replace('- ', '') for line in initial_list_str.split('\n') if line.strip().startswith('- ')]
    
    if not items_to_research:
        return "Could not discover any specific items to research on that topic."

    # 2. INVESTIGATE: For each item, get a summary.
    print(f"   - Found {len(items_to_research)} items. Investigating each...")
    research_data = ""
    for item in items_to_research:
        print(f"     - Getting summary for: {item}")
        investigate_prompt = f"Provide a detailed summary of the key ideas in the book '{item}'."
        summary = knowledge_agent.tavily_search(investigate_prompt)
        research_data += f"\n\n--- Summary for {item} ---\n{summary}"

    # 3. SYNTHESIZE: Use the LLM to analyze the collected data.
    print("   - Synthesizing conclusion with LLM...")
    synthesis_prompt = f"""
    Based on the following research summaries, please act as a world-class analyst.
    Compare and contrast the key ideas from each book. 
    Identify the most unique or actionable concept, and explain why.

    Here is the research data:
    {research_data}
    """
    
    # Use the llm_agent to get the final analysis
    # We call the 'decide_next_action' but frame the prompt for direct response
    llm_decision = llm_agent.decide_next_action(synthesis_prompt)

    # Extract the conversational response from the LLM's decision
    if llm_decision.get("tool") == "conversation":
        return " ".join(llm_decision.get("args", ["Could not form a conclusion."]))
    else:
        # If the LLM didn't choose conversation, return the raw data
        return research_data