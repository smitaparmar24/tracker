from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

app = Flask(__name__)

EXCEL_FILE = "locations.xlsx"

# Setup Nominatim
geolocator = Nominatim(user_agent="my_location_app")
# Add rate limiter to avoid overloading free service
geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)

# Create Excel if it doesn't exist
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["Detailed Address"])
    df.to_excel(EXCEL_FILE, index=False)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/location", methods=["POST"])
def location():
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return {"error": "Missing coordinates"}, 400

    print(f"Received coordinates: lat={latitude}, lon={longitude}")

    # Reverse geocoding
    try:
        location = geocode((latitude, longitude), exactly_one=True)
        if location:
            raw_address = location.raw.get("address", {})

            # Extract as many details as available
            building = raw_address.get("building", "")
            house_number = raw_address.get("house_number", "")
            block = raw_address.get("block", "")
            road = raw_address.get("road", "")
            neighbourhood = raw_address.get("neighbourhood", "")
            suburb = raw_address.get("suburb", "")
            city = raw_address.get("city", raw_address.get(
                "town", raw_address.get("village", "")))
            state = raw_address.get("state", "")
            postcode = raw_address.get("postcode", "")
            country = raw_address.get("country", "")

            # Build detailed address string
            detailed_address = ", ".join(
                filter(None, [building, block, house_number, road,
                       neighbourhood, suburb, city, state, postcode, country])
            )

            # If no building/house info found, fallback to full address
            if not detailed_address:
                detailed_address = location.address
        else:
            detailed_address = "Address not found"
    except Exception as e:
        print("Error during geocoding:", e)
        detailed_address = "Address not found"

    # Save to Excel
    df = pd.read_excel(EXCEL_FILE)
    new_row = pd.DataFrame([[detailed_address]], columns=["Detailed Address"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

    print(f"Saved address: {detailed_address}")
    return jsonify({"status": "success", "detailed_address": detailed_address})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
