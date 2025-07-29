import sys
import os
import requests
import json

# Add the parent directory to the path to find other modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def get_distance(origin: str, destination: str):
    """
    Calculates the driving distance and time between two locations
    using the modern Google Maps Routes API for precise results.
    """
    print(f"   - Calculating route from {origin} to {destination} using Google Routes API...")
    
    # --- FIX ---
    # Corrected the variable name to match config.py
    api_key = config.Maps_API_KEY
    if not api_key or "your_new" in api_key:
        return "Google Maps API key is not configured in config.py."

    # Construct the API request URL and headers
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.staticDuration,routes.localizedValues"
    }
    
    # Construct the request body
    body = {
        "origin": {"address": origin},
        "destination": {"address": destination},
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "languageCode": "en-US",
        "units": "IMPERIAL"
    }

    try:
        response = requests.post(url, data=json.dumps(body), headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        
        if 'routes' in data and data['routes']:
            # Extract the relevant information from the first route
            route = data['routes'][0]
            distance = route['localizedValues']['distance']['text']
            duration = route['localizedValues']['staticDuration']['text'] # Static duration is without traffic
            
            return (
                f"Route Information:\n"
                f"- Distance: {distance}\n"
                f"- Est. Duration: {duration}"
            )
        else:
            # Provide more detailed error info from Google
            error_details = data.get('error', {}).get('message', 'No route found.')
            return f"Could not find a route. Reason: {error_details}"

    except requests.exceptions.RequestException as e:
        return f"An error occurred while contacting the Google Maps API: {e}"
    except (KeyError, IndexError):
        return "Received an unexpected response format from the Google Maps API."