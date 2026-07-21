import pandas as pd
from pathlib import Path

# -----------------------------
# Smart City Master Data
# -----------------------------

city_data = [
    {
        "Zone_ID": 1,
        "Zone": "Hazratganj",
        "Latitude": 26.8467,
        "Longitude": 80.9462,
        "Population": 185000,
        "Area_sq_km": 8.5,
        "Hospitals": 3,
        "Police_Stations": 2,
        "Fire_Stations": 1,
        "Traffic_Signals": 18,
        "Water_Tanks": 2,
        "Electric_Substations": 2
    },
    {
        "Zone_ID": 2,
        "Zone": "Gomti Nagar",
        "Latitude": 26.8550,
        "Longitude": 81.0150,
        "Population": 420000,
        "Area_sq_km": 28.0,
        "Hospitals": 5,
        "Police_Stations": 3,
        "Fire_Stations": 2,
        "Traffic_Signals": 36,
        "Water_Tanks": 5,
        "Electric_Substations": 4
    },
    {
        "Zone_ID": 3,
        "Zone": "Indira Nagar",
        "Latitude": 26.8855,
        "Longitude": 81.0002,
        "Population": 340000,
        "Area_sq_km": 21.0,
        "Hospitals": 4,
        "Police_Stations": 2,
        "Fire_Stations": 1,
        "Traffic_Signals": 30,
        "Water_Tanks": 4,
        "Electric_Substations": 3
    },
    {
        "Zone_ID": 4,
        "Zone": "Alambagh",
        "Latitude": 26.8103,
        "Longitude": 80.9009,
        "Population": 290000,
        "Area_sq_km": 16.0,
        "Hospitals": 3,
        "Police_Stations": 2,
        "Fire_Stations": 1,
        "Traffic_Signals": 24,
        "Water_Tanks": 3,
        "Electric_Substations": 2
    },
    {
        "Zone_ID": 5,
        "Zone": "Charbagh",
        "Latitude": 26.8318,
        "Longitude": 80.9221,
        "Population": 210000,
        "Area_sq_km": 10.0,
        "Hospitals": 2,
        "Police_Stations": 2,
        "Fire_Stations": 1,
        "Traffic_Signals": 20,
        "Water_Tanks": 2,
        "Electric_Substations": 2
    },
    {
        "Zone_ID": 6,
        "Zone": "Mahanagar",
        "Latitude": 26.8758,
        "Longitude": 80.9606,
        "Population": 240000,
        "Area_sq_km": 14.0,
        "Hospitals": 3,
        "Police_Stations": 2,
        "Fire_Stations": 1,
        "Traffic_Signals": 22,
        "Water_Tanks": 3,
        "Electric_Substations": 2
    },
    {
        "Zone_ID": 7,
        "Zone": "Aliganj",
        "Latitude": 26.9005,
        "Longitude": 80.9458,
        "Population": 275000,
        "Area_sq_km": 18.5,
        "Hospitals": 3,
        "Police_Stations": 2,
        "Fire_Stations": 1,
        "Traffic_Signals": 26,
        "Water_Tanks": 3,
        "Electric_Substations": 3
    },
    {
        "Zone_ID": 8,
        "Zone": "Chinhat",
        "Latitude": 26.8751,
        "Longitude": 81.0503,
        "Population": 180000,
        "Area_sq_km": 20.0,
        "Hospitals": 2,
        "Police_Stations": 1,
        "Fire_Stations": 1,
        "Traffic_Signals": 16,
        "Water_Tanks": 2,
        "Electric_Substations": 2
    },
    {
        "Zone_ID": 9,
        "Zone": "Aminabad",
        "Latitude": 26.8474,
        "Longitude": 80.9242,
        "Population": 195000,
        "Area_sq_km": 9.0,
        "Hospitals": 2,
        "Police_Stations": 2,
        "Fire_Stations": 1,
        "Traffic_Signals": 19,
        "Water_Tanks": 2,
        "Electric_Substations": 2
    },
    {
        "Zone_ID": 10,
        "Zone": "Transport Nagar",
        "Latitude": 26.7758,
        "Longitude": 80.8923,
        "Population": 145000,
        "Area_sq_km": 24.0,
        "Hospitals": 1,
        "Police_Stations": 1,
        "Fire_Stations": 1,
        "Traffic_Signals": 14,
        "Water_Tanks": 2,
        "Electric_Substations": 2
    }
]

df = pd.DataFrame(city_data)

BASE_DIR = Path(__file__).resolve().parents[2]
output_dir = BASE_DIR / "data" / "raw"
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "city_master.csv"

df.to_csv(output_file, index=False)

print("=" * 60)
print("✅ City Master Dataset Generated")
print(output_file)
print("=" * 60)

print(df)