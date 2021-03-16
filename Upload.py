import pickle
import os.path
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def authorization(client_secret_file, api_name, api_version, scope):
    creds = None

    # loads already created token
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # no previously created token or token is expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # token refreshing
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scope)  # token generation
            creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)  # saving access token in token.pickle
    # creating Resource for interaction with API
    drive_service = build(api_name, api_version, credentials=creds, )
    return drive_service


def upload(folder_name, file_name, user_email=None, access=None):
    mime = 'application/vnd.google-apps.folder'  # MIME type - identifies file format
    folder_identifier = None
    page_token = None

    # CHECKS IF FOLDER ALREADY EXISTS
    response = service.files().list(q="mimeType='application/vnd.google-apps.folder'",
                                    spaces='drive',
                                    fields='nextPageToken, files(id, name)',
                                    pageToken=page_token).execute()
    for file in response.get('files', []):
        if file.get('name') == folder_name:
            folder_identifier = file.get('id')
            # gets permissions on the file
            perm = service.permissions().list(fileId=folder_identifier,
                                              fields='permissions(emailAddress, role)').execute()
            # deletes owner email from permissions list
            shared_users = [i for i in perm['permissions'] if not (i['role'] == 'owner')]
            # print(shared_users)
            break

    # IF NO FOLDER CREATED
    if not folder_identifier:
        # creating folder
        folder_metadata = {  # resources are represented by metadata
            'name': folder_name,
            'mimeType': mime
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()  # creates folder
        folder_identifier = folder.get('id')  # gets folder id for creating permission
        # shares folder
        if user_email and access:
            permission_body = {
                "kind": "drive#permission", "type": "user",
                "emailAddress": user_email, "role": access
            }
            service.permissions().create(fileId=folder_identifier, body=permission_body).execute()
    # IF FOLDER CREATED
    else:
        # IF NOT SHARED WITH ANYONE
        if not shared_users:
            # IF WE WANT TO SHARE WITH SOMEONE
            if user_email and access:
                permission_body = {
                    "kind": "drive#permission", "type": "user",
                    "emailAddress": user_email, "role": access
                }
                service.permissions().create(fileId=folder_identifier, body=permission_body).execute()
            # IF NO, WE MOVE ON
            else:
                pass
        # IF SHARED WITH SOMEONE
        else:
            for user in shared_users:
                # IF WE HAVE GIVEN SAME EMAIL AGAIN
                if user['emailAddress'] == user_email and user['role'] == access:
                    pass
                # IF WE HAVE GIVEN SAME EMAIL BUT OTHER ROLE ('reader' , 'writer')
                # WE ARE CREATING NEW FOLDER WITH SIMILAR NAME
                elif user['emailAddress'] == user_email and user['role'] != access:
                    suffix = str(datetime.datetime.now())
                    folder_metadata = {
                        'name': folder_name + " " + suffix[:-7],
                        'mimeType': mime
                    }
                    folder = service.files().create(body=folder_metadata, fields='id').execute()  # creates folder
                    folder_identifier = folder.get('id')  # gets folder id for creating permission
                    permission_body = {
                        "kind": "drive#permission", "type": "user",
                        "emailAddress": user_email, "role": access
                    }
                    service.permissions().create(fileId=folder_identifier, body=permission_body).execute()
                # IF WE WANT TO SHARE FOLDER WITH NEXT PERSON
                else:
                    permission_body = {
                        "kind": "drive#permission", "type": "user",
                        "emailAddress": user_email, "role": access
                    }
                    service.permissions().create(fileId=folder_identifier, body=permission_body).execute()

    # UPLOAD
    file_metadata = {
        'name': file_name,
        'parents': [folder_identifier]  # ID of parent folder
    }

    if file_name[-4:] == ".wav":
        file_mime = 'audio / wav'
    elif file_name[-4:] == ".mp3":
        file_mime = 'audio / mpeg'
    elif file_name[-5:] == ".flac":
        file_mime = "audio / flac"
    else:
        file_mime = "image / jpeg"

    # creating MediaFileUpload object
    media = MediaFileUpload(file_name, mimetype=file_mime)
    service.files().create(  # creates file based on file and media metadata
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return None


if __name__ == '__main__':
    CLIENT_SECRET_FILE = 'json file from Google - create your own'
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']  # full scope

    # creating service
    service = authorization(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    # uploading file
    upload(folder_name="folder", file_name="jpg, wav, mp3 or flac",
           user_email="someone's email", access="reader")

