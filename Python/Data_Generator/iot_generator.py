import pandas as pd
import numpy as np
import random
from pathlib import Path
from datetime import datetime, timedelta

# ---------------------------------------------------
# Configurations & Paths
# ---------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

# Toggle DEVELOPMENT_MODE to generate a smaller dataset for testing (e.g. 30 days)
# Set to False to generate the full enterprise-grade 876,000 rows (365 days)
DEVELOPMENT_MODE = False

if DEVELOPMENT_MODE:
    DAYS = 30
    print("⚠️ Running in DEVELOPMENT MODE: Generating 30 days of IoT data.")
else:
    DAYS = 365
    print("🚀 Running in PRODUCTION MODE: Generating full 365 days (876,000 rows) of IoT data.")

# Load City Master and Weather Data for physical consistency
city_master = pd.read_csv(BASE_DIR / "data" / "raw" / "city_master.csv")
weather_data = pd.read_csv(BASE_DIR / "data" / "raw" / "weather_data.csv")

# Set up lookup to align sensor readings with weather
weather_lookup = weather_data.set_index(["Date", "Zone_ID"])

# Define the 10 Sensors per Zone layout (10 zones * 10 sensors = 100 sensors total)
# 100 sensors * 24 hours * 365 days = 876,000 rows
sensor_layout = [
    {"type": "Temperature", "unit": "°C", "count": 2},
    {"type": "Humidity", "unit": "%", "count": 2},
    {"type": "Noise", "unit": "dB", "count": 2},
    {"type": "AQI", "unit": "AQI", "count": 1},
    {"type": "Water Level", "unit": "%", "count": 2},
    {"type": "Power Usage", "unit": "kWh", "count": 1}
]

# Generate Sensor Master List
sensors = []
sensor_id_counter = 1
for _, zone_row in city_master.iterrows():
    zone_id = int(zone_row["Zone_ID"])
    for item in sensor_layout:
        for c in range(1, item["count"] + 1):
            sensors.append({
                "Sensor_ID": f"S-{zone_id:02d}-{item['type'][:3].upper()}-{c:02d}",
                "Zone_ID": zone_id,
                "Sensor_Type": item["type"],
                "Unit": item["unit"]
            })
            sensor_id_counter += 1

print(f"Total sensors deployed across 10 zones: {len(sensors)}")

# ---------------------------------------------------
# Generate IoT Telemetry
# ---------------------------------------------------
start_date = datetime(2025, 1, 1)
records = []

for day_idx in range(DAYS):
    current_day = start_date + timedelta(days=day_idx)
    date_str = current_day.strftime("%Y-%m-%d")
    
    if day_idx % 30 == 0 and day_idx > 0:
        print(f" Progress: Generated data up to day {day_idx}/{DAYS}...")
        
    for hour in range(24):
        timestamp = current_day.replace(hour=hour, minute=0, second=0)
        
        for s in sensors:
            zone_id = s["Zone_ID"]
            sensor_type = s["Sensor_Type"]
            
            # Fetch weather parameters for realistic readings
            try:
                w_row = weather_lookup.loc[(date_str, zone_id)]
                temp = float(w_row["Temperature"])
                humidity = float(w_row["Humidity"])
                rainfall = float(w_row["Rainfall_mm"])
            except KeyError:
                # Default fallbacks if weather not loaded
                temp = 25.0
                humidity = 60.0
                rainfall = 0.0
            
            # Simulate readings depending on physics/weather
            if sensor_type == "Temperature":
                reading = round(temp + np.random.normal(0, 1.2) + (1.5 if 12 <= hour <= 16 else -1.5), 1)
                reading = max(-5.0, min(50.0, reading))
            elif sensor_type == "Humidity":
                reading = round(humidity + np.random.normal(0, 2.5), 1)
                reading = max(0.0, min(100.0, reading))
            elif sensor_type == "Noise":
                # Higher noise during day and peak hours
                base_noise = 65.0 if (7 <= hour <= 21) else 45.0
                if hour in [8, 9, 17, 18, 19]: # Traffic peak
                    base_noise += 15.0
                reading = round(base_noise + random.uniform(-5.0, 8.0), 1)
                reading = max(20.0, min(120.0, reading))
            elif sensor_type == "AQI":
                # Simulated hourly local AQI
                reading = int(max(20, min(500, np.random.normal(100, 25) + (15 if 8 <= hour <= 20 else -10))))
            elif sensor_type == "Water Level":
                # Water tank/reservoir level variations
                reading = round(random.uniform(40, 95) - (5 * np.sin(hour * np.pi / 12)), 1)
                reading = max(0.0, min(100.0, reading))
            elif sensor_type == "Power Usage":
                # Grid load fluctuations
                base_power = 600.0
                if 18 <= hour <= 22: # Evening peak
                    base_power *= 1.4
                elif 0 <= hour <= 5: # Night low
                    base_power *= 0.6
                reading = round(base_power + random.uniform(-100.0, 150.0), 1)
                reading = max(50.0, reading)
                
            # Simulate Battery Level (draining slowly, with random charging/replacements)
            # Battery decays slowly across the year
            day_decay = (day_idx % 120) * 0.5  # Replaces batteries every ~120 days
            battery = int(max(5, min(100, 100 - day_decay + random.randint(-5, 5))))
            
            # Status based on battery and readings
            status = "Normal"
            if battery < 25:
                status = "Critical"
            elif battery < 50:
                status = "Warning"
            
            # Let's add anomaly injection for our Anomaly Detection model!
            # 0.2% chance of injecting a sensor error/anomaly
            if random.random() < 0.002:
                status = "Critical"
                if sensor_type == "Temperature":
                    reading = round(reading + random.choice([30.0, -30.0]), 1)  # Extreme spike/drop
                elif sensor_type == "Power Usage":
                    reading = round(reading * 5.0, 1)  # Sudden power surge
                elif sensor_type == "Water Level":
                    reading = 0.0  # Empty level sensor anomaly
            
            records.append({
                "Sensor_ID": s["Sensor_ID"],
                "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "Zone_ID": zone_id,
                "Sensor_Type": sensor_type,
                "Reading": reading,
                "Status": status,
                "Battery_Level": battery,
                "Unit": s["Unit"]
            })

# ---------------------------------------------------
# Save Output
# ---------------------------------------------------
iot_df = pd.DataFrame(records)
output_file = BASE_DIR / "data" / "raw" / "iot_sensor_data.csv"
output_file.parent.mkdir(parents=True, exist_ok=True)
iot_df.to_csv(output_file, index=False)

print("=" * 60)
print("✅ IoT Telemetry Dataset Generated Successfully!")
print(f"File Path     : {output_file}")
print(f"Total Rows    : {len(iot_df):,}")
print("=" * 60)
print(iot_df.head())
