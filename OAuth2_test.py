"""
Script tests OAuth2.0 authorization protocol.

Imports:
    pickle
        - used for pickling and unpickling tokens.
        - 'pickling' - Python object converted into a byte stream
        - 'unpickling' - inverse operation of pickling
    os.path
        - simple pathname manipulations
    googleapiclient.discovery
        - provides build(serviceName, version, credentials) function which constructs Resource
        for interaction with API,
    google_auth_oauthlib.flow
        - provides InstalledAppFlow class used for acquiring tokens
    google.auth.transport.requests
        - provides Request class, Credentials class
####

auth2_test():
    - generates access tokens based on provided credentials.json and saves them into a token.pickle file,
    - checks if token is valid. If not, token is refreshed.

    Returns:
        name and id of last 10 files used on user Google Drive storage.

"""

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']  # readonly scope


def auth2_test():
    creds = None

    # if token already exists
    if os.path.exists('token.pickle'):  # token.pickle will store user's tokens
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)  # returns Python object - "unpickling"

    # if no tokens or token is expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Credential refreshed !!!")
            creds.refresh(Request())  # token refreshment
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)  # creates authorization flow
            creds = flow.run_local_server(port=0)  # starts local server for user authorization, returns new token
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)  # writes the pickled representation of access tokens
                # to the token.pickle file

    service = build('drive', 'v3', credentials=creds)  # constructs Resource for interaction with API

    result = service.files().list(  # lists 10 last used files names and id's
        pageSize=10, fields="nextPageToken, files(id, name)").execute()  # files(..) specifies metadata fields
    items = result.get('files', [])

    # print(items)   # returns list with dicts

    if not items:
        print('No files found')
    else:
        print('Files:')
        for item in items:
            print(f"{item['name']}  ::::   {item['id']}")


if __name__ == '__main__':
    auth2_test()
