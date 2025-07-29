import datetime
from agents import learning_agent, memory_agent

def run_learning_routine():
    """
    This script is run automatically by the OS scheduler (e.g., at 4 AM).
    It performs Umbra's research tasks and logs the findings to memory.
    """
    print(f"--- Running Umbra's Morning Research Routine at {datetime.datetime.now()} ---")
    
    # 1. Define the research topic for the day
    # In the future, this could be randomly selected from a list in config.py
    topic_of_the_day = "finance books"
    
    # 2. Perform the research task
    insight = learning_agent.research_and_learn(topic_of_the_day)
    
    # 3. Log the synthesized insight to memory with a special tag
    memory_to_log = f"Learned Insight on '{topic_of_the_day}': {insight}"
    memory_agent.add_memory(memory_to_log)
    print("   - Research findings logged to memory.")
    
    print("--- Morning Routine Complete ---")

if __name__ == "__main__":
    run_learning_routine()

