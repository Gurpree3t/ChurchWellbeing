from flask import Flask, render_template, abort
from datetime import datetime
import pandas as pd

from config import *

from services.google_sheet import load_google_sheet
from services.scoring import calculate_points
from services.statistics import church_statistics

app = Flask(__name__)

# ==========================
# Age Group Function
# ==========================

def get_age_group(age):

    try:
        age = int(age)
    except:
        return "Unknown"

    if age < 18:
        return "Under 18"

    elif age <= 40:
        return "18-40"

    else:
        return "40+"

@app.route("/")
def dashboard():

    # ==========================
    # Load Google Sheet
    # ==========================

    df = load_google_sheet()

    df.columns = df.columns.str.strip()

    df["Age Group"] = df[COL_AGE].apply(get_age_group)

   
    # ==========================
    # Standardize Names
    # ==========================

    df[COL_NAME] = (
        df[COL_NAME]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # ==========================
    # Calculate Points
    # ==========================

    df[
        [
            "Steps Points",
            "Exercise Points",
            "Water Points",
            "Sleep Points",
            "Prayer Points",
            "Zoom Points",
            "Screen Time Points",
            "Total"
        ]
    ] = df.apply(calculate_points, axis=1)

    # ==========================
    # Leaderboard
    # ==========================

    leaderboard = (
        df.groupby(COL_NAME, as_index=False)
        .agg({
            "Steps Points": "sum",
            "Exercise Points": "sum",
            "Water Points": "sum",
            "Sleep Points": "sum",
            "Prayer Points": "sum",
            "Total": "sum"
        })
        .sort_values(
            by="Total",
            ascending=False
        )
        .reset_index(drop=True)
    )

    leaderboard.insert(
        0,
        "Rank",
        leaderboard.index + 1
    )

    leaderboard.rename(
        columns={
            COL_NAME: "Name"
        },
        inplace=True
    )
    group_map = (
        df[[COL_NAME, "Age Group"]]
        .drop_duplicates()
        .rename(columns={
            COL_NAME: "Name",
            "Age Group": "Group"
        })
    )

    leaderboard = leaderboard.merge(
        group_map,
        on="Name",
        how="left"
    )

    # ==========================
    # Dashboard Statistics
    # ==========================

    stats = church_statistics(df)

    top3 = leaderboard.head(3)

    # ==========================
    # Group Leaderboards
    # ==========================

    under18 = leaderboard[
        leaderboard["Name"].isin(
            df[df["Age Group"] == "Under 18"][COL_NAME].unique()
        )
    ]

    adults = leaderboard[
        leaderboard["Name"].isin(
            df[df["Age Group"] == "18-40"][COL_NAME].unique()
        )
    ]

    seniors = leaderboard[
        leaderboard["Name"].isin(
            df[df["Age Group"] == "40+"][COL_NAME].unique()
        )
    ]
    total_points = int(leaderboard["Total"].sum())

    last_updated = datetime.now().strftime("%d %b %Y %I:%M:%S %p")

    # ==========================
    # Render Page
    # ==========================
    return render_template(
        "dashboard.html",
        leaderboard=leaderboard.to_dict("records"),
        top3=top3.to_dict("records"),
        under18=under18.to_dict("records"),
        adults=adults.to_dict("records"),
        seniors=seniors.to_dict("records"),
        total_members=stats["members"],
        total_steps=stats["steps"],
        total_points=total_points,
        last_updated=last_updated,
        app_name=APP_NAME,
        church_name=CHURCH_NAME
    )

@app.route("/member/<name>")
def member_profile(name):
    
    # ==========================
    # Load Google Sheet
    # ==========================
    
    df = load_google_sheet()

    df.columns = df.columns.str.strip()

    # ==========================
    # Standardize Names
    # ==========================

    df[COL_NAME] = (
        df[COL_NAME]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    name = name.upper().strip()

    member = df[df[COL_NAME] == name]

    if member.empty:
        abort(404)

    member[
        [
            "Steps Points",
            "Exercise Points",
            "Water Points",
            "Sleep Points",
            "Prayer Points",
            "Zoom Points",
            "Screen Time Points",
            "Total"
        ]
    ] = member.apply(calculate_points, axis=1)
    
    # ==========================
    # Daily Streak
    # ==========================

    dates = (
        pd.to_datetime(member[COL_DATE])
        .dt.normalize()
        .sort_values()
        .drop_duplicates()
        .tolist()
    )

    streak = 0

    if dates:

        today = pd.Timestamp.now().normalize()

        if dates[-1] < today:
            today -= pd.Timedelta(days=1)

        while today in dates:
            streak += 1
            today -= pd.Timedelta(days=1)

    return render_template(
        "member.html",
        member_name=name,
        total_points=int(member["Total"].sum()),
        streak=streak,
        total_steps=int(member["Steps Points"].sum()),
        exercise=int(member["Exercise Points"].sum()),
        water=int(member["Water Points"].sum()),
        sleep=int(member["Sleep Points"].sum()),
        prayer=int(member["Prayer Points"].sum()),
        zoom=int(member["Zoom Points"].sum()),
        screen=int(member["Screen Time Points"].sum()),
        submissions=len(member)
    )

if __name__ == "__main__":
    app.run(debug=True)
