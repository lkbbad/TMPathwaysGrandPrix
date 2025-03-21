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
    SELECT Name, Level, Speeches_Left, Total_Speeches_Completed, Color, Finishing_Position
    FROM `tm-pathwaysgrandprix.toastmasters_race.race_progress`
    """
    df = client.query(query).to_dataframe()
    return df

# Load data into session state
if "progress_data" not in st.session_state:
    st.session_state.progress_data = load_data()

# Function to update finishing position in BigQuery
def update_finishing_position(name, level, finishing_position):
    query = f"""
    UPDATE `tm-pathwaysgrandprix.toastmasters_race.race_progress`
    SET Finishing_Position = {finishing_position}
    WHERE Name = '{name}' AND Level = {level}
    """
    client.query(query).result()  # Wait for the query to complete

# Function to assign finishing positions for finishers (only top 3 per level)
def assign_finishing_positions(df):
    for level in sorted(df["Level"].unique()):
        # Filter racers who have finished (Speeches_Left == 0)
        finishers = df[(df["Level"] == level) & (df["Speeches_Left"] == 0)]
        # Sort finishers using Total_Speeches_Completed as a proxy for finishing order
        finishers_sorted = finishers.sort_values("Total_Speeches_Completed", ascending=True)
        for i, (index, row) in enumerate(finishers_sorted.iterrows(), start=1):
            if i > 3:
                break  # Only assign 1st, 2nd, and 3rd place
            if pd.isna(row.get("Finishing_Position")):
                update_finishing_position(row["Name"], row["Level"], i)
                df.at[index, "Finishing_Position"] = i

# Assign finishing positions if not already set
assign_finishing_positions(st.session_state.progress_data)

# UI: Dashboard Title
st.set_page_config(page_title="Grand Prix", page_icon="🏎️")
st.title("Pathways Grand Prix Challenge")
st.title('🏎️ 🏁 🏎️ 🏁 🏎️ 🏁 🏎️ 🏁 🏎️ 🏁 🏎️ 🏁 🏎️')
st.subheader("Softtalk Toastmasters, March 6th - May 1st")
st.image("tmlogo.png", width=200, )

# Display progress for each participant
st.divider()
st.header("🏁 Race Progress")

if not st.session_state.progress_data.empty:
    sorted_data = st.session_state.progress_data.sort_values(["Level", "Speeches_Left"], ascending=[True, True])
    
    for _, row in sorted_data.iterrows():
        # Calculate total speeches required (must be at least 2)
        total_speeches_required = max(2, row["Speeches_Left"] + row["Total_Speeches_Completed"])

        # Calculate progress based on how many speeches have been given
        progress = row["Total_Speeches_Completed"] / total_speeches_required

        # Ensure progress stays between 0 and 1
        progress = max(0, min(progress, 1))

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

# New section: Display Race Winners (Finishing Positions)
st.divider()
st.header("🎉 Race Winners")

levels = sorted(st.session_state.progress_data["Level"].unique())
for level in levels:
    # Filter finishers (those with Speeches_Left == 0)
    finishers = st.session_state.progress_data[(st.session_state.progress_data["Level"] == level) &
                                                 (st.session_state.progress_data["Speeches_Left"] == 0)]
    
    medal = None
    if not finishers.empty:
        st.subheader(f"Level {level} Winners")
    #     st.write("No finishers yet for this level.")
    # else:
        # Sort by the assigned finishing position
        finishers_sorted = finishers.sort_values("Finishing_Position")
        for _, row in finishers_sorted.iterrows():
            if row["Finishing_Position"] == 1:
                medal = "🥇"
            elif row["Finishing_Position"] == 2:
                medal = "🥈"
            elif row["Finishing_Position"] == 3:
                medal = "🥉"
            st.write(f"{medal} {row['Name']} has finished and secured {int(row['Finishing_Position'])} place!")

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