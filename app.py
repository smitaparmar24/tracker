from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database connection (Render sets DATABASE_URL as env variable)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Define table for locations


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    full_address = db.Column(db.Text, nullable=False)
    extra_details = db.Column(db.Text)


# Create tables if not exist
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/location", methods=["POST"])
def location():
    data = request.get_json(force=True)
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    extra = data.get("extra", "").strip() if data.get("extra") else ""

    if latitude is None or longitude is None:
        return "", 204

    # Store location (without geopy for now, can add back later)
    new_location = Location(
        latitude=latitude,
        longitude=longitude,
        # Replace with geopy address if needed
        full_address=f"{latitude}, {longitude}",
        extra_details=extra
    )
    db.session.add(new_location)
    db.session.commit()

    print(f"Saved location: {latitude}, {longitude}")

    return "", 204


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
