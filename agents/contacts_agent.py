import csv
import os
import re

# --- Local Imports ---
import config
from agents.privacy_agent import sanitize_contact_location # <-- Import the new tool

def find_contact(name: str):
    """
    Finds a single contact by name in the contacts.csv file.
    This is primarily a helper for the 'add-friend' command.
    """
    # This function's logic remains the same.
    # It just finds the raw data.
    if not os.path.exists(config.CONTACTS_FILE_PATH):
        return {"error": "Contacts file not found."}
    
    with open(config.CONTACTS_FILE_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            first_name = row.get("First Name", "").strip()
            last_name = row.get("Last Name", "").strip()
            full_name = f"{first_name} {last_name}".strip()

            if name.lower() in full_name.lower():
                # Get the formatted address if available, otherwise build from parts
                location = row.get("Address 1 - Formatted", "").strip()
                if not location:
                    city = row.get("Address 1 - City", "").strip()
                    region = row.get("Address 1 - Region", "").strip()
                    if city and region:
                        location = f"{city}, {region}"
                
                return {"name": full_name, "location": location}
    return {}


def check_contacts(location_filter: str):
    """
    Searches the entire contacts.csv file for contacts in a specific location
    and returns a sanitized list for display.
    """
    if not os.path.exists(config.CONTACTS_FILE_PATH):
        return "⚠️ Contacts file not found at 'contacts.csv'."

    found_contacts = []
    with open(config.CONTACTS_FILE_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            location = row.get("Address 1 - Formatted", "").strip()
            
            # --- NEW: Use the Privacy Agent to sanitize the location ---
            sanitized_location = sanitize_contact_location(location)

            # Use regex to find the location_filter as a whole word, case-insensitively
            if re.search(r'\b' + re.escape(location_filter) + r'\b', location, re.IGNORECASE):
                first_name = row.get("First Name", "").strip()
                last_name = row.get("Last Name", "").strip()
                full_name = f"{first_name} {last_name}".strip()
                if full_name:
                    # Append the *sanitized* location for display
                    found_contacts.append(f"- {full_name} ({sanitized_location})")

    if not found_contacts:
        return f"No contacts found matching '{location_filter}'."
    else:
        return f"Found {len(found_contacts)} contacts matching '{location_filter}':\n" + "\n".join(found_contacts)
