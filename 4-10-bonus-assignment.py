import streamlit as st
import requests
from PIL import Image
from io import BytesIO

def getImage(file_id):
    image_url = f"https://drive.google.com/uc?export=view&id={file_id}"
    response = requests.get(image_url)
    
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        st.image(image, caption="");
    else:
        return f"Failed to load image. Error: {response.status_code}"

image = getImage("16QWDgh3PDw8_NRo0_EjupTLtg_8OrRdT") # full link: # https://drive.google.com/file/d/16QWDgh3PDw8_NRo0_EjupTLtg_8OrRdT/view?usp=drive_link
if image is not None:
    st.write(image)