-- ==========================================
-- SMART CITY DIGITAL TWIN DATA WAREHOUSE DDL
-- Star Schema Definition (SQLite Compatible)
-- ==========================================

-- Enable Foreign Key constraints in SQLite (must be run per session)
PRAGMA foreign_keys = ON;

-- ------------------------------------------
-- 1. DIMENSION TABLES
-- ------------------------------------------

-- Dimension: City Zones
CREATE TABLE dim_city (
    Zone_ID INTEGER PRIMARY KEY,
    Zone TEXT NOT NULL,
    Latitude REAL NOT NULL,
    Longitude REAL NOT NULL,
    Population INTEGER NOT NULL,
    Area_sq_km REAL NOT NULL,
    Hospitals INTEGER NOT NULL,
    Police_Stations INTEGER NOT NULL,
    Fire_Stations INTEGER NOT NULL,
    Traffic_Signals INTEGER NOT NULL,
    Water_Tanks INTEGER NOT NULL,
    Electric_Substations INTEGER NOT NULL
);

-- Dimension: Date
CREATE TABLE dim_date (
    Date TEXT PRIMARY KEY, -- Format: YYYY-MM-DD
    Year INTEGER NOT NULL,
    Quarter INTEGER NOT NULL,
    Month INTEGER NOT NULL,
    Month_Name TEXT NOT NULL,
    Week INTEGER NOT NULL,
    Day INTEGER NOT NULL,
    Weekend TEXT NOT NULL -- 'Yes' or 'No'
);

-- Dimension: Time
CREATE TABLE dim_time (
    Time TEXT PRIMARY KEY, -- Format: HH:MM
    Hour INTEGER NOT NULL,
    Minute INTEGER NOT NULL,
    DayPart TEXT NOT NULL -- e.g., 'Morning', 'Afternoon', 'Evening', 'Night'
);


-- ------------------------------------------
-- 2. FACT TABLES
-- ------------------------------------------

-- Fact: Weather (Hourly/Daily)
CREATE TABLE fact_weather (
    Date TEXT NOT NULL,
    Zone_ID INTEGER NOT NULL,
    Temperature REAL,
    Humidity REAL,
    Rainfall REAL,
    WindSpeed REAL,
    Pressure REAL,
    Visibility REAL,
    UV_Index INTEGER,
    Weather TEXT,
    PRIMARY KEY (Date, Zone_ID),
    FOREIGN KEY (Date) REFERENCES dim_date(Date),
    FOREIGN KEY (Zone_ID) REFERENCES dim_city(Zone_ID)
);

-- Fact: Air Quality
CREATE TABLE fact_air_quality (
    Date TEXT NOT NULL,
    Zone_ID INTEGER NOT NULL,
    AQI INTEGER,
    PM2_5 REAL,
    PM10 REAL,
    CO REAL,
    NO2 REAL,
    SO2 REAL,
    O3 REAL,
    AQI_Category TEXT,
    PRIMARY KEY (Date, Zone_ID),
    FOREIGN KEY (Date) REFERENCES dim_date(Date),
    FOREIGN KEY (Zone_ID) REFERENCES dim_city(Zone_ID)
);

-- Fact: Traffic
CREATE TABLE fact_traffic (
    Traffic_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Date TEXT NOT NULL,
    Time TEXT NOT NULL,
    Zone_ID INTEGER NOT NULL,
    Intersection_ID TEXT NOT NULL,
    Vehicle_Count INTEGER,
    Average_Speed REAL,
    Congestion_Level TEXT,
    Travel_Time REAL, -- mapped from Travel_Time_Min
    Fuel_Wasted REAL, -- mapped from Fuel_Wasted_Liters
    Signal_Status TEXT,
    Accidents INTEGER, -- 0 or 1
    Weather TEXT,
    Peak_Hour TEXT,
    FOREIGN KEY (Date) REFERENCES dim_date(Date),
    FOREIGN KEY (Time) REFERENCES dim_time(Time),
    FOREIGN KEY (Zone_ID) REFERENCES dim_city(Zone_ID)
);

-- Fact: Water
CREATE TABLE fact_water (
    Date TEXT NOT NULL,
    Zone_ID INTEGER NOT NULL,
    Water_Produced REAL,
    Water_Consumed REAL,
    Leakage REAL,
    Tank_Level REAL,
    Reservoir_Level REAL,
    Water_Quality_Index INTEGER,
    Pipe_Burst TEXT, -- 'Yes' or 'No'
    PRIMARY KEY (Date, Zone_ID),
    FOREIGN KEY (Date) REFERENCES dim_date(Date),
    FOREIGN KEY (Zone_ID) REFERENCES dim_city(Zone_ID)
);

-- Fact: Electricity
CREATE TABLE fact_electricity (
    Date TEXT NOT NULL,
    Zone_ID INTEGER NOT NULL,
    Consumption REAL,
    Peak_Load REAL,
    Solar_Generation REAL,
    Battery_Level REAL,
    Power_Outage TEXT, -- 'Yes' or 'No'
    Voltage REAL,
    Frequency REAL,
    PRIMARY KEY (Date, Zone_ID),
    FOREIGN KEY (Date) REFERENCES dim_date(Date),
    FOREIGN KEY (Zone_ID) REFERENCES dim_city(Zone_ID)
);

-- Fact: Emergency
CREATE TABLE fact_emergency (
    Emergency_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Date TEXT NOT NULL,
    Time TEXT NOT NULL,
    Zone_ID INTEGER NOT NULL,
    Intersection_ID TEXT NOT NULL,
    Incident_Type TEXT NOT NULL,
    Severity TEXT NOT NULL,
    Hospital TEXT,
    Police TEXT,
    Fire_Service TEXT,
    Response_Time REAL, -- mapped from Response_Time_Min
    Ambulance TEXT,
    FOREIGN KEY (Date) REFERENCES dim_date(Date),
    FOREIGN KEY (Time) REFERENCES dim_time(Time),
    FOREIGN KEY (Zone_ID) REFERENCES dim_city(Zone_ID)
);

-- Fact: IoT
CREATE TABLE fact_iot (
    Sensor_ID TEXT NOT NULL,
    Timestamp TEXT NOT NULL, -- Format: YYYY-MM-DD HH:MM:SS
    Zone_ID INTEGER NOT NULL,
    Sensor_Type TEXT NOT NULL,
    Reading REAL,
    Status TEXT,
    Battery_Level REAL,
    Unit TEXT,
    PRIMARY KEY (Sensor_ID, Timestamp),
    FOREIGN KEY (Zone_ID) REFERENCES dim_city(Zone_ID)
);


-- ------------------------------------------
-- 3. INDEXES FOR PERFORMANCE OPTIMIZATION
-- ------------------------------------------
CREATE INDEX idx_traffic_date_zone ON fact_traffic (Date, Zone_ID);
CREATE INDEX idx_traffic_time ON fact_traffic (Time);
CREATE INDEX idx_iot_timestamp_zone ON fact_iot (Timestamp, Zone_ID);
CREATE INDEX idx_iot_sensor_id ON fact_iot (Sensor_ID);
CREATE INDEX idx_emergency_date_zone ON fact_emergency (Date, Zone_ID);
CREATE INDEX idx_weather_date_zone ON fact_weather (Date, Zone_ID);
CREATE INDEX idx_aqi_date_zone ON fact_air_quality (Date, Zone_ID);
