import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "database" / "smart_city.db"
FORECAST_OUTPUT = BASE_DIR / "data" / "processed" / "ml_forecasts.csv"

def get_db_connection():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run the data generator first.")
    conn = sqlite3.connect(DB_PATH)
    return conn

def train_and_forecast():
    print("=" * 60)
    print("🤖 Training Machine Learning Forecasting Models")
    print("=" * 60)
    
    conn = get_db_connection()
    
    # ---------------------------------------------------------
    # 1. Load Data from SQLite
    # ---------------------------------------------------------
    print("Loading historical data from SQLite DWH...")
    df_city = pd.read_sql("SELECT Zone_ID, Zone, Population FROM dim_city", conn)
    df_weather = pd.read_sql("SELECT Date, Zone_ID, Temperature, Humidity, Rainfall, Weather FROM fact_weather", conn)
    df_traffic = pd.read_sql("SELECT Date, Zone_ID, Vehicle_Count, Average_Speed FROM fact_traffic", conn)
    df_aqi = pd.read_sql("SELECT Date, Zone_ID, AQI FROM fact_air_quality", conn)
    df_electricity = pd.read_sql("SELECT Date, Zone_ID, Consumption FROM fact_electricity", conn)
    df_water = pd.read_sql("SELECT Date, Zone_ID, Water_Consumed FROM fact_water", conn)
    
    # ---------------------------------------------------------
    # 2. Prepare Training Sets
    # ---------------------------------------------------------
    # Aggregate traffic to daily level to align with weather/other facts
    df_traffic_daily = df_traffic.groupby(["Date", "Zone_ID"]).agg({
        "Vehicle_Count": "sum",
        "Average_Speed": "mean"
    }).reset_index()
    
    # Merge datasets on Date and Zone_ID
    m1 = pd.merge(df_weather, df_traffic_daily, on=["Date", "Zone_ID"])
    m2 = pd.merge(m1, df_aqi, on=["Date", "Zone_ID"])
    m3 = pd.merge(m2, df_electricity, on=["Date", "Zone_ID"])
    df_train = pd.merge(m3, df_water, on=["Date", "Zone_ID"])
    
    # Feature Engineering
    df_train["Date"] = pd.to_datetime(df_train["Date"])
    df_train["Month"] = df_train["Date"].dt.month
    df_train["DayOfWeek"] = df_train["Date"].dt.dayofweek
    df_train["IsWeekend"] = df_train["DayOfWeek"].isin([5, 6]).astype(int)
    
    # Label encode categorical weather
    le_weather = LabelEncoder()
    df_train["Weather_Encoded"] = le_weather.fit_transform(df_train["Weather"])
    
    print(f"Prepared {len(df_train):,} daily training samples across all zones.")
    
    # ---------------------------------------------------------
    # 3. Train Models
    # ---------------------------------------------------------
    # Define features for each model
    features = ["Zone_ID", "Temperature", "Humidity", "Rainfall", "Weather_Encoded", "Month", "DayOfWeek", "IsWeekend"]
    
    X = df_train[features]
    
    models = {
        "Traffic_Volume": RandomForestRegressor(n_estimators=50, random_state=42),
        "AQI": RandomForestRegressor(n_estimators=50, random_state=42),
        "Electricity_Demand": LinearRegression(),
        "Water_Consumption": LinearRegression()
    }
    
    targets = {
        "Traffic_Volume": "Vehicle_Count",
        "AQI": "AQI",
        "Electricity_Demand": "Consumption",
        "Water_Consumption": "Water_Consumed"
    }
    
    trained_models = {}
    for name, model in models.items():
        print(f"Training {name} forecasting model...")
        target_col = targets[name]
        model.fit(X, df_train[target_col])
        trained_models[name] = model
        
    print("✅ All forecasting models trained.")
    
    # ---------------------------------------------------------
    # 4. Generate Future Forecast Scenario (January 2026)
    # ---------------------------------------------------------
    print("\nGenerating forecasting scenario (Jan 1, 2026 to Jan 30, 2026)...")
    future_dates = pd.date_range("2026-01-01", "2026-01-30")
    
    future_records = []
    # Simple seasonal simulation for future weather
    for d in future_dates:
        for _, zone_row in df_city.iterrows():
            zone_id = int(zone_row["Zone_ID"])
            
            # January is winter: cool temperatures
            temp = float(np.random.normal(15, 3))
            humidity = float(random_uniform(50, 75))
            
            # Weather probability
            weather_type = np.random.choice(["Sunny", "Cloudy", "Rain", "Fog"], p=[0.5, 0.3, 0.1, 0.1])
            rainfall = float(np.random.uniform(5, 20)) if weather_type == "Rain" else 0.0
            
            future_records.append({
                "Date": d,
                "Zone_ID": zone_id,
                "Temperature": temp,
                "Humidity": humidity,
                "Rainfall": rainfall,
                "Weather": weather_type
            })
            
    df_future = pd.DataFrame(future_records)
    df_future["Month"] = df_future["Date"].dt.month
    df_future["DayOfWeek"] = df_future["Date"].dt.dayofweek
    df_future["IsWeekend"] = df_future["DayOfWeek"].isin([5, 6]).astype(int)
    
    # Safe label encoding for future weather (handling unseen labels)
    weather_mapping = {label: idx for idx, label in enumerate(le_weather.classes_)}
    df_future["Weather_Encoded"] = df_future["Weather"].map(lambda x: weather_mapping.get(x, 0))
    
    X_future = df_future[features]
    
    # ---------------------------------------------------------
    # 5. Predict & Output
    # ---------------------------------------------------------
    output_records = []
    
    # Predict for each metric
    for name, model in trained_models.items():
        preds = model.predict(X_future)
        df_future[f"Pred_{name}"] = np.clip(preds, 0, None) # No negative values
        
    # Format output for clean visualization in Power BI (tidy/tall format)
    # We will generate a row for each Date, Zone, Metric
    for name in models.keys():
        pred_col = f"Pred_{name}"
        for _, row in df_future.iterrows():
            output_records.append({
                "Date": row["Date"].strftime("%Y-%m-%d"),
                "Zone_ID": int(row["Zone_ID"]),
                "Metric_Name": name,
                "Forecast_Value": round(float(row[pred_col]), 2),
                "Scenario": "Forecast (ML)"
            })
            
    # Include actuals for comparison
    for _, row in df_train.iterrows():
        date_str = row["Date"].strftime("%Y-%m-%d")
        zone_id = int(row["Zone_ID"])
        
        output_records.append({"Date": date_str, "Zone_ID": zone_id, "Metric_Name": "Traffic_Volume", "Forecast_Value": float(row["Vehicle_Count"]), "Scenario": "Actual"})
        output_records.append({"Date": date_str, "Zone_ID": zone_id, "Metric_Name": "AQI", "Forecast_Value": float(row["AQI"]), "Scenario": "Actual"})
        output_records.append({"Date": date_str, "Zone_ID": zone_id, "Metric_Name": "Electricity_Demand", "Forecast_Value": float(row["Consumption"]), "Scenario": "Actual"})
        output_records.append({"Date": date_str, "Zone_ID": zone_id, "Metric_Name": "Water_Consumption", "Forecast_Value": float(row["Water_Consumed"]), "Scenario": "Actual"})

    df_output = pd.DataFrame(output_records)
    FORECAST_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df_output.to_csv(FORECAST_OUTPUT, index=False)
    
    # Close connection
    conn.close()
    
    print("=" * 60)
    print("🎉 Forecasting Completed & Exported!")
    print(f"File Path     : {FORECAST_OUTPUT}")
    print(f"Total Rows    : {len(df_output):,}")
    print("=" * 60)

# Helper function
def random_uniform(low, high):
    import random
    return random.uniform(low, high)

if __name__ == "__main__":
    train_and_forecast()
