from flask import Flask, request
import pandas as pd
import os

app = Flask(__name__)

EXCEL_FILE = "locations.xlsx"  


if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["Latitude", "Longitude"])
    df.to_excel(EXCEL_FILE, index=False)


@app.route("/")
def index():
    with open('index.html', 'r') as f:
        return f.read()


@app.route('/location', methods=['POST'])
def location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    df = pd.read_excel(EXCEL_FILE)

    
    new_row = pd.DataFrame([[latitude, longitude]], columns=[
                           "Latitude", "Longitude"])
    df = pd.concat([df, new_row], ignore_index=True)

    df.to_excel(EXCEL_FILE, index=False)

    print(f"Saved location: Latitude = {latitude}, Longitude = {longitude}")
    return '', 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
