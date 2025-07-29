import re

def sanitize_address(address: str):
    """
    Checks if an address string likely contains a specific street number
    and redacts it if it does.

    Args:
        address (str): The full address string to check.

    Returns:
        str: The sanitized address string.
    """
    if not isinstance(address, str):
        return ""

    # This regular expression looks for a pattern of numbers at the start
    # of the string, which usually indicates a street address.
    # e.g., "123 Main St" matches, but "Boston, MA" does not.
    if re.search(r'^\d+\s', address.strip()):
        return "[REDACTED - Street Address]"
    else:
        # If no street number is found, the address is considered safe to display.
        return address

def sanitize_contact_location(location: str):
    """
    Takes a potentially multi-line location string and sanitizes each part.
    This handles cases where a contact has multiple addresses.

    Args:
        location (str): The location string from the contacts file.

    Returns:
        str: The fully sanitized location string, safe for display.
    """
    if not isinstance(location, str):
        return ""
        
    # Split the location string by ':::' in case of multiple addresses
    parts = location.split(':::')
    
    sanitized_parts = []
    for part in parts:
        # Sanitize each individual address part
        clean_part = sanitize_address(part.strip())
        sanitized_parts.append(clean_part)
        
    # Join them back together for display
    return " ::: ".join(sanitized_parts)
