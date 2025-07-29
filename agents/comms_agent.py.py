import base64
from email.mime.text import MIMEText
import os
import sys

# Google API Client Libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Add the parent directory to the path to find the 'config' module
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def send_email(subject: str, body: str):
    """
    This is a 'Tool' function.
    It sends an email using the Gmail API with OAuth 2.0.
    The first time it runs, it will require user authorization.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # IMPORTANT: The 'credentials.json' file you downloaded from Google
            # must be in the same directory as this script.
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Create the email message object
        message = MIMEText(body)
        message['to'] = config.YOUR_EMAIL
        message['from'] = config.UMBRA_EMAIL
        message['subject'] = subject
        
        # Encode the message in base64
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }
        
        # Call the Gmail API to send the email
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        
        return f"✅ Email sent successfully. Message ID: {send_message['id']}"

    except HttpError as error:
        return f"❌ Failed to send email. An HTTP error occurred: {error}"
    except Exception as e:
        return f"❌ Failed to send email. An unexpected error occurred: {e}"