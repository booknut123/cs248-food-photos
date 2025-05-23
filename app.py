import streamlit as st
import requests
from PIL import Image
from io import BytesIO

from datetime import date, datetime, timedelta
import pandas as pd
import json

IMAGE_WIDTH = 100  # Fixed width for thumbnails
IMAGE_QUALITY = 50  # Reduce quality for faster loading

# === FROM CHATGPT ===
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate():
    creds = None
    
    # Option 1: Use pre-generated token (for Streamlit Cloud)
    if 'google_token' in st.secrets:
        creds = Credentials.from_authorized_user_info(
            info={
                "token": st.secrets["google_token"]["token"],
                "refresh_token": st.secrets["google_token"]["refresh_token"],
                "token_uri": st.secrets["google_token"]["token_uri"],
                "client_id": st.secrets["google_token"]["client_id"],
                "client_secret": st.secrets["google_token"]["client_secret"],
                "scopes": SCOPES
            },
            scopes=SCOPES
        )
    
    # Option 2: Fallback to Service Account (more reliable)
    elif 'google_service_account' in st.secrets:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["google_service_account"],
            scopes=SCOPES
        )
    
    # Check if credentials are valid/expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())  # Auto-refresh if possible
    
    if not creds:
        st.error("🚨 Google Drive authentication failed. Check your secrets.")
        return None
    
    return build('drive', 'v3', credentials=creds)

# === MY CODE ===
@st.cache_data
def get_file_mapping(folder_id, _service):
    # ChatGPT again when working with service
    results = _service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name)"
    ).execute()
    files = results.get('files', [])
    return {file['name'].split('.')[0]: file['id'] for file in files}

@st.cache_data
def get_images(file_mapping, image_name):
    if not file_mapping:
        st.write('No files found in the folder.')
        return "No image found."
    
    file_id = file_mapping.get(image_name)
    if not file_id:
        return "Image not found."
    
    # Generate the direct image URL
    image_url = f"https://drive.google.com/uc?export=view&id={file_id}"
    thumbnail_url = f"{image_url}&w={IMAGE_WIDTH}&q={IMAGE_QUALITY}"
    response = requests.get(thumbnail_url)

    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        #image.thumbnail((IMAGE_WIDTH, IMAGE_WIDTH))
        st.image(image, caption="")
    else:
        return f"Failed to load image. Error: {response.status_code}"

def getMenuJSON(locationID, mealID, d):
    base_url = "https://dish.avifoodsystems.com/api/menu-items/week"
    params = {"date":d,"locationID":locationID,"mealID":mealID}
    try:
        response = requests.get(base_url,params=params)
        return response.json()
    except:
        return

# def staticDF(data, date): #print as dataframe, includes name, category, desc
#     if data == None:
#         st.toast("We're sorry, but something went wrong.")
    
#     df = pd.DataFrame(data)
#     try:
#         df['date'] = df['date'].apply(lambda x: x.split('T')[0])
#         df = df[df['date']== str(date)]
#         df2 = pd.DataFrame(
#             {"name": df["name"],
#              "station": df["categoryName"], 
#              "description": df["description"]
#             })
#         dataframe = st.dataframe(df2, hide_index=True)
#         return dataframe
#     except:
#         st.toast("We're sorry, but something went wrong.")
#         return
    
def dynamicDF(data, date, folder_id, service): #print as columns w/ add buttons, includes name, calories, category
    if data == None:
        st.toast("We're sorry, but something went wrong.")
        
    df = pd.DataFrame(data)
    try:
        df['date'] = df['date'].apply(lambda x: x.split('T')[0])
        df = df[df['date']== str(date)]
        df2 = pd.DataFrame(
            {"name": df["name"],
             "station": df["stationName"],
             "nutrition": df["nutritionals"]
            })
    except:
        return st.toast("We're sorry, but something went wrong.")
    
    # Get file mapping once at the beginning
    file_mapping = get_file_mapping(folder_id, service)
    
    col0, col1, col2, col3, col4 = st.columns(5, vertical_alignment="top")
    col0.write("")
    col1.write("**Dish**")
    col2.write("**Calories**")
    col3.write("**Category**")
    col4.write("**Add to Journal**")
    for index, row in df2.iterrows():
        col0, col1, col2, col3, col4 = st.columns(5, vertical_alignment="top")
        with col0:
            get_images(file_mapping, row["name"])
        col1.write(row["name"])
        col2.write(pd.json_normalize(row["nutrition"])["calories"][0])
        col3.write(row["station"])
        col4.button("Add", key=index)
      
def create_streamlit():
    # Google Drive folder ID: https://drive.google.com/drive/folders/1HTkwWKrBXl1Rhi7aWOwCJna3-jJy28S9
    folder_id = '1HTkwWKrBXl1Rhi7aWOwCJna3-jJy28S9'
    image_name = ''  # Image name you are searching for
    
    service = authenticate()  # Authenticate and build the service
    
    mealDict = {
        "Bates": {"Breakfast": 145, "Lunch": 146, "Dinner": 311, "LocationID": 95},
        "Lulu": {"Breakfast": 148, "Lunch": 149, "Dinner": 312, "LocationID": 96},
        "Tower": {"Breakfast": 153, "Lunch": 154, "Dinner": 310, "LocationID": 97},
        "StoneD":{"Breakfast": 261, "Lunch": 262, "Dinner": 263, "LocationID": 131}
    }

    # location and meal columns
    col1, col2 = st.columns(2, gap = "small", vertical_alignment="center")
    with col1: location = st.selectbox("Pick a location!", ("Bates", "Lulu", "Tower", "StoneD"))
    with col2: meal = st.selectbox("Pick a meal!", ("Breakfast", "Lunch", "Dinner"))

    mealID = mealDict[location][meal]
    locationID = mealDict[location]["LocationID"]
    today = date.today().weekday()
    d = date.today()

    # date slider columns
    __, col2, __ = st.columns((0.5, 1, 0.5), gap = "small", vertical_alignment="center")
    with col2:
        values = [6, 0, 1, 2, 3, 4, 5] #our week starts on Sunday (6)
        labels = ['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']   
        selection = st.select_slider('Choose a range',values, value=today, format_func=(lambda x:labels[x]))

    if( selection == 6): selection = -1
    d = d + timedelta(days=selection - today)
    st.write("Selected Date: ", d)

    menu_shown = st.toggle("Show menu")
    if (menu_shown):
        # staticDF(getMenuJSON(locationID, mealID, d), d)
        dynamicDF(getMenuJSON(locationID, mealID, d), d, folder_id, service)


def main():    
    st.set_page_config(page_title="WF Streamlit", layout="wide")

    st.header("cs248-food-photos")
    st.subheader(f"Today: {date.today()}")
    
    create_streamlit()

if __name__ == '__main__':
    main()