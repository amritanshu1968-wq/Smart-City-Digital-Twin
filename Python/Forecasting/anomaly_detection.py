import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import IsolationForest

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "database" / "smart_city.db"
ANOMALY_OUTPUT = BASE_DIR / "data" / "processed" / "iot_anomalies.csv"

def get_db_connection():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run the data generator first.")
    return sqlite3.connect(DB_PATH)

def detect_anomalies():
    print("=" * 60)
    print("🔍 Running Anomaly Detection on IoT Sensor Telemetry")
    print("=" * 60)
    
    conn = get_db_connection()
    
    # Load IoT sensor data
    print("Loading IoT telemetry from SQLite...")
    df_iot = pd.read_sql("""
        SELECT i.Sensor_ID, i.Timestamp, i.Zone_ID, c.Zone, i.Sensor_Type, i.Reading, i.Unit, i.Battery_Level
        FROM fact_iot i
        JOIN dim_city c ON i.Zone_ID = c.Zone_ID
    """, conn)
    conn.close()
    
    print(f"Loaded {len(df_iot):,} sensor readings.")
    
    # We must fit anomaly detection separately per Sensor Type,
    # as their scales and distributions are completely different.
    anomalous_records = []
    
    for s_type in df_iot["Sensor_Type"].unique():
        print(f"\nDetecting anomalies for sensor type: {s_type}...")
        df_sub = df_iot[df_iot["Sensor_Type"] == s_type].copy()
        
        if len(df_sub) < 10:
            print(f"Too few records for {s_type}. Skipping.")
            continue
            
        # Reshape data for Isolation Forest (Reading and Battery Level as features)
        X = df_sub[["Reading", "Battery_Level"]].fillna(method="ffill").fillna(0)
        
        # Fit Isolation Forest
        # contamination = 0.005 means we expect roughly 0.5% of readings to be anomalies (including our injected ones!)
        iso = IsolationForest(contamination=0.005, random_state=42, n_jobs=-1)
        preds = iso.fit_predict(X)
        scores = iso.decision_function(X)
        
        df_sub["Anomaly_Score"] = np.round(scores, 4)
        df_sub["Is_Anomaly"] = np.where(preds == -1, "Yes", "No")
        
        # Filter anomalies
        df_anomalies = df_sub[df_sub["Is_Anomaly"] == "Yes"]
        anomalous_records.append(df_anomalies)
        print(f" Flagged {len(df_anomalies):,} anomalies out of {len(df_sub):,} readings.")

    # Combine anomalies across all sensor types
    if anomalous_records:
        df_all_anomalies = pd.concat(anomalous_records, ignore_index=True)
        # Sort by timestamp
        df_all_anomalies = df_all_anomalies.sort_values(by="Timestamp", ascending=False)
    else:
        df_all_anomalies = pd.DataFrame()
        
    ANOMALY_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df_all_anomalies.to_csv(ANOMALY_OUTPUT, index=False)
    
    print("\n" + "=" * 60)
    print("🎉 Anomaly Detection Pipeline Completed!")
    print(f"File Path     : {ANOMALY_OUTPUT}")
    print(f"Total Anomalies Flagged: {len(df_all_anomalies):,}")
    print("=" * 60)
    if len(df_all_anomalies) > 0:
        print(df_all_anomalies.head(10))

if __name__ == "__main__":
    detect_anomalies()
