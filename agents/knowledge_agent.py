import sys
import os
import requests
import json

# Add the parent directory to the path to find the 'config' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def get_weather(location=None):
    """Gets the current weather for a specified location."""
    if location is None:
        location = f"{config.HOME_CITY}"
    
    api_key = config.OPENWEATHER_API_KEY
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": api_key,
        "units": "imperial" 
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        city = data['name']
        
        return f"The weather in {city} is {temp}°F with {weather_desc}."

    except requests.exceptions.HTTPError as http_err:
        return f"Error fetching weather data: {http_err}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


def tavily_search(*args):
    """
    Performs a web search using the Tavily API.
    This version is upgraded to handle multiple arguments from the LLM.
    """
    # Join all arguments into a single query string
    query = " ".join(args)

    if not query:
        return "Search query cannot be empty."

    api_key = config.TAVILY_API_KEY
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": True,
        "max_results": 5
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        data = response.json()
        
        # Format the results into a clean string
        if "answer" in data and data["answer"]:
            return data["answer"]
        elif "results" in data and data["results"]:
            results_str = "\n".join([f"- {res['content']}" for res in data['results']])
            return f"🔎 Tavily Search Results:\n{results_str}"
        else:
            return "No search results found."

    except requests.exceptions.RequestException as e:
        return f"Error performing search: {e}"