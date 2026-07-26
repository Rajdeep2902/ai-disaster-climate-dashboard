"""
data_cleaning.py
-----------------
Ye script "data/raw/" folder ki teeno CSV files (disasters, weather, air quality)
ko padhta hai, unhe clean karta hai (missing values, duplicate rows, date formats
fix karke), aur final Tableau-ready dataset "data/processed/" mein save karta hai.
"""

import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)


def clean_disasters():
    """NASA EONET disaster data ko clean karta hai."""
    path = os.path.join(RAW_DIR, "eonet_disasters_raw.csv")
    empty_result = pd.DataFrame(columns=["lat", "lon", "event_date", "disaster_title", "primary_category"])

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        print("[Disasters] WARNING: eonet_disasters_raw.csv mein koi data nahi mila, skipping.")
        return empty_result

    if df.empty:
        print("[Disasters] WARNING: No disaster rows found, skipping.")
        return empty_result

    df = df.drop_duplicates()
    df = df.dropna(subset=["lat", "lon"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["primary_category"] = df["category"].apply(lambda x: str(x).split(",")[0].strip())
    df = df.rename(columns={"title": "disaster_title", "date": "event_date"})
    df["data_type"] = "disaster"
    return df


def clean_weather():
    """OpenWeatherMap weather data ko clean karta hai."""
    path = os.path.join(RAW_DIR, "weather_raw.csv")
    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_csv(path)
    df = df.drop_duplicates()
    df["event_date"] = pd.to_datetime(df["timestamp_unix"], unit="s", errors="coerce")

    numeric_cols = ["temperature_c", "feels_like_c", "humidity_pct", "wind_speed_ms"]
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean(numeric_only=True))

    df["data_type"] = "weather"
    return df


def clean_air_quality():
    """OpenAQ air quality data ko clean karta hai."""
    path = os.path.join(RAW_DIR, "airquality_raw.csv")
    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_csv(path)
    df = df.drop_duplicates()
    df = df.dropna(subset=["parameter", "unit"])
    df["data_type"] = "air_quality"
    return df


def merge_and_export():
    """Teeno cleaned datasets ko ek common structure mein laake merge karta hai."""
    disasters = clean_disasters()
    weather = clean_weather()
    air_quality = clean_air_quality()

    disasters.to_csv(os.path.join(PROCESSED_DIR, "disasters_clean.csv"), index=False)
    weather.to_csv(os.path.join(PROCESSED_DIR, "weather_clean.csv"), index=False)
    air_quality.to_csv(os.path.join(PROCESSED_DIR, "air_quality_clean.csv"), index=False)

    print(f"disasters_clean.csv     -> {len(disasters)} rows")
    print(f"weather_clean.csv       -> {len(weather)} rows")
    print(f"air_quality_clean.csv   -> {len(air_quality)} rows")

    common_rows = []

    for _, row in disasters.iterrows():
        common_rows.append({
            "data_type": "disaster",
            "lat": row["lat"], "lon": row["lon"],
            "event_date": row["event_date"],
            "details": f"{row['disaster_title']} ({row['primary_category']})",
        })

    for _, row in weather.iterrows():
        common_rows.append({
            "data_type": "weather",
            "lat": row["lat"], "lon": row["lon"],
            "event_date": row["event_date"],
            "details": f"{row['city']}: {row['temperature_c']}C, {row['weather_condition']}",
        })

    for _, row in air_quality.iterrows():
        common_rows.append({
            "data_type": "air_quality",
            "lat": row["lat"], "lon": row["lon"],
            "event_date": pd.NaT,
            "details": f"{row['city']}: {row['parameter']} ({row['unit']})",
        })

    master_df = pd.DataFrame(common_rows)
    master_path = os.path.join(PROCESSED_DIR, "master_dataset.csv")
    master_df.to_csv(master_path, index=False)
    print(f"master_dataset.csv      -> {len(master_df)} rows -> {master_path}")


if __name__ == "__main__":
    merge_and_export()
    print("\nCleaning complete! Ab 'data/processed/' folder Tableau Public mein import karo.")