# Pathways Grand Prix Challenge Dashboard

## 🏎️ Overview
The **Pathways Grand Prix Challenge Dashboard** is a Streamlit-powered web application hosted via Google Cloud Run that visualizes participant progress in the **Softtalk Toastmasters Pathways Grand Prix Challenge (March 6th - May 1st, 2025)**. It pulls real-time data from Google BigQuery and displays:

- **Race progress** for each participant with a visual race track 🏁
- **Leaderboard rankings** for each Pathways Level 🏆

The dashboard makes tracking speech progress engaging and interactive by displaying race cars moving along a track based on progress.

*Access application [here.](https://bit.ly/tm-pathwaysgrandprix)*

---

## 🚀 Features
- **BigQuery Integration**: Fetches real-time race progress from `tm-pathwaysgrandprix.toastmasters_race.race_progress`.
- **Race Track Visualization**: Participants' cars move forward based on speech progress.
- **Leaderboard by Pathways Level**: Displays top 3 participants for each level.
- **Custom Car Colors**: Each participant's car color matches their assigned theme.

---

## 📊 BigQuery Data Structure
The dashboard retrieves race progress from the `tm-pathwaysgrandprix.toastmasters_race.race_progress` table. The relevant columns are:

| Column | Description |
|--------|-------------|
| `Name` | Participant’s name |
| `Level` | Current Pathways level |
| `Speeches_Left` | Number of speeches left to complete the level |
| `Total_Speeches_Completed` | Total number of speeches given |
| `Color` | Car color assigned to the participant |

---

## 🎨 Image Assets
Ensure that the following images are included in the project directory:

| File | Purpose |
|------|---------|
| `tmlogo.png` | Toastmasters logo displayed in the header |
| `car.png` | Default race car image |
| `/cars/{color}.png` | Custom race cars for different participants (stored in `/cars/` folder) |

If any images are missing, errors will be displayed in Streamlit.

---

## 🏁 How Progress is Calculated
Participants' race progress is visually represented on a race track. The logic for positioning:

```python
if row["Total_Speeches_Completed"] == 0:
    progress = 0
elif row["Speeches_Left"] > 0:
    progress = (row["Total_Speeches_Completed"] / 2)  # Partial progress before completing a level
else:
    progress = min(row["Total_Speeches_Completed"] / 2, 1)  # Fully completed level
```
The race car's position is adjusted dynamically using CSS.

---

## 🏆 Leaderboard Rankings
Participants are ranked within their **Pathways Level** based on:
1. **Fewest speeches left** (ascending order)
2. **Most speeches completed** (descending order, in case of ties)

---

## 📬 Contact
For questions, reach out via [GitHub Issues](https://github.com/lkbbad/TMPathwaysGrandPrix/issues).  







---
<p style="text-align: left; font-size: 14px;">
    <a href="https://www.flaticon.com/free-icons/sports-and-competition" title="sports and competition icons" target="_blank">
        Sports and competition icons created by Freepik - Flaticon
    </a>
</p>
