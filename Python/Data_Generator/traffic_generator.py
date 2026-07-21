import pandas as pd
import numpy as np
import random
from pathlib import Path

# ---------------------------------------------------
# Project Path
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

city = pd.read_csv(BASE_DIR / "data" / "raw" / "city_master.csv")
weather = pd.read_csv(BASE_DIR / "data" / "raw" / "weather_data.csv")

weather_lookup = weather.set_index(["Date", "Zone_ID"])

# ---------------------------------------------------
# Configuration
# ---------------------------------------------------

INTERSECTIONS_PER_ZONE = 10
TIME_SLOTS = [
    "06:00", "08:00", "10:00", "12:00",
    "14:00", "16:00", "18:00", "20:00",
    "22:00", "00:00"
]

records = []
traffic_id = 1

# ---------------------------------------------------
# Generate Traffic Data
# ---------------------------------------------------

for _, w in weather.iterrows():

    date = w["Date"]
    zone = int(w["Zone_ID"])
    weather_type = w["Weather"]
    rainfall = w["Rainfall_mm"]

    population = city.loc[
        city["Zone_ID"] == zone,
        "Population"
    ].iloc[0]

    for intersection in range(1, INTERSECTIONS_PER_ZONE + 1):

        intersection_id = f"Z{zone:02d}-I{intersection:02d}"

        for time in TIME_SLOTS:

            hour = int(time.split(":")[0])

            # -------------------------
            # Peak Hour
            # -------------------------

            peak = hour in [8, 18]

            base = population / 900

            if peak:
                base *= 2.2

            if weather_type == "Rain":
                base *= 1.10

            elif weather_type == "Storm":
                base *= 1.20

            vehicle_count = int(
                np.random.normal(base, base * 0.18)
            )

            vehicle_count = max(40, vehicle_count)

            speed = random.uniform(30, 60)

            if vehicle_count > 700:
                speed -= random.uniform(15, 22)

            elif vehicle_count > 500:
                speed -= random.uniform(8, 15)

            if rainfall > 20:
                speed -= random.uniform(4, 8)

            if weather_type == "Fog":
                speed -= random.uniform(8, 15)

            speed = round(max(5, speed), 1)

            # -------------------------
            # Congestion
            # -------------------------

            if speed < 15:
                congestion = "Severe"

            elif speed < 25:
                congestion = "High"

            elif speed < 40:
                congestion = "Moderate"

            else:
                congestion = "Low"

            # -------------------------
            # Accident Probability
            # -------------------------

            accident_probability = 0.003

            if congestion == "High":
                accident_probability += 0.01

            if congestion == "Severe":
                accident_probability += 0.02

            if weather_type in ["Rain", "Storm", "Fog"]:
                accident_probability += 0.01

            accidents = (
                1 if random.random() < accident_probability else 0
            )

            signal = random.choice(
                ["Green", "Yellow", "Red"]
            )

            travel_time = round(
                random.uniform(5, 20) * (60 / speed),
                1
            )

            fuel_wasted = round(
                vehicle_count *
                max(0, (35 - speed)) *
                0.0015,
                2
            )

            records.append({

                "Traffic_ID": traffic_id,

                "Date": date,

                "Time": time,

                "Zone_ID": zone,

                "Intersection_ID": intersection_id,

                "Vehicle_Count": vehicle_count,

                "Average_Speed": speed,

                "Congestion_Level": congestion,

                "Accidents": accidents,

                "Signal_Status": signal,

                "Travel_Time_Min": travel_time,

                "Fuel_Wasted_Liters": fuel_wasted,

                "Peak_Hour": "Yes" if peak else "No",

                "Weather": weather_type

            })

            traffic_id += 1

# ---------------------------------------------------
# Save
# ---------------------------------------------------

traffic = pd.DataFrame(records)

output = BASE_DIR / "data" / "raw" / "traffic_data.csv"

traffic.to_csv(output, index=False)

print("=" * 60)
print("✅ Enterprise Traffic Dataset Generated")
print(output)
print("=" * 60)

print(traffic.head())

print(f"\nTotal Records : {len(traffic):,}")