"""
data_collection.py
-------------------
Ye script 3 free APIs se data khींchta (fetch karta) hai:
1. NASA EONET      -> Natural disasters/events (wildfires, storms, floods, etc.)
2. OpenWeatherMap   -> Live weather data for a list of cities
3. OpenAQ           -> Air quality (PM2.5, PM10, etc.) data for those cities
"""

import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

CITIES = [
    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"name": "Delhi", "lat": 28.7041, "lon": 77.1025},
    {"name": "New York", "lat": 40.7128, "lon": -74.0060},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    {"name": "London", "lat": 51.5074, "lon": -0.1278},
    {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
]


def fetch_eonet_disasters(days=90):
    """NASA EONET API se pichle 'days' dino ke natural disaster/events fetch karta hai."""
    url = "https://eonet.gsfc.nasa.gov/api/v3/events"
    params = {"days": days, "status": "all"}

    print(f"[EONET] Fetching disasters from last {days} days...")
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    events = []
    for event in data.get("events", []):
        categories = ", ".join([c["title"] for c in event.get("categories", [])])
        for geom in event.get("geometry", []):
            coords = geom.get("coordinates") or [None, None]
            if not isinstance(coords, list) or len(coords) < 2:
                coords = [None, None]
            events.append({
                "event_id": event.get("id"),
                "title": event.get("title"),
                "category": categories,
                "date": geom.get("date"),
                "lon": coords[0] if isinstance(coords[0], (int, float)) else None,
                "lat": coords[1] if isinstance(coords[1], (int, float)) else None,
                "source_url": event.get("sources", [{}])[0].get("url", ""),
            })

    df = pd.DataFrame(events)
    save_path = os.path.join(RAW_DIR, "eonet_disasters_raw.csv")
    df.to_csv(save_path, index=False)
    print(f"[EONET] Saved {len(df)} rows -> {save_path}")
    return df


def fetch_weather_data():
    """OpenWeatherMap se har city ka live weather leta hai."""
    if not OPENWEATHER_API_KEY:
        print("[Weather] WARNING: OPENWEATHER_API_KEY nahi mili .env mein. Skipping.")
        return pd.DataFrame()

    url = "https://api.openweathermap.org/data/2.5/weather"
    rows = []

    print("[Weather] Fetching current weather for all cities...")
    for city in CITIES:
        params = {
            "lat": city["lat"],
            "lon": city["lon"],
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        }
        response = requests.get(url, params=params, timeout=30)
        if response.status_code != 200:
            print(f"[Weather] Failed for {city['name']}: {response.text}")
            continue
        data = response.json()

        rows.append({
            "city": city["name"],
            "lat": city["lat"],
            "lon": city["lon"],
            "temperature_c": data.get("main", {}).get("temp"),
            "feels_like_c": data.get("main", {}).get("feels_like"),
            "humidity_pct": data.get("main", {}).get("humidity"),
            "weather_condition": data.get("weather", [{}])[0].get("main"),
            "wind_speed_ms": data.get("wind", {}).get("speed"),
            "timestamp_unix": data.get("dt"),
        })
        time.sleep(1)

    df = pd.DataFrame(rows)
    save_path = os.path.join(RAW_DIR, "weather_raw.csv")
    df.to_csv(save_path, index=False)
    print(f"[Weather] Saved {len(df)} rows -> {save_path}")
    return df


def fetch_air_quality_data():
    """OpenAQ se har city ke nazdeek air quality measurements leta hai."""
    if not OPENAQ_API_KEY:
        print("[AirQuality] WARNING: OPENAQ_API_KEY nahi mili .env mein. Skipping.")
        return pd.DataFrame()

    url = "https://api.openaq.org/v3/locations"
    headers = {"X-API-Key": OPENAQ_API_KEY}
    rows = []

    print("[AirQuality] Fetching nearest air quality stations for all cities...")
    for city in CITIES:
        params = {
            "coordinates": f"{city['lat']},{city['lon']}",
            "radius": 25000,
            "limit": 1,
        }
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            print(f"[AirQuality] Failed for {city['name']}: {response.text}")
            continue
        data = response.json()

        results = data.get("results", [])
        if not results:
            print(f"[AirQuality] No station found near {city['name']}")
            continue

        station = results[0]
        for sensor in station.get("sensors", []):
            rows.append({
                "city": city["name"],
                "station_name": station.get("name"),
                "parameter": sensor.get("parameter", {}).get("name"),
                "unit": sensor.get("parameter", {}).get("units"),
                "lat": city["lat"],
                "lon": city["lon"],
            })
        time.sleep(1)

    df = pd.DataFrame(rows)
    save_path = os.path.join(RAW_DIR, "airquality_raw.csv")
    df.to_csv(save_path, index=False)
    print(f"[AirQuality] Saved {len(df)} rows -> {save_path}")
    return df


if __name__ == "__main__":
    fetch_eonet_disasters(days=90)
    fetch_weather_data()
    fetch_air_quality_data()
    print("\nData collection complete! Check data/raw/ folder.")