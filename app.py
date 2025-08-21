from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

app = Flask(__name__)

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    db_url = "sqlite:///locations.db"

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    full_address = db.Column(db.Text, nullable=False)
    extra_details = db.Column(db.Text)


with app.app_context():
    db.create_all()

geolocator = Nominatim(user_agent="my_location_app")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)


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

    
    address = reverse((latitude, longitude))
    full_address = address.address if address else f"{latitude}, {longitude}"

  
    new_location = Location(
        latitude=latitude,
        longitude=longitude,
        full_address=full_address,
        extra_details=extra
    )
    db.session.add(new_location)
    db.session.commit()

    print(f"Saved location: {latitude}, {longitude}, {full_address}")
    return "", 204


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
