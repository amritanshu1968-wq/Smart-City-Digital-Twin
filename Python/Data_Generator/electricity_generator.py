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

# ----------------------------------------
# Generate Electricity Data
# ----------------------------------------

for _, row in weather.iterrows():

    zone = int(row["Zone_ID"])

    population = city.loc[zone, "Population"]

    temp = row["Temperature"]

    weather_type = row["Weather"]

    # -----------------------------
    # Base Consumption
    # -----------------------------

    base = population * 0.020

    # AC Usage
    if temp > 35:
        base *= 1.40

    elif temp > 30:
        base *= 1.20

    elif temp < 15:
        base *= 1.15

    # Weather Effect

    if weather_type == "Storm":
        base *= 1.08

    elif weather_type == "Rain":
        base *= 1.03

    consumption = round(base + random.uniform(-250, 250), 2)

    peak_load = round(consumption * random.uniform(1.10, 1.30), 2)

    if weather_type == "Sunny":

        solar = round(random.uniform(900, 2200), 2)

    else:

        solar = round(random.uniform(100, 800), 2)

    battery = round(random.uniform(40, 100), 1)

    outage = random.choices(

        ["No", "Yes"],

        weights=[97, 3]

    )[0]

    voltage = round(random.uniform(220, 240), 1)

    frequency = round(random.uniform(49.8, 50.2), 2)

    records.append({

        "Date": row["Date"],

        "Zone_ID": zone,

        "Consumption_kWh": consumption,

        "Peak_Load_kWh": peak_load,

        "Solar_Generation_kWh": solar,

        "Battery_Level_%": battery,

        "Power_Outage": outage,

        "Voltage": voltage,

        "Frequency_Hz": frequency

    })

# ----------------------------------------
# Save
# ----------------------------------------

electricity = pd.DataFrame(records)

output = BASE_DIR / "data" / "raw" / "electricity_data.csv"

electricity.to_csv(output, index=False)

print("=" * 60)
print("Electricity Dataset Generated")
print(output)
print("=" * 60)

print(electricity.head())

print(f"\nTotal Records : {len(electricity):,}")