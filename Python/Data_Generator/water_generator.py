import pandas as pd
import random
from pathlib import Path

# ----------------------------------------
# Project Path
# ----------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

city = pd.read_csv(BASE_DIR / "data" / "raw" / "city_master.csv")
weather = pd.read_csv(BASE_DIR / "data" / "raw" / "weather_data.csv")

city = city.set_index("Zone_ID")

records = []

for _, row in weather.iterrows():

    zone = int(row["Zone_ID"])

    population = city.loc[zone, "Population"]

    temperature = row["Temperature"]
    rainfall = row["Rainfall_mm"]

    # Base daily water consumption (liters)
    base_consumption = population * 135

    # Temperature increases consumption
    if temperature > 35:
        base_consumption *= 1.10
    elif temperature > 30:
        base_consumption *= 1.05

    # Rainfall reduces consumption
    if rainfall > 20:
        base_consumption *= 0.96

    consumption = round(base_consumption)

    # Water production
    production = round(consumption * random.uniform(1.02, 1.08))

    leakage = round(production * random.uniform(0.03, 0.10))

    tank_level = round(random.uniform(45, 100), 1)

    reservoir = round(random.uniform(40, 100), 1)

    quality = random.randint(85, 100)

    pipe_burst = random.choices(
        ["No", "Yes"],
        weights=[98, 2]
    )[0]

    records.append({

        "Date": row["Date"],

        "Zone_ID": zone,

        "Water_Produced_Liters": production,

        "Water_Consumed_Liters": consumption,

        "Leakage_Liters": leakage,

        "Tank_Level_%": tank_level,

        "Reservoir_Level_%": reservoir,

        "Water_Quality_Index": quality,

        "Pipe_Burst": pipe_burst

    })

water = pd.DataFrame(records)

output = BASE_DIR / "data" / "raw" / "water_data.csv"

water.to_csv(output, index=False)

print("=" * 60)
print("✅ Water Dataset Generated")
print(output)
print("=" * 60)
print(water.head())
print(f"\nTotal Records : {len(water):,}")