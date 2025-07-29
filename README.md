Umbra the Awakened
📖 Overview
Umbra is a personalized, command-line AI assistant designed to act as a synergistic partner. It helps gather and analyze information, manage personal data, and automate tasks through a system of specialized agents.

✨ Core Features
Orchestrator-Agent Architecture: A central orchestrator delegates tasks to specialized agents for memory, knowledge, travel, and communication.

Persistent Memory: Umbra remembers information through a dedicated SQLite database.

External Knowledge: Connects to external APIs (OpenWeather, Tavily) to fetch real-time information.

Travel Database: Manages a personal database of friends and points of interest to assist in planning.

Automated Briefings: Can compose and send daily email briefings.

🚀 Getting Started
Prerequisites
Python 3.x

An API key from OpenWeatherMap

An API key from Tavily

A dedicated Gmail account with an App Password or OAuth Credentials (credentials.json) for sending emails.

Installation & Setup
Clone the repository:

git clone https://github.com/kmflanagan28/Umbra_the_Awakened.git
cd Umbra_the_Awakened

Set up the Python virtual environment:

# On Windows
python -m venv umbra-env
.\umbra-env\Scripts\activate

# On macOS/Linux
python3 -m venv umbra-env
source umbra-env/bin/activate

Install dependencies:

pip install -r requirements.txt 
# Note: We will need to create this requirements.txt file later.

Configure Umbra:

Create a config.py file and populate it with your email credentials and API keys.

Place your credentials.json file (if using OAuth) in the root directory.

Export your contacts as contacts.csv and place it in the root directory.

Run Umbra:

python orchestrator.py
