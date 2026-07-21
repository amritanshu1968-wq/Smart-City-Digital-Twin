-- =====================================================================
-- SMART CITY ANALYTICAL QUERIES
-- High-impact SQL queries for municipal operational planning and interviews.
-- =====================================================================

-- ---------------------------------------------------------------------
-- QUERY 1: Hourly Peak Congestion Analysis by Zone
-- Identifies the worst hours and intersections for traffic delays.
-- ---------------------------------------------------------------------
WITH HourlyTraffic AS (
    SELECT 
        c.Zone,
        t.Time,
        t.Intersection_ID,
        AVG(t.Vehicle_Count) as Avg_Vehicles,
        AVG(t.Average_Speed) as Avg_Speed,
        ROW_NUMBER() OVER (PARTITION BY c.Zone ORDER BY AVG(t.Vehicle_Count) DESC) as Peak_Rank
    FROM fact_traffic t
    JOIN dim_city c ON t.Zone_ID = c.Zone_ID
    GROUP BY c.Zone, t.Time, t.Intersection_ID
)
SELECT 
    Zone,
    Time as Peak_Time_Slot,
    Intersection_ID,
    ROUND(Avg_Vehicles, 1) as Avg_Vehicle_Volume,
    ROUND(Avg_Speed, 1) as Avg_Speed_kmph
FROM HourlyTraffic
WHERE Peak_Rank = 1
ORDER BY Avg_Vehicle_Volume DESC;


-- ---------------------------------------------------------------------
-- QUERY 2: Top 3 Zones with the Poorest Air Quality
-- Ranks zones by average AQI and provides the days exceeding limits.
-- ---------------------------------------------------------------------
SELECT 
    c.Zone,
    ROUND(AVG(a.AQI), 1) as Avg_AQI,
    MAX(a.AQI) as Max_AQI,
    SUM(CASE WHEN a.AQI > 150 THEN 1 ELSE 0 END) as Days_Above_Safe_AQI,
    ROUND(AVG(a.PM2_5), 2) as Avg_PM2_5,
    ROUND(AVG(a.PM10), 2) as Avg_PM10
FROM fact_air_quality a
JOIN dim_city c ON a.Zone_ID = c.Zone_ID
GROUP BY c.Zone
ORDER BY Avg_AQI DESC
LIMIT 3;


-- ---------------------------------------------------------------------
-- QUERY 3: Municipal Water Loss (Leakage) Analysis
-- Tracks water leakage rate and flags zones exceeding the 8% target.
-- ---------------------------------------------------------------------
SELECT 
    c.Zone,
    ROUND(SUM(w.Water_Produced_Liters) / 1000000.0, 2) as Total_Produced_ML,
    ROUND(SUM(w.Water_Consumed_Liters) / 1000000.0, 2) as Total_Consumed_ML,
    ROUND(SUM(w.Leakage_Liters) / 1000000.0, 2) as Total_Lost_ML,
    ROUND((SUM(w.Leakage_Liters) * 100.0 / SUM(w.Water_Produced_Liters)), 2) as Leakage_Rate_Pct,
    SUM(CASE WHEN w.Pipe_Burst = 'Yes' THEN 1 ELSE 0 END) as Total_Pipe_Bursts
FROM fact_water w
JOIN dim_city c ON w.Zone_ID = c.Zone_ID
GROUP BY c.Zone
ORDER BY Leakage_Rate_Pct DESC;


-- ---------------------------------------------------------------------
-- QUERY 4: Emergency Response Efficiency by Zone & Severity
-- Calculates avg response time and counts of critical incidents.
-- ---------------------------------------------------------------------
SELECT 
    c.Zone,
    em.Severity,
    COUNT(em.Emergency_ID) as Total_Incidents,
    ROUND(AVG(em.Response_Time_Min), 1) as Avg_Response_Time_Min,
    MAX(em.Response_Time_Min) as Max_Response_Time_Min
FROM fact_emergency em
JOIN dim_city c ON em.Zone_ID = c.Zone_ID
GROUP BY c.Zone, em.Severity
HAVING Total_Incidents > 5
ORDER BY c.Zone, 
         CASE em.Severity 
            WHEN 'Critical' THEN 1 
            WHEN 'High' THEN 2 
            WHEN 'Medium' THEN 3 
            WHEN 'Low' THEN 4 
         END;


