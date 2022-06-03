import os


def get_user(email):
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json',
                                                      ["https://www.googleapis.com/auth/admin.directory.user.readonly"])
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', ["https://www.googleapis.com/auth/admin.directory.user.readonly"])
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('admin', 'directory_v1', credentials=creds)

    result = service.users().get(userKey=email, projection="basic", viewType="domain_public").execute()

    data = {"name": result["name"]["fullName"], "class": result["organizations"][0]["department"][-4:]}
    print(data)
    return data


if __name__ == "__main__":
    get_user("mvail24@g.holycross.edu")
