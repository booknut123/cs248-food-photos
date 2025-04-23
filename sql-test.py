import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import pandas as pd
import sqlite3
from datetime import date, timedelta

# ========== DATABASE FUNCTIONS ==========

def create_db():
    conn = sqlite3.connect("image_map.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS image_mapping (
            name TEXT PRIMARY KEY,
            file_id TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_mapping(name, file_id):
    conn = sqlite3.connect("image_map.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO image_mapping (name, file_id) VALUES (?, ?)", (name, file_id))
    conn.commit()
    conn.close()

def get_file_id(name):
    conn = sqlite3.connect("image_map.db")
    c = conn.cursor()
    c.execute("SELECT file_id FROM image_mapping WHERE name = ?", (name,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

@st.cache_data
def get_all_mappings():
    conn = sqlite3.connect("image_map.db")
    df = pd.read_sql_query("SELECT * FROM image_mapping", conn)
    conn.close()
    return dict(zip(df["name"], df["file_id"]))

# ========== IMAGE DISPLAY ==========

def get_image_from_sql(name, mapping=None):
    if mapping:
        file_id = mapping.get(name)
    else:
        file_id = get_file_id(name)

    if not file_id:
        return "No image found."

    image_url = f"https://drive.google.com/uc?export=view&id={file_id}"
    response = requests.get(image_url)

    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        st.image(image, caption="")
    else:
        st.error(f"Failed to load image. Error: {response.status_code}")

# ========== MENU MOCKUP (Replace with real API) ==========

def get_fake_menu():
    return [
        {"name": "Spaghetti", "station": "Pasta Bar", "calories": 400},
        {"name": "Salad", "station": "Salad Bar", "calories": 150},
        {"name": "Burger", "station": "Grill", "calories": 700},
    ]

# ========== MAIN APP ==========

def main():
    st.set_page_config(page_title="Food Menu Viewer", layout="wide")
    st.title("🍽️ Dining Hall Menu with Images")
    create_db()

    mapping = get_all_mappings()

    today = date.today()
    d = st.date_input("Choose date", value=today)

    menu = get_fake_menu()

    col0, col1, col2, col3, col4 = st.columns(5)
    col0.write("📷")
    col1.write("**Dish**")
    col2.write("**Calories**")
    col3.write("**Station**")
    col4.write("**Add**")

    for i, item in enumerate(menu):
        col0, col1, col2, col3, col4 = st.columns(5)
        with col0:
            get_image_from_sql(item["name"], mapping)
        col1.write(item["name"])
        col2.write(item["calories"])
        col3.write(item["station"])
        col4.button("Add", key=i)

if __name__ == "__main__":
    main()
