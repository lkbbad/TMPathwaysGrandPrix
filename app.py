import streamlit as st
import pandas as pd
import os
from google.oauth2 import service_account
from google.cloud import bigquery
import base64

# Get the PORT from environment variables (default to 8080 if not set)
PORT = int(os.getenv("PORT", 8080))

# Authenticate using Streamlit Secrets or Local File
if "GOOGLE_SERVICE_ACCOUNT" in st.secrets:
    credentials_dict = st.secrets["GOOGLE_SERVICE_ACCOUNT"]
else:
    import toml
    with open(".streamlit/secrets.toml", "r") as f:
        credentials_dict = toml.load(f)["GOOGLE_SERVICE_ACCOUNT"]

# Authenticate with BigQuery
credentials = service_account.Credentials.from_service_account_info(credentials_dict)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Function to get base64 image encoding
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return None

# Query BigQuery to Get Race Progress
def load_data():
    query = """
    SELECT Name, Level, Speeches_Left, Total_Speeches_Completed, Color
    FROM `tm-pathwaysgrandprix.toastmasters_race.race_progress`
    """
    df = client.query(query).to_dataframe()
    return df

# Load data into session state
if "progress_data" not in st.session_state:
    st.session_state.progress_data = load_data()

# UI: Dashboard Title
st.set_page_config(page_title="Grand Prix", page_icon="🏎️")
st.title("Pathways Grand Prix Challenge")
st.title('🏎️ 🏁 🏎️ 🏁 🏎️ 🏁 🏎️ 🏁 🏎️ 🏁 🏎️ 🏁 🏎️')
st.subheader("Softtalk Toastmasters, March 6th - May 1st")
st.image("tmlogo.png", width=200, )

# Display progress for each participant
st.divider()
st.header("🏁 Race Progress")

# Load the racecar image
racecar_path = "car.png"  # Ensure this file exists in your project directory
if not os.path.exists(racecar_path):
    st.error("⚠️ car.png not found! Make sure it's in the project directory.")

if not st.session_state.progress_data.empty:
    sorted_data = st.session_state.progress_data.sort_values(["Level", "Speeches_Left"], ascending=[True, True])
    
    for _, row in sorted_data.iterrows():
        if row["Total_Speeches_Completed"] == 0:
            progress = 0  # No progress if they haven't given any speeches
        elif row["Speeches_Left"] > 0:
            progress = (row["Total_Speeches_Completed"] / 2)  # Partial progress before completing a level
        else:  # Level is completed
            progress = min(row["Total_Speeches_Completed"] / 2, 1)

        racecar_position = progress * 100  # Convert to percentage for CSS positioning

        # Construct file path for racecar
        car_color = row["Color"].lower()  # Convert to lowercase for consistency
        car_image_path = f"cars/{car_color}.png"

        # Load car image
        car_base64 = get_base64_image(car_image_path)
        if car_base64 is None:
            st.error(f"⚠️ Missing image for {car_color}.png in /cars directory!")
            continue  # Skip this entry if the image is missing

        car_src = f"data:image/png;base64,{car_base64}"

        # Create race track with a moving racecar
        race_html = f"""
        <div style="position: relative; width: 100%; height: 40px; background-color: #ddd; border-radius: 20px;">
            <img src="{car_src}" width="75px" style="position: absolute; left: {racecar_position}%; top: -10px; transform: translateX(-50%);">
        </div>
        """

        st.subheader(f"{row['Name']} - Level {row['Level']}")
        st.markdown(race_html, unsafe_allow_html=True)

else:
    st.write("No race progress yet. Stay tuned!")

# Leaderboard for each Pathways Level
st.divider()
st.header("🏆 Leaderboard by Pathways Level")

levels = sorted(st.session_state.progress_data["Level"].unique())

for level in levels:
    st.subheader(f"Level {level}")
    level_data = st.session_state.progress_data[st.session_state.progress_data["Level"] == level]
    
    # Sort by speeches left (ascending) then total speeches completed (descending)
    leaderboard = level_data.sort_values(["Speeches_Left", "Total_Speeches_Completed"], ascending=[True, False]).head(3)

    for idx, row in leaderboard.iterrows():
        st.write(f"🥇 {row['Name']} - {row['Total_Speeches_Completed']} speeches completed")


st.markdown(
    """
    ---
    <p style="text-align: center; font-size: 14px;">
        <a href="https://www.flaticon.com/free-icons/sports-and-competition" title="sports and competition icons" target="_blank">
            Sports and competition icons created by Freepik - Flaticon
        </a>
    </p>
    """,
    unsafe_allow_html=True
)
