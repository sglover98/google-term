from __future__ import print_function
import os.path
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user', "https://www.googleapis.com/auth/admin.directory.domain"]



def suspend_user(service, email, retry):
    """Suspends a specific user in the domain."""
    try:
        user = service.users().get(userKey=email).execute()
        user['suspended'] = True
        user['orgUnitPath'] = '/suspended'
        updated_user = service.users().update(userKey=email, body=user).execute()
        print(f"User {updated_user['primaryEmail']} has been suspended.")
        
        return True
        
        
    except HttpError as e:
        error_message = e.content.decode("utf-8")
        error_details = e._get_reason()

        if "EntityNotFound" in error_message:
            print("User does not exist.")
        elif "domain_not_found" in error_message:
            print("Domain does not exist.")
        elif "userKeyInvalid" in error_message:
            print("Invalid email format.")
        else:
            print("An error occurred:", error_details)
        
        retry_input = input("Do you want to retry? (Y/N): ")
        retry[0] = retry_input.lower() == "y"
        return False


def main():
    """Shows basic usage of the Admin SDK Directory API.
    Suspends a specific user in the domain.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens and is
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

    service = build('admin', 'directory_v1', credentials=creds)

    # Call the suspend_user function to suspend a specific email
    retry = [True]  # Use a mutable list to allow updating the retry value by reference
    while retry[0]:
        email = input("Enter email: ")
        email_to_suspend = email
        success = suspend_user(service, email_to_suspend, retry)
        
        if success:
            break
            

        


if __name__ == '__main__':
    main()
