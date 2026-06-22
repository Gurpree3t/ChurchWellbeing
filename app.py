from flask import Flask, render_template, abort, request, redirect, url_for, send_file, flash
from datetime import datetime, timedelta
from io import BytesIO
import json
import re
from pathlib import Path
import pandas as pd
from werkzeug.utils import secure_filename

from config import *

from services.google_sheet import load_google_sheet
from services.scoring import calculate_points
from services.statistics import church_statistics

app = Flask(__name__)
app.secret_key = "church-wellbeing-local"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
PRAYER_REQUESTS_FILE = DATA_DIR / "prayer_requests.json"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def slugify_name(name):
    return re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-") or "member"


def read_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_prayer_requests():
    return read_json(PRAYER_REQUESTS_FILE, [])


def save_prayer_request(name, message):
    requests = load_prayer_requests()
    requests.insert(0, {
        "name": name.strip() or "Anonymous",
        "message": message.strip(),
        "created_at": datetime.now().strftime("%d %b %Y %I:%M %p")
    })
    write_json(PRAYER_REQUESTS_FILE, requests[:50])


def profile_photo_for(name):
    slug = slugify_name(name)
    for ext in ("png", "jpg", "jpeg", "webp", "gif"):
        candidate = UPLOAD_DIR / f"{slug}.{ext}"
        if candidate.exists():
            return url_for("static", filename=f"uploads/{candidate.name}")
    return None


def church_events():
    current_year = datetime.now().year
    return [
        {"type": "Birthday", "title": "June Birthday Blessings", "date": f"30 Jun {current_year}", "details": "Celebrate members with June birthdays after fellowship."},
        {"type": "Anniversary", "title": "Family Anniversary Prayer", "date": f"07 Jul {current_year}", "details": "Thanksgiving prayer for couples celebrating anniversaries."},
        {"type": "Retreat", "title": "Church Family Retreat", "date": f"18 Jul {current_year}", "details": "A day of worship, rest, teaching, and fellowship."},
        {"type": "Picnic", "title": "Community Picnic", "date": f"02 Aug {current_year}", "details": "Bring food to share and invite a friend."},
        {"type": "Sports Day", "title": "Wellbeing Sports Day", "date": f"16 Aug {current_year}", "details": "Team games, walking challenge, and family activities."}
    ]


def prepare_dashboard_data():
    df = load_google_sheet()
    df.columns = df.columns.str.strip()
    df["Age Group"] = df[COL_AGE].apply(get_age_group)
    df[COL_NAME] = df[COL_NAME].astype(str).str.upper().str.strip()

    point_columns = [
        "Steps Points",
        "Exercise Points",
        "Water Points",
        "Sleep Points",
        "Prayer Points",
        "Zoom Points",
        "Screen Time Points",
        "Total"
    ]
    df[point_columns] = df.apply(calculate_points, axis=1)

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
        .sort_values(by="Total", ascending=False)
        .reset_index(drop=True)
    )
    leaderboard.insert(0, "Rank", leaderboard.index + 1)
    leaderboard.rename(columns={COL_NAME: "Name"}, inplace=True)

    group_map = (
        df[[COL_NAME, "Age Group"]]
        .drop_duplicates()
        .rename(columns={COL_NAME: "Name", "Age Group": "Group"})
    )
    leaderboard = leaderboard.merge(group_map, on="Name", how="left")
    return df, leaderboard


def notification_cards(df, leaderboard):
    latest_date = pd.to_datetime(df[COL_DATE], dayfirst=True, errors="coerce").max()
    submitted_today = bool(pd.notna(latest_date) and latest_date.normalize() == pd.Timestamp.now().normalize())
    rank_six = leaderboard[leaderboard["Rank"] == 6]
    return [
        {
            "icon": "🔥",
            "title": "You haven't submitted today" if not submitted_today else "Today's submission received",
            "detail": "Open the form and complete today's wellbeing entry." if not submitted_today else "Great work staying current today.",
            "level": "warning" if not submitted_today else "success"
        },
        {
            "icon": "🏅",
            "title": "New Badge Unlocked",
            "detail": "Prayer Warrior is available for consistent prayer check-ins.",
            "level": "info"
        },
        {
            "icon": "👏",
            "title": "You're now Rank #6",
            "detail": f"{rank_six.iloc[0]['Name']} is holding rank #6." if not rank_six.empty else "Keep going to reach rank #6.",
            "level": "rank"
        }
    ]


