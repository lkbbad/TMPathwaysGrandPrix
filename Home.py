import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery

# Authenticate using Streamlit Secrets
credentials_dict = st.secrets["GOOGLE_SERVICE_ACCOUNT"]
credentials = service_account.Credentials.from_service_account_info(credentials_dict)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Query BigQuery to Get Race Progress
def load_data():
    query = """
    SELECT Name, Level, Speeches_Left, Total_Speeches_Completed
    FROM `YOUR_PROJECT_ID.toastmasters_race.race_progress`
    """
    df = client.query(query).to_dataframe()
    return df

# Load data into session state
if "progress_data" not in st.session_state:
    st.session_state.progress_data = load_data()

# UI: Dashboard Title
st.title("🏎️ Toastmasters Pathways Grand Prix Challenge 🏁")
st.subheader("March 6th - May 1st")

# Display progress for each participant
st.header("🚗 Race Progress")
if not st.session_state.progress_data.empty:
    sorted_data = st.session_state.progress_data.sort_values(["Level", "Speeches_Left"], ascending=[True, True])

    for _, row in sorted_data.iterrows():
        col1, col2 = st.columns([1, 5])  # Adjust column widths
        with col1:
            st.image("racecar.png", width=80, caption=row["Name"])  # Replace with actual racecar image
        with col2:
            st.write(f"**Level {int(row['Level'])}** - {row['Name']}")
            st.write(f"🏁 {int(row['Speeches_Left'])} speeches left")
            st.progress(2 - row["Speeches_Left"] if row["Speeches_Left"] <= 2 else 0)

else:
    st.write("No race progress yet. Stay tuned!")

# Leaderboard for each Pathways Level
st.header("🏆 Leaderboard by Pathways Level")

levels = sorted(st.session_state.progress_data["Level"].unique())

for level in levels:
    st.subheader(f"Level {level}")
    level_data = st.session_state.progress_data[st.session_state.progress_data["Level"] == level]
    leaderboard = level_data.sort_values(["Speeches_Left", "Total_Speeches_Completed"], ascending=[True, False]).head(3)
    
    for idx, row in leaderboard.iterrows():
        st.write(f"🥇 {row['Name']} - {row['Total_Speeches_Completed']} speeches completed")
