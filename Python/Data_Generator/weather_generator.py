import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path

# -----------------------------
# Configuration
# -----------------------------

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)

WEATHER_TYPES = [
    "Sunny",
    "Cloudy",
    "Rain",
    "Storm",
    "Fog"
]

# -----------------------------
# Load City Master
# -----------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

city_master = pd.read_csv(
    BASE_DIR / "data" / "raw" / "city_master.csv"
)

records = []

current = START_DATE

while current <= END_DATE:

    for _, row in city_master.iterrows():

        month = current.month

        # Temperature by season
        if month in [4, 5, 6]:
            temperature = round(random.uniform(35, 45), 1)
        elif month in [7, 8, 9]:
            temperature = round(random.uniform(26, 35), 1)
        elif month in [12, 1]:
            temperature = round(random.uniform(10, 22), 1)
        else:
            temperature = round(random.uniform(20, 32), 1)

        humidity = random.randint(35, 95)

        rainfall = 0

        weather = random.choices(
            WEATHER_TYPES,
            weights=[45, 20, 25, 5, 5]
        )[0]

        if weather == "Rain":
            rainfall = round(random.uniform(5, 60), 1)

        elif weather == "Storm":
            rainfall = round(random.uniform(60, 150), 1)

        wind_speed = round(random.uniform(5, 35), 1)

        pressure = random.randint(990, 1025)

        visibility = random.randint(2, 10)

        uv_index = random.randint(1, 11)

        records.append({

            "Date": current.date(),

            "Zone_ID": row["Zone_ID"],

            "Temperature": temperature,

            "Humidity": humidity,

            "Rainfall_mm": rainfall,

            "WindSpeed_kmph": wind_speed,

            "Pressure_hPa": pressure,

            "Visibility_km": visibility,

            "UV_Index": uv_index,

            "Weather": weather

        })

    current += timedelta(days=1)

weather_df = pd.DataFrame(records)

output = BASE_DIR / "data" / "raw" / "weather_data.csv"

weather_df.to_csv(output, index=False)

print("=" * 60)
print("✅ Weather Dataset Generated")
print(output)
print(weather_df.head())
print(f"\nTotal Records : {len(weather_df):,}")