# Smart City Digital Twin: Enterprise Command Center & Analytics Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://amritanshu1968-wq-smart-city-digital-twin-app-dii0vm.streamlit.app/)

🔗 **Live Web Application:** Experience the operational command center dashboard live in your browser: **[Smart City Digital Twin Command Center](https://amritanshu1968-wq-smart-city-digital-twin-app-dii0vm.streamlit.app/)**

An end-to-end, enterprise-grade data warehouse and predictive analytics platform simulating a real-time Municipal Command Center. Built with Python (Pandas, NumPy, scikit-learn), SQL (SQLite / PostgreSQL), Power BI, and Git.

Designed to demonstrate production-level skills in data engineering, DWH star-schema modeling, analytical SQL queries, time-series forecasting, anomaly detection, and corporate-standard BI dashboards.

---

## 🗺️ System Architecture

The platform follows a classic enterprise-grade business intelligence data lifecycle:

```
[1. SIMULATION ENGINE]     [2. DATA WAREHOUSE]      [3. ML ANALYTICS ENGINE]     [4. ENTERPRISE BI]
  Python + Faker + NumPy   SQLite DWH (Star Schema)     scikit-learn Models      Power BI Dashboard
       (Raw CSVs)          (PRAGMA Foreign Keys)      (Forecasts + Anomalies)    (Segoe UI + Theme)
           │                        │                           │                         │
           ▼                        ▼                           ▼                         ▼
   Generates 1.2M+ rows ──► Strict DQL Loader ──► Predicts Jan 2026 Metrics ──► Dynamic Slicers,
   of physical telemetry    PKs, FKs & Indexes     Isolation Forest Outliers    Bookmarks & Map KPIs
```

- **Data Simulation**: Simulates weather, traffic, air quality (AQI), water supply, electrical grid loads, emergency dispatches, and raw IoT sensor telemetry over 365 days, incorporating realistic physical correlations (e.g., weather and traffic peak hours driving emergency dispatch frequency).
- **Data Warehousing**: Enforces a robust Star Schema with primary and foreign keys, custom compound indexes for optimized joins, and pre-aggregated analytical views.
- **Machine Learning**: Leverages `scikit-learn` to forecast key municipal indicators 30 days into the future and implements an `IsolationForest` anomaly detection model to flag outlier IoT readings.
- **Business Intelligence**: A Microsoft Fabric/Azure-themed dashboard incorporating custom bookmarks, rich hover tooltips, page-to-page drillthroughs, and time-intelligence DAX measures.

---

## 📂 Project Structure

```
Smart-City-Digital-Twin/
│
├── Assets/                        # Design assets
│   ├── icons/                     # UI Icons
│   └── screenshots/               # Dashboard previews
│
├── data/                          # Data layers
│   ├── raw/                       # Generated raw CSVs (1.2M+ total rows)
│   └── processed/                 # ML forecasts, IoT anomalies, dimension files
│
├── database/                      # Relational database layer
│   └── smart_city.db              # SQLite Data Warehouse
│
├── Documentation/                 # Technical documentation
│   ├── Architecture.png           # Pipeline architecture diagram
│   ├── ER_Diagram.png             # Star Schema Entity-Relationship Diagram
│   └── Data_Dictionary.md         # Field-level database descriptions
│
├── PowerBI/                       # Business intelligence workspace
│   ├── SmartCity.pbix             # Core Power BI Desktop dashboard
│   ├── Theme.json                 # Custom Azure/Fabric corporate color theme
│   └── dax_measures.dax           # Copy-paste DAX formulas reference
│
├── Python/                        # Codebase
│   ├── Data_Generator/            # Data engineering scripts
│   │   ├── city_master_generator.py
│   │   ├── weather_generator.py
│   │   ├── traffic_generator.py   # Generates 365k traffic logs
│   │   ├── air_quality_generator.py
│   │   ├── electricity_generator.py
│   │   ├── water_generator.py
│   │   ├── emergency_generator.py  # Models emergency incidents (~1.7k rows)
│   │   ├── iot_generator.py       # Simulates 876k sensor readings
│   │   ├── database_loader.py     # Schema creation, indexing, DWH load
│   │   └── main.py                # Main orchestrator
│   │
│   ├── Forecasting/               # Predictive modeling scripts
│   │   ├── train_models.py        # ML regression forecasting for Jan 2026
│   │   └── anomaly_detection.py   # Isolation Forest anomaly detection
│   │
│   └── Utilities/                 # Developer tools
│       └── generate_diagrams.py   # Renders ERD/Architecture PNGs programmatically
│
├── LICENSE                        # MIT License
├── requirements.txt               # Project dependencies
└── .gitignore
```

---

## 🗄️ Data Warehouse Star Schema

The data warehouse consists of **3 Dimension Tables** and **7 Fact Tables**, fully indexed to accelerate analytical queries. Refer to the [Data Dictionary](file:///c:/Users/Amritanshu/OneDrive/Desktop/Smart-City-Digital-Twin/Documentation/Data_Dictionary.md) for full field descriptions.

### Dimension Tables
1. **`dim_city`**: Holds population, location (latitude/longitude), area, and infrastructure counts for the 10 municipal zones.
2. **`dim_date`**: Calendar-level attributes supporting time-intelligence aggregations (Year, Month, Quarter, Week, Weekend flag).
3. **`dim_time`**: Clock-level intervals (Hour, Minute, DayPart segment).

### Fact Tables & Row Counts
- **`fact_weather`** (3,650 rows): Temperature, humidity, pressure, wind speed, daily precipitation, weather conditions.
- **`fact_air_quality`** (3,650 rows): AQI index, categorizations, and concentrations of $\text{PM}_{2.5}$, $\text{PM}_{10}$, $\text{CO}$, $\text{NO}_2$, $\text{SO}_2$, and $\text{O}_3$.
- **`fact_traffic`** (365,000 rows): Intersection vehicle counts, speed, congestion, travel time, accidents, and fuel wasted.
- **`fact_water`** (3,650 rows): Production vs metered consumption volumes, network leakages, tank/reservoir reserves, and pipe bursts.
- **`fact_electricity`** (3,650 rows): Grid consumption, peak load, solar generation offsets, battery storage level, and outage flags.
- **`fact_emergency`** (~1,700 rows): Dispatch logs (incident type, severity, ambulance/police/fire response times, receiving hospitals).
- **`fact_iot`** (876,000 rows): Telemetry from 100 hourly temperature, humidity, noise, water, power, and AQI sensors.

---

## 🎛️ Analytical SQL Views

The database DDL includes pre-built views to streamline Power BI imports and rapid reporting:
- `view_traffic_summary`: Speed trends, accident counts, and peak congestion volumes.
- `view_aqi_summary`: AQI classification counts and critical pollutant levels.
- `view_water_usage_summary`: Main pipeline leakage percentage and pipe burst incident rates.
- `view_electricity_summary`: Solar offset percentages, power grid outages, and battery reserves.
- `view_emergency_dashboard`: Dynamic response times, severity breakdowns, and dispatch logs.
- `view_iot_dashboard`: Sensor status summaries and battery warning metrics.

Check the query examples in [analytics_queries.sql](file:///c:/Users/Amritanshu/OneDrive/Desktop/Smart-City-Digital-Twin/SQL/analytics_queries.sql) to see how window functions, CTEs, and multi-joins are used to calculate complex indicators.

---

## 🤖 Machine Learning Forecasting

The `Forecasting/` directory runs advanced analytical pipelines:
1. **Regression Forecasting (`train_models.py`)**:
   - Trains ML algorithms (Random Forest & Linear Regression) to predict future values.
   - Learns relationships between variables (e.g., how weather and weekend status affect traffic flow; how temperature drives electricity grid loads).
   - Projects predictions for Jan 2026 and saves them to `data/processed/ml_forecasts.csv` for side-by-side comparison in Power BI.
2. **Anomaly Detection (`anomaly_detection.py`)**:
   - Deploys an `IsolationForest` model grouped by sensor type to evaluate raw IoT telemetry.
   - Detects malfunctioning hardware (e.g., sudden voltage drops, extreme temperature spikes, or sensor lockups).
   - Generates `data/processed/iot_anomalies.csv` to feed the maintenance dispatch dashboard.

---

## 📊 Power BI Executive Dashboard

The `SmartCity.pbix` file is a premium corporate-grade reporting solution designed with the custom color theme configured in `Theme.json`.

### Dashboard Layout & Features:
- **Title Banner**: Smart City Digital Twin - Executive Command Center.
- **Slicers Panel**: Dynamic filters by date range, zone, and weather conditions.
- **KPI Metrics**: Cards showing vehicles, air quality index, power levels, water supply, emergency dispatches, and online sensors.
- **Interactives**:
  - **Map Visual**: Bubble map showing zone coordinates with metrics (AQI, emergencies, traffic speed) mapped to card tooltips.
  - **Diurnal Traffic Curves**: Hourly vehicle counts vs. speed levels.
  - **Environmental & Utility Trends**: Synchronized charts comparing water leakage %, solar energy offsets, and AQI shifts.
  - **Emergency Response**: Response time charts categorized by incident type and severity.
- **Advanced Navigation**: Customized bookmarks for quick view resets, rich tooltips on hover, and page drill-through to view raw sensor logs.

---

## 🛠️ Installation & Getting Started

### Prerequisites
- Python 3.10 or higher
- Power BI Desktop (for opening the `.pbix` dashboard)

### 1. Setup the Environment
```bash
# Clone the repository
git clone https://github.com/your-username/Smart-City-Digital-Twin.git
cd Smart-City-Digital-Twin

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Data & Create Database
Runs the data engineering orchestrator to build the DWH:
```bash
python Python/Data_Generator/main.py
```
This generates raw CSVs in `data/raw/`, builds the schema and views in `SQL/`, and populates the SQLite database `database/smart_city.db`.

### 3. Run Machine Learning Pipeline
Trains forecasting models and flags IoT anomalies:
```bash
python Python/Forecasting/train_models.py
python Python/Forecasting/anomaly_detection.py
```
This exports forecasting results and anomalies to `data/processed/` for direct Power BI consumption.

### 4. Open the Power BI Dashboard
1. Open [PowerBI/SmartCity.pbix](file:///c:/Users/Amritanshu/OneDrive/Desktop/Smart-City-Digital-Twin/PowerBI/SmartCity.pbix) in Power BI Desktop.
2. Go to **Home > Transform Data** to open Power Query Editor.
3. Update the source paths of the SQLite database connection and the ML forecast/anomaly CSV files to point to your local project directory.
4. Click **Close & Apply** to refresh the dashboard.

### 5. Launch the Streamlit Web Dashboard
To view the command center, maps, forecasting models, and anomaly logs directly in your browser, run:
```bash
streamlit run app.py
```
This will open the dashboard in your default web browser (typically at `http://localhost:8501`).

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](file:///c:/Users/Amritanshu/OneDrive/Desktop/Smart-City-Digital-Twin/LICENSE) file for details.
