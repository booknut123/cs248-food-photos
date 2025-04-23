import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import date, timedelta

# Google Sheets Setup
def load_image_map_from_sheet():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=scopes
    )
    client = gspread.authorize(creds)
    sheet = client.open("cs248-food-photos").sheet1
    st.write("sheet success")
    data = sheet.get_all_records()
    return {row["image_name"]: row["file_id"] for row in data}

# Display image from file_id
@st.cache_data
def get_image_from_mapping(image_name, file_map):
    if image_name not in file_map:
        return "No image found."

    file_id = file_map[image_name]
    image_url = f"https://drive.google.com/uc?export=view&id={file_id}"
    response = requests.get(image_url)

    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        st.image(image, caption="")
    else:
        return f"Failed to load image. Error: {response.status_code}"

# Sample food data function
def get_sample_food_data():
    return pd.DataFrame({
        "name": ["Pasta Primavera", "Grilled Chicken", "Veggie Burger"],
        "station": ["Main", "Grill", "Vegetarian"],
        "calories": [350, 420, 290]
    })

# Main display
def display_food_menu():
    st.title("Dining Hall Menu with Images")

    food_df = get_sample_food_data()
    file_map = load_image_map_from_sheet()

    col0, col1, col2, col3, col4 = st.columns(5)
    col0.write("")
    col1.write("**Dish**")
    col2.write("**Calories**")
    col3.write("**Station**")
    col4.write("**Add**")

    for index, row in food_df.iterrows():
        col0, col1, col2, col3, col4 = st.columns(5)
        with col0:
            get_image_from_mapping(row["name"], file_map)
        col1.write(row["name"])
        col2.write(row["calories"])
        col3.write(row["station"])
        col4.button("Add", key=index)

if __name__ == '__main__':
    st.set_page_config(page_title="Menu Viewer", layout="wide")
    display_food_menu()
