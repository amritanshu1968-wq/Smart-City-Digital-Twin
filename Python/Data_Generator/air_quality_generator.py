import pandas as pd
import random
from pathlib import Path

# --------------------------------------------------
# Project Path
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

# --------------------------------------------------
# Load Datasets
# --------------------------------------------------

city = pd.read_csv(BASE_DIR / "data" / "raw" / "city_master.csv")
weather = pd.read_csv(BASE_DIR / "data" / "raw" / "weather_data.csv")

# --------------------------------------------------
# Zone Pollution Baseline
# --------------------------------------------------

zone_baseline = {
    1: 105,   # Hazratganj
    2: 98,    # Gomti Nagar
    3: 90,
    4: 112,
    5: 115,
    6: 95,
    7: 88,
    8: 70,
    9: 118,
    10: 82
}

records = []

# --------------------------------------------------
# Generate AQI
# --------------------------------------------------

for _, row in weather.iterrows():

    zone = int(row["Zone_ID"])

    base = zone_baseline[zone]

    temp = row["Temperature"]
    humidity = row["Humidity"]
    rainfall = row["Rainfall_mm"]
    wind = row["WindSpeed_kmph"]
    weather_type = row["Weather"]

    # Temperature Effect
    temp_effect = (temp - 25) * 1.2

    # Wind clears pollution
    wind_effect = -(wind * 0.8)

    # Rain cleans air
    rain_effect = -(rainfall * 0.9)

    # Weather Condition
    weather_effect = 0

    if weather_type == "Sunny":
        weather_effect = 8

    elif weather_type == "Cloudy":
        weather_effect = 3

    elif weather_type == "Rain":
        weather_effect = -20

    elif weather_type == "Storm":
        weather_effect = -30

    elif weather_type == "Fog":
        weather_effect = 18

    noise = random.randint(-8, 8)

    aqi = base + temp_effect + wind_effect + rain_effect + weather_effect + noise

    aqi = max(20, min(500, round(aqi)))

    # Pollutants
    pm25 = round(aqi * random.uniform(0.38, 0.55), 1)
    pm10 = round(aqi * random.uniform(0.65, 0.95), 1)
    co = round(random.uniform(0.3, 2.5), 2)
    no2 = round(random.uniform(15, 90), 1)
    so2 = round(random.uniform(5, 45), 1)
    o3 = round(random.uniform(20, 110), 1)

    # AQI Category
    if aqi <= 50:
        category = "Good"
    elif aqi <= 100:
        category = "Satisfactory"
    elif aqi <= 200:
        category = "Moderate"
    elif aqi <= 300:
        category = "Poor"
    elif aqi <= 400:
        category = "Very Poor"
    else:
        category = "Severe"

    records.append({

        "Date": row["Date"],

        "Zone_ID": zone,

        "AQI": aqi,

        "AQI_Category": category,

        "PM2_5": pm25,

        "PM10": pm10,

        "CO": co,

        "NO2": no2,

        "SO2": so2,

        "O3": o3

    })

# --------------------------------------------------
# Save
# --------------------------------------------------

air_df = pd.DataFrame(records)

output = BASE_DIR / "data" / "raw" / "air_quality_data.csv"

air_df.to_csv(output, index=False)

print("=" * 60)
print("✅ Air Quality Dataset Generated")
print(output)
print("=" * 60)
print(air_df.head())
print(f"\nTotal Records : {len(air_df):,}")