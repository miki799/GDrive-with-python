"""
Script tests uploading file to new directory
-----------------------------------------------------------------------------------------------
Imports:
    pickle
        - used for pickling and unpickling tokens.
        - 'pickling' - Python object converted into a byte stream
        - 'unpickling' - inverse operation of pickling
    os.path
        - simple pathname manipulations
    time
        - used for measuring execution time
    googleapiclient.discovery
        - provides build(serviceName, version, credentials) function which constructs Resource
        for interaction with API,
    googleapiclient.http
        - provides MediaFileUpload class
    google_auth_oauthlib.flow
        - provides InstalledAppFlow class used for acquiring tokens
    google.auth.transport.requests
        - provides Request class, Credentials class
----------------------------------------------------------------------------------------------
Functions:
    authorization():
        - generates access tokens based on provided credentials.json and saves them into a token.pickle file,
        - checks if token is valid. If not, token is refreshed.
        - constructs Resource object for interaction with API
    -----------------------------------------------------------
    create_folder():
        - creates folder in user My Drive with specified name
        - returns created folder ID
    -----------------------------------------------------------
    create_permission():
        - creates a permission for a file/folder, which grants other users access to it
        - returns None
    -----------------------------------------------------------
    upload_file():
        - uploads file to a specified folder
        - returns None

"""

import pickle
import os.path
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

CLIENT_SECRET_FILE = 'wavereco_test_pc.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']  # full scope


def authorization(client_secret_file, api_name, api_version, scope):
    """
    OAuth2 app authorization
    Parameters
    ----------
    client_secret_file: str
            Name of credentials.json file
    api_name: str
            Name of API e.g. 'drive'
    api_version: str
            Version of API
    scope: [str]
            Scope of access

    Returns
    -------
    drive_service: Resource object
        Resource with methods for interaction with API
    """

    creds = None

    # if token already exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # if no tokens or token is expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # token refreshing
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scope)  # token generation
            creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)  # saving access token in token.pickle

    drive_service = build(api_name, api_version, credentials=creds)  # constructs Resource for interaction with API
    print("Authorization complete!")
    return drive_service


def create_folder(name):
    """
    Creates folder in user My Drive
    Parameters
    ----------
    name: str
          Folder name

    Returns
    -------
    identifier: str
          Folder ID sequence
    """
    mime = 'application/vnd.google-apps.folder'  # MIME type - identifies file format

    folder_metadata = {  # resources are represented by metadata
        'name': name,
        'mimeType': mime
    }
    folder = service.files().create(body=folder_metadata, fields='id').execute()  # creates folder specified in metadata
    identifier = folder.get('id')  # gets folder id

    permission_body = {
        "kind": "drive#permission",
        "type": "user",
        "emailAddress": 'mikolaj.telec@gmail.com',
        "role": "reader"
    }
    service.permissions().create(fileId=identifier, body=permission_body).execute()

    print("Folder created!")
    return identifier


def create_permission(file_identifier, permission_type, email_address, access_role):
    """
     Creates permission (shares) for file/folder
     Parameters
     ----------
     file_identifier: str
           File/folder ID

     permission_type: str
           Permission type ('user', 'group', 'domain', 'anyone')

     email_address: str
           Email address of users you want to share

     access_role: str
           User access ('onwer', 'organizer', 'fileOrganizer', 'writer', 'commenter', 'reader')

     Returns
     -------
        None
     """

    permission_body = {                         # creates Permission body
        "kind": "drive#permission",
        "type": permission_type,                # 'user', 'group' etc.
        "emailAddress": email_address,          # user or users e-mail address
        "role": access_role,                    # what user/s can do
        "sendNotificationEmail": True,          # notification to gmail
    }

    service.permissions().create(fileId=file_identifier, body=permission_body).execute()

    return None


def upload_file(file_name, file_mime, dir_id):
    """
    Uploads file to specified folder
    Parameters
    ----------
    file_name: str
        File name
    file_mime: str
        Defines file type
    dir_id: str
        Folder ID sequence
    Returns
    -------
        None
    """
    file_metadata = {  # resources are represented by metadata
        'name': file_name,
        'parents': [dir_id]  # ID of parent folder
    }

    media = MediaFileUpload(file_name, mimetype=file_mime)  # creates MediaFileUpload class object
    service.files().create(  # creates file based on file and media metadata
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print('Upload finished!')

    return None


if __name__ == '__main__':
    start_time = time.time()
    service = authorization(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)  # returns Resource object
    folder_id = create_folder('test_folder')  # creates folder
    # create_permission(folder_id, 'user', 'piotr.telec@gmail.com', 'reader')
    up_start = time.time()
    upload_file('file_example_WAV_10MG.wav', 'audio / mpeg', folder_id)  # uploads file
    end_time = time.time()
    upload_time = end_time - up_start
    execution_time = end_time - start_time

    print(f"It took {execution_time} seconds to execute program.\n",
          f"It took {upload_time} seconds to upload file")
