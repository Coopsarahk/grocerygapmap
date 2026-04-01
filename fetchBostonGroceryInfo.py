import requests
import pandas as pd
import time
import geopandas as gpd
from shapely.geometry import Point
from apiKeys import GOOGLE_MAPS_API_KEY

API_KEY = GOOGLE_MAPS_API_KEY

url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# Boston grid
latitudes = [42.30, 42.32, 42.34, 42.36, 42.38, 42.40]
longitudes = [-71.12, -71.10, -71.08, -71.06, -71.04, -71.02]

all_results = []

for lat in latitudes:
    for lng in longitudes:
        location = f"{lat},{lng}"

        params = {
            "location": location,
            "radius": 2000,
            "type": "grocery_or_supermarket",
            "key": API_KEY
        }

        while True:
            response = requests.get(url, params=params)
            data = response.json()

            for place in data.get("results", []):
                all_results.append({
                    "name": place.get("name"),
                    "address": place.get("vicinity"),
                    "lat": place["geometry"]["location"]["lat"],
                    "lng": place["geometry"]["location"]["lng"],
                    "rating": place.get("rating"),
                    "user_ratings_total": place.get("user_ratings_total")
                })

            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break

            time.sleep(2)
            params["pagetoken"] = next_page_token

        time.sleep(1)

# Convert to DataFrame
df = pd.DataFrame(all_results)

# Clean + dedupe
df = df.dropna(subset=["name", "lat", "lng"])
df = df.drop_duplicates(subset=["name", "lat", "lng"])

# Convert to GeoDataFrame
geometry = [Point(xy) for xy in zip(df["lng"], df["lat"])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# Save CSV (no neighborhoods now)
df.to_csv("boston_grocery_stores.csv", index=False)

print(df.head())