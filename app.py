
from flask import Flask, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

KOBO_TOKEN = os.getenv("KOBO_TOKEN")
FORM_UID = os.getenv("FORM_UID")
API_URL = f"https://kf.kobotoolbox.org/api/v2/assets/{FORM_UID}/data.json"

HEADERS = {
    "Authorization": f"Token {KOBO_TOKEN}"
}

# Normalize sector names to 4 main categories
def normalize_sector(sector_raw):
    if not sector_raw:
        return "Others"
    sector = sector_raw.strip().lower()
    if sector in ["energie", "energy"]:
        return "Energy"
    elif sector in ["water & sanitation", "eau et assainissement", "water sanitation"]:
        return "Water & Sanitation"
    elif sector == "transport":
        return "Transport"
    else:
        return "Others"

@app.route("/")
def home():
    return "RASME+ API is live. Use /data endpoint to get submissions."

@app.route("/data")
def get_data():
    if not KOBO_TOKEN or not FORM_UID:
        raise Exception("KOBO_TOKEN and FORM_UID must be set in environment variables")

    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        raw_data = response.json()

        cleaned_data = []
        for item in raw_data.get("results", []):
            geo = item.get("_geolocation", [None, None])
            # Validate lat/lon presence and type
            if (isinstance(geo, list) and len(geo) == 2 and
                isinstance(geo[0], (float, int)) and isinstance(geo[1], (float, int))):
                lat = float(geo[0])
                lon = float(geo[1])
            else:
                # skip entries without valid geo location
                continue

            sector_raw = item.get("info_activity/group_description_act/sector_activity", "")
            sector = normalize_sector(sector_raw)

            collector = item.get("group_enumerator_info/name_enum", "Unknown")
            submission_date = item.get("_submission_time", None)

            cleaned_data.append({
                "latitude": lat,
                "longitude": lon,
                "sector": sector,
                "collector": collector,
                "submission_date": submission_date,
                "score": None  # Optional: add later if needed
            })

        return jsonify(cleaned_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
