import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "database" / "smart_city.db"
SQL_DDL_PATH = BASE_DIR / "SQL" / "create_tables.sql"
SQL_VIEWS_PATH = BASE_DIR / "SQL" / "views.sql"
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# ---------------------------------------------------
# Helper: Generate Dimension Data Programmatically
# ---------------------------------------------------
def generate_dimensions():
    print("🛠️ Generating Dimension Data...")
    
    # 1. Date Dimension (dim_date)
    start_date = datetime(2025, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    date_records = []
    for d in dates:
        date_records.append({
            "Date": d.strftime("%Y-%m-%d"),
            "Year": d.year,
            "Quarter": (d.month - 1) // 3 + 1,
            "Month": d.month,
            "Month_Name": d.strftime("%B"),
            "Week": int(d.strftime("%V")),
            "Day": d.day,
            "Weekend": "Yes" if d.weekday() in [5, 6] else "No"
        })
    df_date = pd.DataFrame(date_records)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df_date.to_csv(PROCESSED_DATA_DIR / "dim_date.csv", index=False)
    
    # 2. Time Dimension (dim_time)
    time_records = []
    # We populate all 24 hours of the day
    for h in range(24):
        # We can support HH:00 format
        time_str = f"{h:02d}:00"
        
        # Determine DayPart
        if 5 <= h < 12:
            day_part = "Morning"
        elif 12 <= h < 17:
            day_part = "Afternoon"
        elif 17 <= h < 21:
            day_part = "Evening"
        else:
            day_part = "Night"
            
        time_records.append({
            "Time": time_str,
            "Hour": h,
            "Minute": 0,
            "DayPart": day_part
        })
    df_time = pd.DataFrame(time_records)
    df_time.to_csv(PROCESSED_DATA_DIR / "dim_time.csv", index=False)
    print("✅ Date and Time dimensions written to data/processed/")

# ---------------------------------------------------
# Database Loader Pipeline
# ---------------------------------------------------
def main():
    print("=" * 60)
    print("🗄️ Starting Smart City Database Loader")
    print("=" * 60)
    
    # Check/Generate dimensions
    generate_dimensions()
    
    # Connect to SQLite
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    
    # Step 1: Create Tables
    print("\nExecuting DDL create_tables.sql...")
    if not SQL_DDL_PATH.exists():
        raise FileNotFoundError(f"Missing create_tables.sql at {SQL_DDL_PATH}")
        
    ddl_script = SQL_DDL_PATH.read_text()
    
    # SQLite does not support executing multiple statements containing drop/creates 
    # easily in one go if there are errors, so we split by semicolon or use executescript
    cursor.executescript("""
    DROP TABLE IF EXISTS fact_iot;
    DROP TABLE IF EXISTS fact_emergency;
    DROP TABLE IF EXISTS fact_electricity;
    DROP TABLE IF EXISTS fact_water;
    DROP TABLE IF EXISTS fact_traffic;
    DROP TABLE IF EXISTS fact_air_quality;
    DROP TABLE IF EXISTS fact_weather;
    DROP TABLE IF EXISTS dim_time;
    DROP TABLE IF EXISTS dim_date;
    DROP TABLE IF EXISTS dim_city;
    """)
    cursor.executescript(ddl_script)
    print("✅ Tables and indexes created successfully.")

    # Step 2: Load Data
    files_to_load = [
        # (Table Name, File Path, Columns Map)
        (
            "dim_city", 
            RAW_DATA_DIR / "city_master.csv", 
            None
        ),
        (
            "dim_date", 
            PROCESSED_DATA_DIR / "dim_date.csv", 
            None
        ),
        (
            "dim_time", 
            PROCESSED_DATA_DIR / "dim_time.csv", 
            None
        ),
        (
            "fact_weather", 
            RAW_DATA_DIR / "weather_data.csv", 
            {
                "Date": "Date",
                "Zone_ID": "Zone_ID",
                "Temperature": "Temperature",
                "Humidity": "Humidity",
                "Rainfall_mm": "Rainfall",
                "WindSpeed_kmph": "WindSpeed",
                "Pressure_hPa": "Pressure",
                "Visibility_km": "Visibility",
                "UV_Index": "UV_Index",
                "Weather": "Weather"
            }
        ),
        (
            "fact_air_quality", 
            RAW_DATA_DIR / "air_quality_data.csv", 
            None # direct match
        ),
        (
            "fact_traffic", 
            RAW_DATA_DIR / "traffic_data.csv", 
            {
                "Traffic_ID": "Traffic_ID",
                "Date": "Date",
                "Time": "Time",
                "Zone_ID": "Zone_ID",
                "Intersection_ID": "Intersection_ID",
                "Vehicle_Count": "Vehicle_Count",
                "Average_Speed": "Average_Speed",
                "Congestion_Level": "Congestion_Level",
                "Travel_Time_Min": "Travel_Time",
                "Fuel_Wasted_Liters": "Fuel_Wasted",
                "Signal_Status": "Signal_Status",
                "Accidents": "Accidents",
                "Weather": "Weather",
                "Peak_Hour": "Peak_Hour"
            }
        ),
        (
            "fact_water", 
            RAW_DATA_DIR / "water_data.csv", 
            {
                "Date": "Date",
                "Zone_ID": "Zone_ID",
                "Water_Produced_Liters": "Water_Produced",
                "Water_Consumed_Liters": "Water_Consumed",
                "Leakage_Liters": "Leakage",
                "Tank_Level_%": "Tank_Level",
                "Reservoir_Level_%": "Reservoir_Level",
                "Water_Quality_Index": "Water_Quality_Index",
                "Pipe_Burst": "Pipe_Burst"
            }
        ),
        (
            "fact_electricity", 
            RAW_DATA_DIR / "electricity_data.csv", 
            {
                "Date": "Date",
                "Zone_ID": "Zone_ID",
                "Consumption_kWh": "Consumption",
                "Peak_Load_kWh": "Peak_Load",
                "Solar_Generation_kWh": "Solar_Generation",
                "Battery_Level_%": "Battery_Level",
                "Power_Outage": "Power_Outage",
                "Voltage": "Voltage",
                "Frequency_Hz": "Frequency"
            }
        ),
        (
            "fact_emergency", 
            RAW_DATA_DIR / "emergency_data.csv", 
            {
                "Emergency_ID": "Emergency_ID",
                "Date": "Date",
                "Time": "Time",
                "Zone_ID": "Zone_ID",
                "Intersection_ID": "Intersection_ID",
                "Incident_Type": "Incident_Type",
                "Severity": "Severity",
                "Response_Time_Min": "Response_Time",
                "Hospital": "Hospital",
                "Ambulance": "Ambulance",
                "Police": "Police",
                "Fire_Service": "Fire_Service"
            }
        ),
        (
            "fact_iot", 
            RAW_DATA_DIR / "iot_sensor_data.csv", 
            {
                "Sensor_ID": "Sensor_ID",
                "Timestamp": "Timestamp",
                "Zone_ID": "Zone_ID",
                "Sensor_Type": "Sensor_Type",
                "Reading": "Reading",
                "Status": "Status",
                "Battery_Level": "Battery_Level",
                "Unit": "Unit"
            }
        )
    ]
    
    print("\nLoading files into SQLite database tables...")
    for table_name, file_path, col_map in files_to_load:
        if not file_path.exists():
            print(f"⚠️ Warning: File {file_path} not found. Skipping {table_name}.")
            continue
            
        df = pd.read_csv(file_path)
        
        # Apply columns mapping if specified
        if col_map:
            # Only keep columns defined in map and rename them
            df = df[list(col_map.keys())].rename(columns=col_map)
            
        # Append data to the pre-created schema table
        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f" Loaded {table_name:<20} {len(df):>10,} rows from {file_path.name}")
        
    # Step 3: Create Views
    print("\nCreating analytical views...")
    if not SQL_VIEWS_PATH.exists():
        raise FileNotFoundError(f"Missing views.sql at {SQL_VIEWS_PATH}")
    
    views_script = SQL_VIEWS_PATH.read_text()
    cursor.executescript(views_script)
    print("✅ Analytical Views created successfully.")
    
    # Step 4: Verification
    print("\n" + "="*40 + "\nDATA WAREHOUSE ROW COUNT VERIFICATION\n" + "="*40)
    verification_tables = [
        "dim_city", "dim_date", "dim_time", 
        "fact_weather", "fact_air_quality", "fact_traffic", 
        "fact_water", "fact_electricity", "fact_emergency", "fact_iot"
    ]
    for tbl in verification_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
        cnt = cursor.fetchone()[0]
        print(f" Table: {tbl:<20} | Row Count: {cnt:,}")
        
    conn.commit()
    conn.close()
    print("=" * 60)
    print("🎉 Database Population Complete! smart_city.db is ready.")
    print("=" * 60)

if __name__ == "__main__":
    main()
