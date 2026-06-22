import pandas as pd

from config import *


def calculate_points(row):

    # -------------------
    # Steps
    # -------------------

    try:
        steps = int(row[COL_STEPS])
    except:
        steps = 0

    step_points = 0

    if steps >= 10000:
        step_points = 10

    elif steps >= 6000:
        step_points = 6

    elif steps >= 4000:
        step_points = 3

    # -------------------
    # Exercise
    # -------------------

    exercise = str(row[COL_EXERCISE]).lower()

    exercise_points = 0

    if "60" in exercise:
        exercise_points = 12

    elif "45" in exercise:
        exercise_points = 10

    elif "30" in exercise:
        exercise_points = 8

    elif "15" in exercise:
        exercise_points = 5

    # -------------------
    # Water
    # -------------------

    try:
        water = int(row[COL_WATER])
    except:
        water = 0

    water_points = 3 if water >= WATER_TARGET else 0

    # -------------------
    # Sleep
    # -------------------

    sleep = str(row[COL_SLEEP])

    sleep_points = 1 if ("7" in sleep or "8" in sleep) else 0

    # -------------------
    # Prayer
    # -------------------

    prayer = str(row[COL_PRAYER]).strip().lower()

    prayer_points = 5 if prayer == "yes" else 0

    # -------------------
    # Zoom Meeting
    # -------------------

    zoom = str(row.get(COL_ZOOM, "")).strip().lower()

    zoom_points = ZOOM_POINTS if zoom == "yes" else 0

    # -------------------
    # Screen Time
    # -------------------

    screen = str(row.get(COL_SCREEN, "")).strip().lower()

    print("Screen Time Value:", screen)

    if "less than 2" in screen:
        screen_points = 10

    elif "2 to 3" in screen:
        screen_points = 5

    elif "more than 3" in screen:
        screen_points = 0

    else:
        screen_points = 0

    # -------------------
    # Total
    # -------------------

    total = (
        step_points
        + exercise_points
        + water_points
        + sleep_points
        + prayer_points
        + zoom_points
        + screen_points
    )

    return pd.Series([
        step_points,
        exercise_points,
        water_points,
        sleep_points,
        prayer_points,
        zoom_points,
        screen_points,
        total
    ])