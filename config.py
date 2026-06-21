# ==========================================
# Church Wellbeing Configuration
# Version : 1.0
# ==========================================

# -------------------------------
# Google Sheet CSV URL
# -------------------------------

GOOGLE_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vQkAXzQq4b-BGOfbI2SFIytBKeytN7ProFK9aQGNQgwb7ZU-BnAS9oru4sKjBSqzLiFqWELYzxaDOaN"
    "/pub?output=csv"
)

# -------------------------------
# Google Sheet Column Names
# -------------------------------

COL_NAME = "Full Name"
COL_AGE = "Age"
COL_DATE = "Date & Time"

COL_STEPS = "How many steps did you complete today?"

COL_EXERCISE = "Exercise Duration ? (minutes)"

COL_WATER = "Water Intake ? (Glasses)"

COL_SLEEP = "Sleep Duration ? (Hours)"

COL_PRAYER = "Have You Completed Today's Prayer?"

# -------------------------------
# Point System
# -------------------------------

STEP_POINTS = {
    10000: 10,
    6000: 6,
    4000: 3
}

EXERCISE_POINTS = {
    "60": 12,
    "45": 10,
    "30": 8,
    "15": 5
}

WATER_TARGET = 8
WATER_POINTS = 3

SLEEP_TARGET = 7
SLEEP_POINTS = 1

PRAYER_POINTS = 5

# -------------------------------
# Application
# -------------------------------

APP_NAME = "Church Wellbeing"

APP_VERSION = "1.0"

CHURCH_NAME = "Hindi Christian Fellowship"

THEME_COLOR = "#2563eb"