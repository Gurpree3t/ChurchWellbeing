# ==========================================
# Church Wellbeing Configuration
# Version : 1.1
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

# NEW

COL_ZOOM = "Did you attend today's Zoom Fellowship?"

COL_SCREEN = "What was your total screen time today?"

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
# Zoom Attendance
# -------------------------------

ZOOM_POINTS = 15

# -------------------------------
# Screen Time
# -------------------------------

SCREEN_TIME_POINTS = {
    "Less than 2 hours": 10,
    "2 to 3 hours": 5,
    "More than 3 hours": 0
}

# -------------------------------
# Application
# -------------------------------

APP_NAME = "Church Wellbeing"

APP_VERSION = "1.1"

CHURCH_NAME = "Hindi Christian Fellowship"

THEME_COLOR = "#2563eb"