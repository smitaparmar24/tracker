from flask import Flask, request, send_from_directory
import pandas as pd
import os

app = Flask(__name__)


EXCEL_FILE = "locations.xlsx"


if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["Latitude", "Longitude"])
    df.to_excel(EXCEL_FILE, index=False)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")




@app.route("/location", methods=["POST"])
def location():
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return {"error": "Missing latitude or longitude"}, 400

    
    df = pd.read_excel(EXCEL_FILE)

    
    new_row = pd.DataFrame([[latitude, longitude]], columns=[
                           "Latitude", "Longitude"])
    df = pd.concat([df, new_row], ignore_index=True)

    
    df.to_excel(EXCEL_FILE, index=False)

    print(f"Saved location: Latitude={latitude}, Longitude={longitude}")
    return {"status": "success"}, 200


if __name__ == "__main__":
   
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
