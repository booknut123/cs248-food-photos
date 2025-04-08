import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# === FROM CHATGPT ===
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
# If modifying scopes, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Authenticate and create the API client
def authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is created automatically when the
    # authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)  # credentials.json from Google Developer Console
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Build the service to interact with Google Drive API
    service = build('drive', 'v3', credentials=creds)
    return service

def get_image(folder_id, image_name, service):
    
    # ChatGPT again
    results = service.files().list(q=f"'{folder_id}' in parents and trashed = false",
                                   fields="files(id, name)").execute()
    files = results.get('files', [])

    # === MY CODE ===
    if not files:
        st.write('No files found in the folder.')
        return None
    else:
        for file in files:
            if file['name'] == image_name:
                file_id = file['id']
                # Generate the direct image URL
                image_url = f"https://drive.google.com/uc?export=view&id={file_id}"
                response = requests.get(image_url)
    
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content)) # StackOverflow - https://stackoverflow.com/questions/7391945/how-do-i-read-image-data-from-a-url-in-python
                    st.image(image, caption="");
                else:
                    return f"Failed to load image. Error: {response.status_code}"

def main():
    # Google Drive folder ID from your URL: https://drive.google.com/drive/folders/1HTkwWKrBXl1Rhi7aWOwCJna3-jJy28S9
    folder_id = '1HTkwWKrBXl1Rhi7aWOwCJna3-jJy28S9'
    image_name = 'Maryland Crab Dip.jpg'  # Image name you are searching for
    
    service = authenticate()  # Authenticate and build the service
    image_url = get_image(folder_id, image_name, service)

if __name__ == '__main__':
    main()
