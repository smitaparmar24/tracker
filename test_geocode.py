import requests

lat = 23.2156
lon = 72.6369
key = "YOUR_GOOGLE_MAPS_API_KEY"  # Replace with your actual API key

url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={key}"
res = requests.get(url).json()
print(res)
