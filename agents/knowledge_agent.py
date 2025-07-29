import json
import os
import sys
import requests

# Add the parent directory to the path to find the 'config' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def get_weather(location: str = None):
    """
    This is a 'Tool' function.
    It gets the current weather for a given location using the OpenWeatherMap API.
    If no location is provided, it combines the default city and country from the config.
    """
    query_location = location
    
    if query_location is None:
        # If no location is provided, build a more specific query from the config
        query_location = f"{config.DEFAULT_CITY},{config.DEFAULT_COUNTRY}"

    # The base URL for the OpenWeatherMap API
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    # Parameters to send with the API request
    params = {
        "q": query_location,
        "appid": config.OPENWEATHER_API_KEY,
        "units": "imperial" # Use 'metric' for Celsius
    }
    
    try:
        response = requests.get(base_url, params=params)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status() 
        
        weather_data = response.json()
        
        city_name = weather_data['name']
        main_weather = weather_data['weather'][0]['main']
        description = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        
        return f"The weather in {city_name} is {temp}°F with {description}."
        
    except requests.exceptions.RequestException as e:
        # Provide a more user-friendly error message
        return f"Error fetching weather data. Please check your connection or API key. Details: {e}"
    except KeyError:
        return f"Error: Could not parse weather data. The city '{query_location}' might not be found."


def tavily_search(query: str):
    """
    This is a 'Tool' function.
    It performs a web search using the Tavily API to answer a question.
    """
    if not config.TAVILY_API_KEY:
        return "Error: Tavily API key is not set in the config file."

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": config.TAVILY_API_KEY,
                "query": query,
                "search_depth": "basic",
                "max_results": 3,
            },
        )
        response.raise_for_status()
        
        search_results = response.json()
        
        # Format the results into a readable string
        formatted_response = "🔎 Tavily Search Results:\n"
        for result in search_results.get("results", []):
            formatted_response += f"- {result['content']}\n"
            
        return formatted_response if search_results.get("results") else "No search results found."

    except requests.exceptions.RequestException as e:
        return f"Error with Tavily search: {e}"