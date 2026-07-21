# Smart City Digital Twin - Data Dictionary

This document details the schema of the **Smart City Digital Twin Analytics Platform** data warehouse. The warehouse uses a **Star Schema** to optimize query performance in analytical environments like Power BI and SQL reporting tools.

---

## 1. Dimension Tables

### `dim_city` (Zone Master)
Contains static and geographical properties of the municipal zones.

| Column | Data Type | Key | Description |
| :--- | :--- | :---: | :--- |
| **Zone_ID** | INTEGER | PK | Unique identifier for each municipal zone. |
| **Zone** | VARCHAR | | Name of the city zone (e.g., Hazratganj, Gomti Nagar). |
| **Latitude** | DOUBLE | | GPS Latitude coordinate of the zone center. |
| **Longitude** | DOUBLE | | GPS Longitude coordinate of the zone center. |
| **Population** | INTEGER | | Total resident population of the zone. |
| **Area_sq_km** | DOUBLE | | Total geographic area of the zone in square kilometers. |
| **Hospitals** | INTEGER | | Count of public and private hospitals in the zone. |
| **Police_Stations** | INTEGER | | Count of active police stations/outposts in the zone. |
| **Fire_Stations** | INTEGER | | Count of municipal fire stations. |
| **Traffic_Signals** | INTEGER | | Number of smart traffic intersections. |
| **Water_Tanks** | INTEGER | | Count of local water distribution tanks. |
| **Electric_Substations**| INTEGER | | Count of power distribution grid substations. |

### `dim_date` (Time Intelligence)
Enables date-based slicing and advanced Time Intelligence calculations (YTD, YoY).

| Column | Data Type | Key | Description |
| :--- | :--- | :---: | :--- |
| **Date** | VARCHAR | PK | Date primary key formatted as `YYYY-MM-DD`. |
| **Year** | INTEGER | | Calendar Year (e.g., 2025). |
| **Quarter** | INTEGER | | Calendar Quarter (1 to 4). |
| **Month** | INTEGER | | Calendar Month number (1 to 12). |
| **Month_Name** | VARCHAR | | Name of the month (e.g., January, February). |
| **Week** | INTEGER | | ISO week number of the year (1 to 53). |
| **Day** | INTEGER | | Calendar day of the month (1 to 31). |
| **Weekend** | VARCHAR | | Flag indicating weekend status ('Yes' or 'No'). |

### `dim_time` (Intraday Clocks)
Enables diurnal and peak-hour slice analyses.

| Column | Data Type | Key | Description |
| :--- | :--- | :---: | :--- |
| **Time** | VARCHAR | PK | Hourly clock index formatted as `HH:MM` (e.g. `08:00`). |
| **Hour** | INTEGER | | Clock hour of day (0 to 23). |
| **Minute** | INTEGER | | Clock minute (default is 0 for hourly data). |
| **DayPart** | VARCHAR | | Segment of day ('Morning', 'Afternoon', 'Evening', 'Night'). |

---

## 2. Fact Tables

### `fact_weather`
Captures daily environmental observations. (3,650 rows)

| Column | Data Type | Key | Description |
| :--- | :--- | :---: | :--- |
| **Date** | VARCHAR | FK | Links to `dim_date`. |
| **Zone_ID** | INTEGER | FK | Links to `dim_city`. |
| **Temperature** | REAL | | Ambient temperature in degrees Celsius (°C). |
| **Humidity** | REAL | | Air humidity percentage (%). |
| **Rainfall** | REAL | | Daily accumulated precipitation in millimeters (mm). |
| **WindSpeed** | REAL | | Average wind speed in kilometers per hour (km/h). |
| **Pressure** | REAL | | Barometric pressure in hectopascals (hPa). |
| **Visibility** | REAL | | Visibility range in kilometers (km). |
| **UV_Index** | INTEGER | | Ultraviolet index level (1 to 11+). |
| **Weather** | VARCHAR | | Primary weather condition ('Sunny', 'Cloudy', 'Rain', 'Storm', 'Fog'). |

### `fact_air_quality`
Hourly/Daily environmental pollution metrics. (3,650 rows)

| Column | Data Type | Key | Description |
| :--- | :--- | :---: | :--- |
| **Date** | VARCHAR | FK | Links to `dim_date`. |
| **Zone_ID** | INTEGER | FK | Links to `dim_city`. |
| **AQI** | INTEGER | | Composite Air Quality Index (20 to 500). |
| **AQI_Category** | VARCHAR | | Health assessment category ('Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe'). |
| **PM2_5** | REAL | | Fine particulate matter ≤ 2.5 µm concentration ($\mu g/m^3$). |
| **PM10** | REAL | | Coarse particulate matter ≤ 10 µm concentration ($\mu g/m^3$). |
| **CO** | REAL | | Carbon Monoxide level (ppm). |
| **NO2** | REAL | | Nitrogen Dioxide level ($\mu g/m^3$). |
| **SO2** | REAL | | Sulfur Dioxide level ($\mu g/m^3$). |
| **O3** | REAL | | Ozone concentration ($\mu g/m^3$). |

### `fact_traffic`
Granular vehicle throughput logs. (365,000 rows)

