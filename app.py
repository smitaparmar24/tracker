from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

app = Flask(__name__)

EXCEL_FILE = "locations.xlsx"

# Setup Nominatim
geolocator = Nominatim(user_agent="my_location_app")
geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)

# Create Excel if it doesn't exist
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["Latitude", "Longitude",
                      "Full Address", "Extra Details"])
    df.to_excel(EXCEL_FILE, index=False)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/location", methods=["POST"])
def location():
    data = request.get_json(force=True)
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    extra = data.get("extra", "").strip()  # from your HTML input field

    if latitude is None or longitude is None:
        return {"error": "Missing coordinates"}, 400

    print(f"Received coordinates: lat={latitude}, lon={longitude}")

    try:
        location = geocode((latitude, longitude), exactly_one=True)

        if location:
            base_address = location.address  # ✅ Always gives full formatted address
        else:
            base_address = "Address not found"
    except Exception as e:
        print("Error during geocoding:", e)
        base_address = "Address not found"

    # Merge extra details if provided
    if extra:
        full_address = f"{extra}, {base_address}"
    else:
        full_address = base_address

    # Save to Excel
    df = pd.read_excel(EXCEL_FILE)
    new_row = pd.DataFrame([[latitude, longitude, full_address, extra]],
                           columns=["Latitude", "Longitude", "Full Address", "Extra Details"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

    print(f"Saved address: {full_address}")
    return jsonify({
        "status": "success",
        "full_address": full_address
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