def ai_coach_message(df, leaderboard):
    display_name = leaderboard.iloc[0]["Name"].title() if not leaderboard.empty else "User"
    today = pd.Timestamp.now().normalize()
    dates = pd.to_datetime(df[COL_DATE], dayfirst=True, errors="coerce")
    this_week = df[dates >= today - pd.Timedelta(days=7)]
    previous_week = df[(dates < today - pd.Timedelta(days=7)) & (dates >= today - pd.Timedelta(days=14))]
    this_prayer = this_week["Prayer Points"].sum() if "Prayer Points" in this_week else 0
    previous_prayer = previous_week["Prayer Points"].sum() if "Prayer Points" in previous_week else 0
    trend = "dropped" if this_prayer < previous_prayer else "is holding steady"
    return {
        "name": display_name,
        "headline": f"Hello {display_name}",
        "body": f"Your prayer consistency {trend} this week.",
        "tip": "Try completing prayer before dinner."
    }


def add_period_filter(df, period):
    dates = pd.to_datetime(df[COL_DATE], dayfirst=True, errors="coerce")
    today = pd.Timestamp.now().normalize()
    if period == "weekly":
        return df[dates >= today - pd.Timedelta(days=7)]
    if period == "monthly":
        return df[dates >= today - pd.Timedelta(days=30)]
    return df

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
    df, leaderboard = prepare_dashboard_data()

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
        notifications=notification_cards(df, leaderboard),
        ai_coach=ai_coach_message(df, leaderboard),
        prayer_requests=load_prayer_requests(),
        events=church_events(),
        app_name=APP_NAME,
        church_name=CHURCH_NAME
    )


@app.post("/prayer-requests")
def submit_prayer_request():
    name = request.form.get("name", "")
    message = request.form.get("message", "")
    if message.strip():
        save_prayer_request(name, message)
        flash("Prayer request added to the wall.", "success")
    return redirect(url_for("dashboard"))


@app.route("/reports/<period>.pdf")
def report_pdf(period):
    if period not in {"weekly", "monthly"}:
        abort(404)

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    df, leaderboard = prepare_dashboard_data()
    period_df = add_period_filter(df, period)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    title = f"{period.title()} Church Wellbeing Report"
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(48, height - 56, title)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(48, height - 76, f"{CHURCH_NAME} | Generated {datetime.now().strftime('%d %b %Y %I:%M %p')}")
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(48, height - 112, f"Members: {leaderboard['Name'].nunique()}")
    pdf.drawString(190, height - 112, f"Submissions: {len(period_df)}")
    pdf.drawString(350, height - 112, f"Points: {int(leaderboard['Total'].sum())}")

    y = height - 155
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(48, y, "Rank")
    pdf.drawString(95, y, "Name")
    pdf.drawString(380, y, "Group")
    pdf.drawString(485, y, "Points")
    pdf.setFont("Helvetica", 10)
    for person in leaderboard.head(20).to_dict("records"):
        y -= 20
        if y < 56:
            pdf.showPage()
            y = height - 56
        pdf.drawString(48, y, str(person["Rank"]))
        pdf.drawString(95, y, str(person["Name"])[:34])
        pdf.drawString(380, y, str(person.get("Group", ""))[:16])
        pdf.drawString(485, y, str(int(person["Total"])))

    pdf.save()
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=f"{period}-church-wellbeing-report.pdf")


@app.route("/reports/export.xlsx")
def excel_export():
    df, leaderboard = prepare_dashboard_data()
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        leaderboard.to_excel(writer, sheet_name="Leaderboard", index=False)
        df.to_excel(writer, sheet_name="Submissions", index=False)
    buffer.seek(0)
    return send_file(buffer, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="church-wellbeing-export.xlsx")


@app.route("/reports/church")
def church_report():
    df, leaderboard = prepare_dashboard_data()
    stats = church_statistics(df)
    return render_template(
        "church_report.html",
        leaderboard=leaderboard.head(25).to_dict("records"),
        total_members=stats["members"],
        total_steps=stats["steps"],
        total_points=int(leaderboard["Total"].sum()),
        generated_at=datetime.now().strftime("%d %b %Y %I:%M %p"),
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
    pd.to_datetime(
        member[COL_DATE],
        dayfirst=True,
        errors="coerce"
    )
    .dropna()
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
        submissions=len(member),
        profile_photo=profile_photo_for(name),
        app_name=APP_NAME,
        church_name=CHURCH_NAME
    )


@app.post("/member/<name>/photo")
def upload_profile_photo(name):
    upload = request.files.get("profile_photo")
    if not upload or not upload.filename:
        return redirect(url_for("member_profile", name=name))

    ext = secure_filename(upload.filename).rsplit(".", 1)[-1].lower()
    if ext not in {"png", "jpg", "jpeg", "webp", "gif"}:
        flash("Please upload a PNG, JPG, WEBP, or GIF image.", "warning")
        return redirect(url_for("member_profile", name=name))

    slug = slugify_name(name)
    for existing in UPLOAD_DIR.glob(f"{slug}.*"):
        existing.unlink(missing_ok=True)
    upload.save(UPLOAD_DIR / f"{slug}.{ext}")
    flash("Profile picture updated.", "success")
    return redirect(url_for("member_profile", name=name))

if __name__ == "__main__":
    app.run(debug=True)