-- ---------------------------------------------------------------------
-- QUERY 5: Solar Generation Penetration and Grid Reliance
-- Measures solar offset vs energy consumption across city zones.
-- ---------------------------------------------------------------------
SELECT 
    c.Zone,
    ROUND(SUM(e.Consumption_kWh) / 1000.0, 2) as Total_Consumption_MWh,
    ROUND(SUM(e.Solar_Generation_kWh) / 1000.0, 2) as Total_Solar_MWh,
    ROUND((SUM(e.Solar_Generation_kWh) * 100.0 / SUM(e.Consumption_kWh)), 2) as Solar_Offset_Pct,
    ROUND(AVG(e.Battery_Level_Pct), 1) as Avg_Battery_Storage_Pct,
    SUM(CASE WHEN e.Power_Outage = 'Yes' THEN 1 ELSE 0 END) as Outage_Occurrences
FROM fact_electricity e
JOIN dim_city c ON e.Zone_ID = c.Zone_ID
GROUP BY c.Zone
ORDER BY Solar_Offset_Pct DESC;


-- ---------------------------------------------------------------------
-- QUERY 6: Traffic Accident Risk and Weather Correlation
-- Evaluates accident rates under different weather conditions.
-- ---------------------------------------------------------------------
SELECT 
    t.Weather,
    COUNT(t.Traffic_ID) as Total_Traffic_Observations,
    SUM(t.Accidents) as Total_Accidents,
    ROUND(AVG(t.Average_Speed), 1) as Avg_Speed_kmph,
    ROUND((SUM(t.Accidents) * 100.0 / COUNT(t.Traffic_ID)), 4) as Accident_Rate_Pct
FROM fact_traffic t
GROUP BY t.Weather
ORDER BY Accident_Rate_Pct DESC;


-- ---------------------------------------------------------------------
-- QUERY 7: IoT Sensor Alert Summary & Battery Warning List
-- Identifies sensors with less than 20% battery or frequent critical alerts.
-- ---------------------------------------------------------------------
SELECT 
    i.Sensor_ID,
    c.Zone,
    i.Sensor_Type,
    AVG(i.Battery_Level) as Avg_Battery_Level,
    SUM(CASE WHEN i.Status = 'Critical' THEN 1 ELSE 0 END) as Critical_Alerts
FROM fact_iot i
JOIN dim_city c ON i.Zone_ID = c.Zone_ID
GROUP BY i.Sensor_ID, c.Zone, i.Sensor_Type
HAVING Avg_Battery_Level < 30 OR Critical_Alerts > 10
ORDER BY Avg_Battery_Level ASC;


-- ---------------------------------------------------------------------
-- QUERY 8: Monthly Zone Efficiency Score Card
-- Ranks zones by combining a multi-metric utility index.
-- ---------------------------------------------------------------------
WITH ZonePerformance AS (
    SELECT 
        c.Zone,
        AVG(t.Average_Speed) as Traffic_Speed,
        AVG(a.AQI) as AQI_Level,
        SUM(w.Leakage_Liters) * 100.0 / SUM(w.Water_Produced_Liters) as Water_Leakage,
        AVG(e.Solar_Generation_kWh) as Solar_kWh,
        AVG(em.Response_Time_Min) as Emergency_Response
    FROM dim_city c
    LEFT JOIN fact_traffic t ON c.Zone_ID = t.Zone_ID
    LEFT JOIN fact_air_quality a ON c.Zone_ID = a.Zone_ID AND t.Date = a.Date
    LEFT JOIN fact_water w ON c.Zone_ID = w.Zone_ID AND t.Date = w.Date
    LEFT JOIN fact_electricity e ON c.Zone_ID = e.Zone_ID AND t.Date = e.Date
    LEFT JOIN fact_emergency em ON c.Zone_ID = em.Zone_ID AND t.Date = em.Date
    GROUP BY c.Zone
)
SELECT 
    Zone,
    ROUND(Traffic_Speed, 1) as Avg_Speed_kmph,
    ROUND(AQI_Level, 1) as Avg_AQI,
    ROUND(Water_Leakage, 2) as Leakage_Pct,
    ROUND(Solar_kWh, 1) as Avg_Solar_kWh,
    ROUND(Emergency_Response, 1) as Avg_Response_Min
FROM ZonePerformance
ORDER BY Avg_AQI ASC, Leakage_Pct ASC;
