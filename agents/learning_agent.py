import sys
import os
import sqlite3
import datetime

# Add the parent directory to the path to find other agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents import knowledge_agent, llm_agent
import config

def _initialize_learning_log():
    """Ensures the learning log database and its table exist."""
    conn = sqlite3.connect(config.LEARNING_LOG_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            topic TEXT NOT NULL,
            summary TEXT NOT NULL,
            source TEXT 
        )
    """)
    conn.commit()
    conn.close()

# Initialize the database when the agent is loaded
_initialize_learning_log()


def research_market_trends(item_name: str):
    """
    This is an autonomous research tool. It researches the 'sold' listings for
    an item on eBay, uses the LLM to analyze the data, and logs the findings.
    """
    print(f"   - Researching market trends for: {item_name}")

    # 1. DISCOVER: Use the knowledge agent to find raw data
    discover_prompt = f"Find the 5 most recent 'sold' listings for '{item_name}' on eBay.com. Include the price and date for each."
    raw_data = knowledge_agent.tavily_search(discover_prompt)
    
    if "No search results found" in raw_data:
        return f"Could not find any recent sold listings for '{item_name}'."

    # 2. SYNTHESIZE: Use the LLM to analyze the raw data
    print("   - Synthesizing market analysis with LLM...")
    synthesis_prompt = f"""
    You are a market analyst. Based on the following raw data of recently sold eBay listings,
    calculate the average sale price and provide a brief summary of the market activity for '{item_name}'.

    RAW DATA:
    ---
    {raw_data}
    ---
    """
    
    llm_response = llm_agent.decide_tool(synthesis_prompt)
    
    # Extract the conversational response from the LLM's decision
    thought = llm_response.get("thought", "Analysis failed.")
    decision = llm_response.get("decision")
    
    if decision and decision.get("tool") == "conversation":
        analysis_summary = " ".join(decision.get("args", ["Could not form a conclusion."]))
    else:
        analysis_summary = f"Analysis was inconclusive. Raw thought: {thought}"

    # 3. LOG: Save the structured findings to the learning log
    print("   - Saving analysis to the Learning Log...")
    conn = sqlite3.connect(config.LEARNING_LOG_PATH)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO learnings (timestamp, topic, summary, source) VALUES (?, ?, ?, ?)",
        (timestamp, item_name, analysis_summary, "eBay Sold Listings")
    )
    conn.commit()
    conn.close()
    
    return f"Market research for '{item_name}' complete and logged."

