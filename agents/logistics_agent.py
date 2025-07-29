import requests
import sys
import os

# Add the parent directory to the path to find the 'config' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def get_route_info(args: list):
    """
    This is a 'Tool' function.
    It takes a list containing two arguments, a start and destination,
    and returns the driving distance and duration using the Google Routes API.
    """
    if len(args) < 2:
        return "Please provide both a starting location and a destination."
    
    start, destination = args[0], args[1]
    
    print(f"   - Calculating route from {start} to {destination} using Google Routes API...")

    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': config.Maps_API_KEY,
        'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters'
    }

    payload = {
        "origin": {"address": start},
        "destination": {"address": destination},
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()

        if 'routes' in data and len(data['routes']) > 0:
            route = data['routes'][0]
            distance_meters = route.get('distanceMeters', 0)
            duration_seconds_str = route.get('duration', '0s')

            # Convert distance to miles
            distance_miles = round(distance_meters * 0.000621371)

            # Parse duration (e.g., "3600s") into something human-readable
            duration_seconds = int(duration_seconds_str.replace('s', ''))
            days, remainder = divmod(duration_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, _ = divmod(remainder, 60)

            duration_str = ""
            if days > 0:
                duration_str += f"{days} day{'s' if days > 1 else ''} "
            if hours > 0:
                duration_str += f"{hours} hour{'s' if hours > 1 else ''} "
            if minutes > 0:
                duration_str += f"{minutes} minute{'s' if minutes > 1 else ''}"
            
            return f"\nRoute Information:\n- Distance: {distance_miles:,} mi\n- Est. Duration: {duration_str.strip()}"

        else:
            return "Could not find a route between the specified locations."

    except requests.exceptions.HTTPError as http_err:
        # Try to get a more specific error message from the response
        error_details = response.json().get('error', {}).get('message', str(http_err))
        return f"\nCould not find a route. Reason: {error_details}"
    except Exception as e:
        return f"\nAn unexpected error occurred: {e}"