| Column | Data Type | Key | Description |
| :--- | :--- | :---: | :--- |
| **Traffic_ID** | INTEGER | PK | Auto-incrementing primary key. |
| **Date** | VARCHAR | FK | Links to `dim_date`. |
| **Time** | VARCHAR | FK | Links to `dim_time`. |
| **Zone_ID** | INTEGER | FK | Links to `dim_city`. |
| **Intersection_ID**| VARCHAR | | Traffic node identifier (e.g. `Z01-I05`). |
| **Vehicle_Count** | INTEGER | | Count of unique vehicles scanned during the interval. |
| **Average_Speed** | REAL | | Mean vehicle transit speed in km/h. |
| **Congestion_Level**| VARCHAR | | Visual congestion rating ('Low', 'Moderate', 'High', 'Severe'). |
| **Travel_Time** | REAL | | Average time in minutes to clear the junction. |
| **Fuel_Wasted** | REAL | | Estimate of fuel wasted in liters due to delays. |
| **Signal_Status** | VARCHAR | | Active signal color ('Red', 'Yellow', 'Green'). |
| **Accidents** | INTEGER | | Accident occurrance flag (0 = None, 1 = Incident reported). |
| **Weather** | VARCHAR | | Weather condition during observations. |
| **Peak_Hour** | VARCHAR | | Indicates if slot is peak traffic ('Yes' or 'No'). |

### `fact_water`
Monitors clean water production, consumption, and efficiency. (3,650 rows)

| Column | Data Type | Key | Description |
| :--- | :--- | :---: | :--- |
| **Date** | VARCHAR | FK | Links to `dim_date`. |
| **Zone_ID** | INTEGER | FK | Links to `dim_city`. |
| **Water_Produced** | REAL | | Volume of clean water pumped into mains (Liters). |
| **Water_Consumed** | REAL | | Volume of metered customer consumption (Liters). |
| **Leakage** | REAL | | Unaccounted water loss in distribution (Liters). |
| **Tank_Level** | REAL | | Average local zone tank storage level (%). |
| **Reservoir_Level**| REAL | | Primary water reservoir level (%). |
| **Water_Quality_Index**| INTEGER| | Chemical/biological quality index (85 to 100). |
| **Pipe_Burst** | VARCHAR | | Flag indicating water main failure ('Yes' or 'No'). |

### `fact_electricity`
Tracks grid load and renewable offset performance. (3,650 rows)

| Column | Data Type | Key | Description |
| :--- | :--- | :---: | :--- |
| **Date** | VARCHAR | FK | Links to `dim_date`. |
| **Zone_ID** | INTEGER | FK | Links to `dim_city`. |
| **Consumption** | REAL | | Total energy grid load consumed (kWh). |
| **Peak_Load** | REAL | | Maximum power draw observed during the day (kWh). |
| **Solar_Generation**| REAL | | Total solar energy generated in zone (kWh). |
| **Battery_Level** | REAL | | Average municipal storage battery reserve (%). |
| **Power_Outage** | VARCHAR | | Indicates if grid drop occurred ('Yes' or 'No'). |
| **Voltage** | REAL | | Average line voltage (Target: 230V). |
| **Frequency** | REAL | | Average grid frequency in Hertz (Hz) (Target: 50Hz). |

### `fact_emergency`
Operational command center dispatch registry. (~2,000 rows)

| Column | Data Type | Key | Description |
| :--- | :--- | :---: | :--- |
| **Emergency_ID** | INTEGER | PK | Auto-incrementing primary key. |
| **Date** | VARCHAR | FK | Links to `dim_date`. |
| **Time** | VARCHAR | FK | Links to `dim_time`. |
| **Zone_ID** | INTEGER | FK | Links to `dim_city`. |
| **Intersection_ID**| VARCHAR | | Geographical intersection of the incident. |
| **Incident_Type** | VARCHAR | | Categorized nature of emergency. |
| **Severity** | VARCHAR | | Urgency rating ('Low', 'Medium', 'High', 'Critical'). |
| **Hospital** | VARCHAR | | Receiving medical center. |
| **Police** | VARCHAR | | Indicates police dispatch status ('Yes' or 'No'). |
| **Fire_Service** | VARCHAR | | Indicates fire service deployment status ('Yes' or 'No'). |
| **Response_Time** | REAL | | Dispatch-to-scene arrival duration (Minutes). |
| **Ambulance** | VARCHAR | | Indicates ambulance deployment status ('Yes' or 'No'). |

### `fact_iot`
Raw hourly telemetry from municipal sensors. (876,000 rows)

| Column | Data Type | Key | Description |
| :--- | :--- | :---: | :--- |
| **Sensor_ID** | VARCHAR | PK | Unique hardware MAC/ID of the sensor. |
| **Timestamp** | VARCHAR | PK | Log timestamp formatted as `YYYY-MM-DD HH:MM:SS`. |
| **Zone_ID** | INTEGER | FK | Links to `dim_city`. |
| **Sensor_Type** | VARCHAR | | Sensing unit ('Temperature', 'Humidity', 'Noise', 'AQI', 'Water Level', 'Power Usage'). |
| **Reading** | REAL | | Telemetric floating value. |
| **Status** | VARCHAR | | Sensor operational status ('Normal', 'Warning', 'Critical'). |
| **Battery_Level** | INTEGER | | Battery charge percentage remaining (%). |
| **Unit** | VARCHAR | | Measurement unit (e.g. °C, %, dB, AQI, kWh). |
