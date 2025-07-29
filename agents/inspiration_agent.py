import random
import sys
import os

# Add the parent directory to the path to find other modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the specific tool we need from another agent
from agents.knowledge_agent import tavily_search
import config

def get_daily_quote():
    """
    Selects a random source from the config list, finds a quote, 
    and formats it. This is a great example of one agent using another's tool.
    """
    try:
        # 1. Pick a random person from your list in config.py
        author = random.choice(config.INSPIRATIONAL_SOURCES)
        
        # 2. Create a focused, high-quality search query
        print(f"   - Searching for a quote from {author}...")
        query = f"profound or inspirational quote by {author} about life, work, or mindset"
        
        # 3. Use the knowledge_agent's tool to perform the search
        search_result = tavily_search(query)
        
        # 4. Clean up the result and format it
        if "No search results found" in search_result:
            return "Could not find a quote today. The web is quiet."
        
        # Take the first search result, which is usually the most relevant
        first_result = search_result.split('\n- ')[1] 
        
        return f'"{first_result.strip()}"\n   - {author}'

    except Exception as e:
        print(f"   - Error finding quote: {e}")
        return "Could not find a quote today due to an error."
