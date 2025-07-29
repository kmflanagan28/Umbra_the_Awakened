import datetime
from agents import inspiration_agent, knowledge_agent, memory_agent, comms_agent

def run_briefing_and_send():
    """
    This script is run automatically by the OS scheduler (e.g., at 6 AM).
    It assembles and sends the daily briefing email.
    """
    print(f"--- Assembling and Sending Briefing at {datetime.datetime.now()} ---")
    
    # 1. Gather all the components for the email
    daily_quote = inspiration_agent.get_daily_quote()
    weather_report = knowledge_agent.get_weather()
    
    # 2. Recall the specific insights logged by the morning routine
    learned_insight = memory_agent.search_memories("Learned Insight:")
    # Remove the "No memories found" default message if nothing is there yet
    if "No memories found" in learned_insight:
        learned_insight = "No new insights learned this morning."
    else:
        # Clean up the output from search_memories
        learned_insight = learned_insight.replace("Found 1 memories containing 'Learned Insight:':\n", "")
        learned_insight = learned_insight.split("] ", 1)[1] # Get text after the timestamp

    # 3. Assemble the email
    subject = f"Umbra's Daily Briefing - {datetime.date.today().strftime('%A, %B %d')}"
    body = (
        f"Good morning.\n\n"
        f"Here is your daily briefing:\n\n"
        f"--- Thought for the Day ---\n{daily_quote}\n\n"
        f"--- Today's Learning ---\n{learned_insight}\n\n"
        f"--- Weather ---\n{weather_report}\n\n"
        f"Have a productive day.\n- Umbra"
    )
    
    # 4. Send the email
    email_status = comms_agent.send_email(subject, body)
    print(f"   - {email_status}")

    print("--- Briefing Sent ---")


if __name__ == "__main__":
    run_briefing_and_send()
