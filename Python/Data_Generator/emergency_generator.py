import pandas as pd
import random
from pathlib import Path

# -----------------------------------
# Project Path
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

traffic = pd.read_csv(BASE_DIR / "data" / "raw" / "traffic_data.csv")

# -----------------------------------
# Hospital Mapping
# -----------------------------------

hospital_map = {
    1: "Civil Hospital",
    2: "Medanta",
    3: "Apollo",
    4: "KGMU",
    5: "Balrampur Hospital",
    6: "Sahara Hospital",
    7: "Max Hospital",
    8: "Integral Hospital",
    9: "Lohia Hospital",
    10: "Trauma Centre"
}

incident_types = [
    "Road Accident",
    "Medical Emergency",
    "Fire",
    "Gas Leak",
    "Building Collapse",
    "Electrical Fault"
]

records = []
emergency_id = 1

for _, row in traffic.iterrows():

    probability = 0.0015

    if row["Congestion_Level"] == "Moderate":
        probability += 0.002

    elif row["Congestion_Level"] == "High":
        probability += 0.006

    elif row["Congestion_Level"] == "Severe":
        probability += 0.010

    if row["Weather"] in ["Rain", "Storm", "Fog"]:
        probability += 0.004

    if row["Accidents"] == 1:
        probability += 0.10

    if random.random() > probability:
        continue

    incident = random.choices(
        incident_types,
        weights=[45, 25, 10, 5, 5, 10]
    )[0]

    severity = random.choices(
        ["Low", "Medium", "High", "Critical"],
        weights=[40, 35, 18, 7]
    )[0]

    response_time = random.randint(4, 25)

    records.append({

        "Emergency_ID": emergency_id,

        "Date": row["Date"],

        "Time": row["Time"],

        "Zone_ID": row["Zone_ID"],

        "Intersection_ID": row["Intersection_ID"],

        "Incident_Type": incident,

        "Severity": severity,

        "Response_Time_Min": response_time,

        "Hospital": hospital_map[row["Zone_ID"]],

        "Ambulance": "Yes",

        "Police": "Yes" if incident != "Medical Emergency" else "No",

        "Fire_Service": "Yes" if incident in [
            "Fire",
            "Gas Leak",
            "Building Collapse",
            "Electrical Fault"
        ] else "No"

    })

    emergency_id += 1

emergency = pd.DataFrame(records)

output = BASE_DIR / "data" / "raw" / "emergency_data.csv"

emergency.to_csv(output, index=False)

print("=" * 60)
print("✅ Emergency Dataset Generated")
print(output)
print("=" * 60)
print(emergency.head())
print(f"\nTotal Emergencies : {len(emergency):,}")