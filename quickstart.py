from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://mail.google.com/', 'https://www.googleapis.com/auth/gmail.compose']

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {
        'raw': raw_message.decode("utf-8")
    }

def create_draft(service, user_id, message_body):
    try:
        message = {'message': message_body}
        draft = service.users().drafts().create(userId=user_id, body=message).execute()

        print("Draft id: %s\nDraft message: %s" % (draft['id'], draft['message']))

        return draft
    except Exception as e:
        print('An error occurred: %s' % e)
        return None  

# def create_draft(service, user_id, message_body):
#     """Create and insert a draft email. Print the returned draft's message and id.

#     Args:
#     service: Authorized Gmail API service instance.
#     user_id: User's email address. The special value "me"
#     can be used to indicate the authenticated user.
#     message_body: The body of the email message, including headers.

#     Returns:
#     Draft object, including draft id and message meta data.
#     """
#     message = {'message': message_body}
#     draft = service.users().drafts().create(userId=user_id, body=message).execute()

#     print('Draft id: %s\nDraft message: %s' % (draft['id'], draft['message']))

#     return draft

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
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
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])

    # Get the profile
    profile = service.users().getProfile(userId='me').execute()

    if not profile:
        print('No profile')
    else:
        print(profile['emailAddress'])

    # Create a draft
    messageText = "Test Email"
    messageBody = create_message(sender=profile['emailAddress'], to='sinhvtr@gmail.com', subject='Test', message_text=messageText)
    create_draft(service=service, user_id='me', message_body=messageBody)

if __name__ == '__main__':
    main()