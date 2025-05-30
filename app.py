from flask import Flask, jsonify
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# KoboToolbox settings
KOBO_API_KEY = os.environ.get("KOBO_API_KEY", "7a188f9457864dd166c64b0d070ba96fa95b24fc")
DATA_URL = "https://kf.kobotoolbox.org/api/v2/assets/aGr5kutzkG7nrHiEyH7vCt/data/"

# Normalize sector
def normalize_sector(value):
    if not value:
        return "Others"
    value = value.strip().lower()
    if "energy" in value:
        return "Energy"
    elif "transport" in value:
        return "Transport"
    elif "water" in value or "sanitation" in value:
        return "Water and Sanitation"
    else:
        return "Others"

@app.route("/api/projects")
def get_projects():
    headers = {
        "Authorization": f"Token {KOBO_API_KEY}"
    }

    try:
        response = requests.get(DATA_URL, headers=headers)
        response.raise_for_status()
        results = response.json().get("results", [])

        processed = []
        collectors = {}
        status_counts = {}
        agencies = set()
        sector_count = {}
        project_names = set()

        for row in results:
            lat = row.get("_geolocation", [None, None])[0]
            lon = row.get("_geolocation", [None, None])[1]
            project_name = row.get("Name_of_project")
            sector = normalize_sector(row.get("Activity_sector"))
            collector = row.get("Full_name_of_the_field_contact", "Unknown")
            status = row.get("Activity_implementation_status", "Unknown")
            agency = row.get("Name_of_the_activity_implementing_agency", "Unknown")

            if lat and lon:
                processed.append({
                    "lat": lat,
                    "lon": lon,
                    "project": project_name,
                    "sector": sector
                })

            # Top collectors
            key = (collector, sector)
            collectors[key] = collectors.get(key, 0) + 1

            # Status
            status_counts[status] = status_counts.get(status, 0) + 1

            # Sector counts
            sector_count[sector] = sector_count.get(sector, 0) + 1

            # Agencies
            if agency: agencies.add(agency)

            # Project list
            if project_name: project_names.add(project_name)

        # Reorganize collector data
        top_collectors = []
        for (collector, sector), count in collectors.items():
            top_collectors.append({
                "name": collector,
                "count": count,
                "sector": sector
            })

        return jsonify({
            "projects": processed,
            "top_collectors": sorted(top_collectors, key=lambda x: x["count"], reverse=True),
            "total_submissions": len(results),
            "status_counts": status_counts,
            "agencies": sorted(list(agencies)),
            "sector_count": sector_count,
            "submitted_projects": sorted(list(project_names))
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
