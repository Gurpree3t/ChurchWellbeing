from flask import Flask, render_template
from datetime import datetime
import pandas as pd

from config import *

from services.google_sheet import load_google_sheet
from services.scoring import calculate_points
from services.statistics import church_statistics

app = Flask(__name__)


@app.route("/")
def dashboard():

    # ==========================
    # Load Google Sheet
    # ==========================

    df = load_google_sheet()

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

    # ==========================
    # Dashboard Statistics
    # ==========================

    stats = church_statistics(df)

    top3 = leaderboard.head(3)

    total_points = int(leaderboard["Total"].sum())

    last_updated = datetime.now().strftime("%d %b %Y %I:%M:%S %p")

    # ==========================
    # Render Page
    # ==========================

    return render_template(
        "dashboard.html",

        leaderboard=leaderboard.to_dict("records"),

        top3=top3.to_dict("records"),

        total_members=stats["members"],

        total_steps=stats["steps"],

        total_points=total_points,

        last_updated=last_updated,

        app_name=APP_NAME,

        church_name=CHURCH_NAME
    )


if __name__ == "__main__":
    app.run(debug=True)