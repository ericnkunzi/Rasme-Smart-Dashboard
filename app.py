import os
import requests
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

KOBO_API_KEY = os.environ.get("KOBO_API_KEY", "7a188f9457864dd166c64b0d070ba96fa95b24fc")
KOBO_FORM_ID = "aGr5kutzkG7nrHiEyH7vCt"
KOBO_API_URL = f"https://kf.kobotoolbox.org/api/v2/assets/{KOBO_FORM_ID}/data/"

SECTOR_COLORS = {
    "Energy": "red",
    "Transport": "blue",
    "Water and sanitation": "green",
    "Others": "orange"
}

STATUS_COLORS = {
    "Completed": "green",
    "Ongoing": "blue",
    "Not started": "gray",
    "Delayed": "red"
}

def normalize_sector(sector):
    sector = sector.lower()
    if "water" in sector or "sanitation" in sector:
        return "Water and sanitation"
    elif "energy" in sector:
        return "Energy"
    elif "transport" in sector:
        return "Transport"
    else:
        return "Others"

def fetch_data():
    headers = {
        "Authorization": f"Token {KOBO_API_KEY}"
    }
    response = requests.get(KOBO_API_URL, headers=headers)
    if response.status_code != 200:
        return []
    return response.json().get("results", [])

@app.route("/data")
def get_data():
    raw_data = fetch_data()

    map_data = []
    sector_counts = {"Energy": 0, "Transport": 0, "Water and sanitation": 0, "Others": 0}
    collectors = {}
    implementation_status = {}
    projects = set()
    agencies = set()

    for entry in raw_data:
        name = entry.get("Name_of_project")
        sector = normalize_sector(entry.get("Activity_Sector", "Others"))
        lat = entry.get("latitude")
        lon = entry.get("longitude")
        alt = entry.get("altitude")
        acc = entry.get("accuracy")
        collector = entry.get("Full_name_of_the_field_contact", "Unknown")
        status = entry.get("Activity_Implementation_Status", "Unknown")
        agency = entry.get("Name_of_the_activity_Implementing_Agency", "Unknown")

        if name:
            projects.add(name)

        if lat and lon:
            map_data.append({
                "name": name,
                "sector": sector,
                "lat": float(lat),
                "lon": float(lon),
                "color": SECTOR_COLORS.get(sector, "gray")
            })

        sector_counts[sector] += 1
        agencies.add(agency)

        if collector not in collectors:
            collectors[collector] = {"count": 0, "sectors": set()}
        collectors[collector]["count"] += 1
        collectors[collector]["sectors"].add(sector)

        if status not in implementation_status:
            implementation_status[status] = 0
        implementation_status[status] += 1

    sorted_collectors = sorted(collectors.items(), key=lambda x: x[1]["count"], reverse=True)
    collectors_table = [
        {
            "name": name,
            "count": data["count"],
            "sectors": list(data["sectors"])
        } for name, data in sorted_collectors
    ]

    return jsonify({
        "map_data": map_data,
        "sector_counts": sector_counts,
        "collectors_table": collectors_table,
        "total_submissions": len(raw_data),
        "projects": list(projects),
        "implementation_status": implementation_status,
        "agencies": list(agencies)
    })

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
