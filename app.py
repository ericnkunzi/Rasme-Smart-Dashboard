from flask import Flask, jsonify, render_template
import requests
import json
import os

app = Flask(__name__)

# Your KoBoToolbox API info — replace with your real values
KOBO_API_KEY = "YOUR_KOBO_API_KEY_HERE"
KOBO_FORM_ID = "YOUR_KOBO_FORM_ID_HERE"
KOBO_API_URL = f"https://kf.kobotoolbox.org/api/v2/assets/{KOBO_FORM_ID}/data/"

# Path to static fallback JSON data file (for testing)
STATIC_DATA_FILE = "data.json"

def fetch_data():
    headers = {
        "Authorization": f"Token {KOBO_API_KEY}"
    }
    try:
        response = requests.get(KOBO_API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        # You can add code here to transform the data as your dashboard needs
        return results
    except Exception as e:
        print("Error fetching KoBo data:", e)
        # Fallback: try loading static data from local file for testing
        if os.path.exists(STATIC_DATA_FILE):
            print("Loading data from local static file:", STATIC_DATA_FILE)
            with open(STATIC_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    data = fetch_data()
    
    # Example: transform raw KoBo results into dashboard format
    # This part depends on your actual data structure; here is a dummy example:

    # Dummy processed data to show dashboard structure
    dashboard_data = {
        "map_data": [
            # Replace with your processed project locations and colors
            {"lat": -1.95, "lon": 30.05, "name": "Project A", "sector": "Water", "color": "blue"},
            {"lat": -1.94, "lon": 29.99, "name": "Project B", "sector": "Energy", "color": "green"},
        ],
        "sector_counts": {
            "Water": 5,
            "Energy": 3,
            "Road": 4,
            "Agriculture": 2
        },
        "implementation_status": {
            "Completed": 6,
            "Ongoing": 5,
            "Not started": 2,
            "Delayed": 1
        },
        "collectors_table": [
            {"name": "Alice", "count": 5, "sectors": ["Water", "Energy"]},
            {"name": "Bob", "count": 4, "sectors": ["Road"]},
            {"name": "Charlie", "count": 3, "sectors": ["Agriculture", "Water"]}
        ],
        "total_submissions": 12,
        "projects": ["Project A", "Project B", "Project C"],
        "agencies": ["Agency X", "Agency Y", "Agency Z"]
    }

    # You can customize and replace dashboard_data with real processed data from KoBo here
    return jsonify(dashboard_data)

if __name__ == "__main__":
    app.run(debug=True)
