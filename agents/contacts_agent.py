import csv
import os
import sys

# Add the parent directory to the path to find the 'config' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

# A simple cache to avoid reading the file every single time
_contacts_cache = None

def _load_contacts():
    """
    Loads contacts from the CSV file into a cache for faster access.
    This function is for internal use by the agent.
    """
    global _contacts_cache
    if _contacts_cache is not None:
        return _contacts_cache

    contacts = []
    if not os.path.exists(config.CONTACTS_FILE_PATH):
        print(f"⚠️  Contacts file not found at '{config.CONTACTS_FILE_PATH}'.")
        _contacts_cache = []
        return []

    try:
        with open(config.CONTACTS_FILE_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # --- DEBUGGING STEP ---
            # The following line will print the exact column headers from your file.
            # This helps us see if we are looking for the correct column names.
            # print(f"\n[DEBUG] Headers found in contacts.csv: {reader.fieldnames}\n")

            for row in reader:
                # --- FIX: Use the correct column headers from your specific CSV file ---
                given_name = row.get('First Name', '') # Changed from 'Given Name'
                family_name = row.get('Last Name', '')  # Changed from 'Family Name'
                full_name_from_parts = f"{given_name} {family_name}".strip()
                
                # Use the 'Name' column if it's there, otherwise use the one we built.
                contact_name = row.get('Name') or full_name_from_parts

                # Find the location from Google's various address columns
                location = row.get('Address 1 - City', '') or row.get('Address 2 - City', '')
                
                if contact_name:
                    contacts.append({
                        "name": contact_name,
                        "location": location,
                        "phone": row.get('Phone 1 - Value'),
                        "email": row.get('E-mail 1 - Value')
                    })

        _contacts_cache = contacts
        print("✅ Contacts loaded successfully.")
        return contacts
    except Exception as e:
        print(f"❌ Error reading contacts file: {e}")
        _contacts_cache = []
        return []

def find_contact(name_query: str):
    """
    Searches the loaded contacts for a name. This version is more forgiving.
    Returns the contact's data dictionary if a match is found, otherwise None.
    """
    contacts = _load_contacts()
    if not contacts:
        return None
    
    search_name = name_query.lower().strip()
    
    for contact in contacts:
        contact_name = contact.get('name')
        if contact_name and search_name in contact_name.lower():
            return contact
            
    return None
