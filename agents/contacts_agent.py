import sys
import os
import csv
import re # Import the regular expressions module

# Add the parent directory to the path to find the 'config' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

def find_contact(name_to_find: str):
    """
    Finds a single contact by name from the contacts.csv file.
    This version is more robust and checks multiple name fields.
    """
    if not os.path.exists(config.CONTACTS_FILE_PATH):
        print(f"⚠️  Contacts file not found at '{config.CONTACTS_FILE_PATH}'.")
        return None

    try:
        with open(config.CONTACTS_FILE_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            contacts = list(reader)

        # print("✅ Contacts loaded successfully.")
        
        for contact in contacts:
            first_name = contact.get('First Name', '').strip()
            last_name = contact.get('Last Name', '').strip()
            full_name = f"{first_name} {last_name}".strip()
            
            if name_to_find.lower() in full_name.lower():
                location = contact.get('Address 1 - Formatted', '').strip()
                return {"name": full_name, "location": location}

        return None

    except Exception as e:
        print(f"An error occurred while reading the contacts file: {e}")
        return None

def check_contacts(location_filter: str):
    """
    Searches the entire contacts.csv file for any contacts in a specific location.
    This version uses a more precise search to avoid partial word matches.
    """
    if not os.path.exists(config.CONTACTS_FILE_PATH):
        return f"Contacts file not found at '{config.CONTACTS_FILE_PATH}'."

    found_contacts = []
    try:
        with open(config.CONTACTS_FILE_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for contact in reader:
                location = contact.get('Address 1 - Formatted', '').strip()
                
                # --- SMARTER SEARCH LOGIC ---
                # This uses a regular expression to find the filter as a whole word.
                # It's case-insensitive and handles word boundaries.
                if re.search(r'\b' + re.escape(location_filter) + r'\b', location, re.IGNORECASE):
                    first_name = contact.get('First Name', '').strip()
                    last_name = contact.get('Last Name', '').strip()
                    full_name = f"{first_name} {last_name}".strip()
                    found_contacts.append(f"- {full_name} ({location})")
        
        if not found_contacts:
            return f"No contacts found matching '{location_filter}'."

        return f"Found {len(found_contacts)} contacts matching '{location_filter}':\n" + "\n".join(found_contacts)

    except Exception as e:
        return f"An error occurred while reading the contacts file: {e}"
