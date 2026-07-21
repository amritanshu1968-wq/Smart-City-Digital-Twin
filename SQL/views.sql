-- ==========================================
-- SMART CITY ANALYTICAL VIEWS
-- Pre-aggregated views for Executive Dashboards
-- ==========================================

-- 1. View: Traffic Summary
CREATE VIEW IF NOT EXISTS view_traffic_summary AS
SELECT 
    t.Date,
    t.Zone_ID,
    c.Zone,
    COUNT(t.Traffic_ID) as Total_Records,
    SUM(t.Vehicle_Count) as Total_Vehicles,
    AVG(t.Vehicle_Count) as Avg_Vehicles_Per_Slot,
    AVG(t.Average_Speed) as Avg_Speed_kmph,
    SUM(t.Accidents) as Total_Accidents,
    SUM(t.Fuel_Wasted) as Total_Fuel_Wasted_Liters,
    AVG(t.Travel_Time) as Avg_Travel_Time_Min,
    SUM(CASE WHEN t.Peak_Hour = 'Yes' THEN 1 ELSE 0 END) as Peak_Hour_Records
FROM fact_traffic t
JOIN dim_city c ON t.Zone_ID = c.Zone_ID
GROUP BY t.Date, t.Zone_ID;

-- 2. View: AQI Summary
CREATE VIEW IF NOT EXISTS view_aqi_summary AS
SELECT 
    a.Date,
    a.Zone_ID,
    c.Zone,
    a.AQI,
    a.AQI_Category,
    a.PM2_5,
    a.PM10,
    a.CO,
    a.NO2,
    a.SO2,
    a.O3
FROM fact_air_quality a
JOIN dim_city c ON a.Zone_ID = c.Zone_ID;

-- 3. View: Water Usage Summary
CREATE VIEW IF NOT EXISTS view_water_usage_summary AS
SELECT 
    w.Date,
    w.Zone_ID,
    c.Zone,
    w.Water_Produced as Produced_Liters,
    w.Water_Consumed as Consumed_Liters,
    w.Leakage as Leakage_Liters,
    (w.Leakage * 100.0 / w.Water_Produced) as Leakage_Percentage,
    w.Tank_Level as Avg_Tank_Level_Pct,
    w.Reservoir_Level as Avg_Reservoir_Level_Pct,
    w.Water_Quality_Index,
    SUM(CASE WHEN w.Pipe_Burst = 'Yes' THEN 1 ELSE 0 END) as Total_Pipe_Bursts
FROM fact_water w
JOIN dim_city c ON w.Zone_ID = c.Zone_ID
GROUP BY w.Date, w.Zone_ID;

-- 4. View: Electricity Summary
CREATE VIEW IF NOT EXISTS view_electricity_summary AS
SELECT 
    e.Date,
    e.Zone_ID,
    c.Zone,
    e.Consumption as Consumption_kWh,
    e.Peak_Load as Peak_Load_kWh,
    e.Solar_Generation as Solar_Generation_kWh,
    (e.Solar_Generation * 100.0 / e.Consumption) as Solar_Penetration_Pct,
    e.Battery_Level as Avg_Battery_Level_Pct,
    SUM(CASE WHEN e.Power_Outage = 'Yes' THEN 1 ELSE 0 END) as Total_Power_Outages,
    AVG(e.Voltage) as Avg_Voltage,
    AVG(e.Frequency) as Avg_Frequency
FROM fact_electricity e
JOIN dim_city c ON e.Zone_ID = c.Zone_ID
GROUP BY e.Date, e.Zone_ID;

-- 5. View: Emergency Dashboard
CREATE VIEW IF NOT EXISTS view_emergency_dashboard AS
SELECT 
    em.Date,
    em.Zone_ID,
    c.Zone,
    COUNT(em.Emergency_ID) as Total_Incidents,
    AVG(em.Response_Time) as Avg_Response_Time_Min,
    SUM(CASE WHEN em.Severity = 'Critical' THEN 1 ELSE 0 END) as Critical_Incidents,
    SUM(CASE WHEN em.Severity = 'High' THEN 1 ELSE 0 END) as High_Incidents,
    SUM(CASE WHEN em.Severity = 'Medium' THEN 1 ELSE 0 END) as Medium_Incidents,
    SUM(CASE WHEN em.Severity = 'Low' THEN 1 ELSE 0 END) as Low_Incidents,
    SUM(CASE WHEN em.Incident_Type = 'Road Accident' THEN 1 ELSE 0 END) as Road_Accidents,
    SUM(CASE WHEN em.Incident_Type = 'Medical Emergency' THEN 1 ELSE 0 END) as Medical_Emergencies,
    SUM(CASE WHEN em.Incident_Type = 'Fire' THEN 1 ELSE 0 END) as Fire_Incidents,
    SUM(CASE WHEN em.Incident_Type = 'Gas Leak' THEN 1 ELSE 0 END) as Gas_Leaks,
    SUM(CASE WHEN em.Incident_Type = 'Building Collapse' THEN 1 ELSE 0 END) as Building_Collapses,
    SUM(CASE WHEN em.Incident_Type = 'Electrical Fault' THEN 1 ELSE 0 END) as Electrical_Faults
FROM fact_emergency em
JOIN dim_city c ON em.Zone_ID = c.Zone_ID
GROUP BY em.Date, em.Zone_ID;

-- 6. View: IoT Dashboard
CREATE VIEW IF NOT EXISTS view_iot_dashboard AS
SELECT 
    DATE(i.Timestamp) as Date,
    i.Zone_ID,
    c.Zone,
    i.Sensor_Type,
    COUNT(DISTINCT i.Sensor_ID) as Sensor_Count,
    AVG(i.Reading) as Avg_Reading,
    SUM(CASE WHEN i.Status = 'Critical' THEN 1 ELSE 0 END) as Critical_Alert_Count,
    SUM(CASE WHEN i.Status = 'Warning' THEN 1 ELSE 0 END) as Warning_Alert_Count,
    AVG(i.Battery_Level) as Avg_Battery_Level
FROM fact_iot i
JOIN dim_city c ON i.Zone_ID = c.Zone_ID
GROUP BY DATE(i.Timestamp), i.Zone_ID, i.Sensor_Type;
