import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------
# Page Config & Styling
# ---------------------------------------------------
st.set_page_config(
    page_title="Smart City Digital Twin - Executive Command Center",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Netflix-style Premium Dark CSS Injection
st.markdown("""
<style>
    /* Main App Background */
    .stApp {
        background-color: #090E17 !important;
        color: #E2E8F0 !important;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #070B12 !important;
        border-right: 1px solid #1E293B !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #E2E8F0 !important;
    }
    
    /* Headers */
    h1 {
        color: #E50914 !important; /* Netflix Crimson Red */
        font-family: 'Segoe UI', sans-serif;
        font-weight: 800 !important;
        text-shadow: 0 0 15px rgba(229, 9, 20, 0.4);
        letter-spacing: 0.5px;
    }
    h2, h3 {
        color: #F8FAFC !important;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 600 !important;
        margin-top: 15px !important;
    }
    
    /* Sleek Glassmorphic Card Container */
    .metric-card {
        background-color: #111827 !important;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        border: 1px solid #1F2937 !important;
        text-align: center;
        margin-bottom: 10px;
        transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #E50914 !important; /* glowing red border on hover */
        box-shadow: 0 0 15px rgba(229, 9, 20, 0.25);
    }
    .metric-title {
        color: #9CA3AF !important;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 5px;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #F9FAFB !important;
        font-size: 30px;
        font-weight: 800;
    }
    .metric-sub {
        font-size: 12px;
        margin-top: 5px;
        font-weight: 500;
    }
    
    /* Tab Styling */
    button[data-baseweb="tab"] {
        color: #9CA3AF !important;
        font-weight: 600 !important;
    }
    button[aria-selected="true"] {
        color: #E50914 !important;
        border-bottom-color: #E50914 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Load Data Helper Functions
# ---------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "smart_city.db"
FORECAST_PATH = BASE_DIR / "data" / "processed" / "ml_forecasts.csv"
ANOMALIES_PATH = BASE_DIR / "data" / "processed" / "iot_anomalies.csv"

def query_db(query, params=()):
    if not DB_PATH.exists():
        # Check if compressed database exists and extract it
        zip_path = BASE_DIR / "database" / "smart_city.db.zip"
        if zip_path.exists():
            with st.spinner("📦 Extracting Smart City Digital Twin database (approx. 2 seconds)..."):
                import zipfile
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(BASE_DIR / "database")
                    
    if not DB_PATH.exists():
        st.error(f"❌ Database not found at {DB_PATH}. Please run python Python/Data_Generator/main.py first.")
        st.stop()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/000000/city.png", width=80)
st.sidebar.title("Operational Filters")

# Fetch dynamic metadata
zones_df = query_db("SELECT Zone_ID, Zone FROM dim_city ORDER BY Zone_ID")
zone_options = {"All Zones": 0}
for _, r in zones_df.iterrows():
    zone_options[r["Zone"]] = int(r["Zone_ID"])

selected_zone_name = st.sidebar.selectbox("Select Zone", list(zone_options.keys()))
selected_zone_id = zone_options[selected_zone_name]

# Date slider setup
dates_df = query_db("SELECT MIN(Date) as start, MAX(Date) as end FROM dim_date")
start_date_dwh = datetime.strptime(dates_df["start"].iloc[0], "%Y-%m-%d").date()
end_date_dwh = datetime.strptime(dates_df["end"].iloc[0], "%Y-%m-%d").date()

selected_date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=start_date_dwh,
    max_value=end_date_dwh,
    value=(start_date_dwh, end_date_dwh)
)
start_date_str = selected_date_range[0].strftime("%Y-%m-%d")
end_date_str = selected_date_range[1].strftime("%Y-%m-%d")

# Weather condition filters
weather_list = ["All", "Sunny", "Cloudy", "Rain", "Storm", "Fog"]
selected_weather = st.sidebar.selectbox("Weather Condition", weather_list)

# ---------------------------------------------------
# Main SQL Query Builder based on Sidebar
# ---------------------------------------------------
where_clause_args = []
where_clause_parts = ["Date BETWEEN ? AND ?"]
where_clause_args.extend([start_date_str, end_date_str])

if selected_zone_id != 0:
    where_clause_parts.append("Zone_ID = ?")
    where_clause_args.append(selected_zone_id)

# ---------------------------------------------------
# HEADER BANNER
# ---------------------------------------------------
st.title("🏙️ SMART CITY DIGITAL TWIN")
st.subheader("Executive Command Center - Real-Time Performance & ML Forecasting Dashboard")
st.markdown("---")

# ---------------------------------------------------
# DATA EXTRACTION & AGGREGATIONS FOR KPIs
# ---------------------------------------------------
# Traffic Aggregation
traffic_q = f"SELECT SUM(Vehicle_Count) as tot_veh, AVG(Average_Speed) as avg_spd, SUM(Accidents) as tot_acc FROM fact_traffic WHERE {' AND '.join(where_clause_parts)}"
traffic_stats = query_db(traffic_q, where_clause_args)

# AQI Aggregation
aqi_q = f"SELECT AVG(AQI) as avg_aqi FROM fact_air_quality WHERE {' AND '.join(where_clause_parts)}"
aqi_stats = query_db(aqi_q, where_clause_args)

# Water Aggregation
water_q = f"SELECT SUM(Water_Produced) as prod, SUM(Water_Consumed) as cons, SUM(Leakage) as leak FROM fact_water WHERE {' AND '.join(where_clause_parts)}"
water_stats = query_db(water_q, where_clause_args)

# Electricity Aggregation
elec_q = f"SELECT SUM(Consumption) as cons, SUM(Solar_Generation) as solar, SUM(CASE WHEN Power_Outage='Yes' THEN 1 ELSE 0 END) as outages FROM fact_electricity WHERE {' AND '.join(where_clause_parts)}"
elec_stats = query_db(elec_q, where_clause_args)

# Emergency Aggregation
em_q = f"SELECT COUNT(*) as incidents, AVG(Response_Time) as resp FROM fact_emergency WHERE {' AND '.join(where_clause_parts)}"
em_stats = query_db(em_q, where_clause_args)

# IoT Health Stats
iot_q = f"SELECT Status, COUNT(*) as count FROM fact_iot GROUP BY Status"
iot_stats = query_db(iot_q)
iot_total = iot_stats["count"].sum()
iot_critical = iot_stats[iot_stats["Status"] == "Critical"]["count"].sum()
iot_online = iot_total - iot_critical

# Render KPI Columns
kpi_cols = st.columns(5)

with kpi_cols[0]:
    val = f"{int(traffic_stats['tot_veh'].iloc[0] or 0):,}"
    spd = f"{float(traffic_stats['avg_spd'].iloc[0] or 0):.1f} kmph avg speed"
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">🚗 Mobility & Traffic</div>
        <div class="metric-value">{val}</div>
        <div class="metric-sub" style="color: #38BDF8;">{spd}</div>
    </div>""", unsafe_allow_html=True)

with kpi_cols[1]:
    aqi_val = int(aqi_stats['avg_aqi'].iloc[0] or 0)
    if aqi_val <= 50: aqi_c, aqi_lbl = "#10B981", "Good"
    elif aqi_val <= 100: aqi_c, aqi_lbl = "#F59E0B", "Satisfactory"
    else: aqi_c, aqi_lbl = "#EF4444", "Moderate/Poor"
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">🍃 Environmental AQI</div>
        <div class="metric-value">{aqi_val}</div>
        <div class="metric-sub" style="color: {aqi_c}; font-weight: bold;">{aqi_lbl} Category</div>
    </div>""", unsafe_allow_html=True)

with kpi_cols[2]:
    cons_mwh = (elec_stats['cons'].iloc[0] or 0) / 1000.0
    solar_mwh = (elec_stats['solar'].iloc[0] or 0) / 1000.0
    solar_pct = (solar_mwh * 100 / cons_mwh) if cons_mwh > 0 else 0
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">⚡ Power & Solar Grid</div>
        <div class="metric-value">{cons_mwh:,.1f} MWh</div>
        <div class="metric-sub" style="color: #FBBF24;">{solar_pct:.1f}% Solar Offset ({elec_stats['outages'].iloc[0] or 0} Outages)</div>
    </div>""", unsafe_allow_html=True)

with kpi_cols[3]:
    prod_ml = (water_stats['prod'].iloc[0] or 0) / 1000000.0
    cons_ml = (water_stats['cons'].iloc[0] or 0) / 1000000.0
    leak_pct = (water_stats['leak'].iloc[0] or 0) * 100 / water_stats['prod'].iloc[0] if (water_stats['prod'].iloc[0] or 0) > 0 else 0
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">💧 Clean Water Supply</div>
        <div class="metric-value">{cons_ml:,.1f} ML</div>
        <div class="metric-sub" style="color: #F87171;">{leak_pct:.1f}% Pipeline Leakage</div>
    </div>""", unsafe_allow_html=True)

with kpi_cols[4]:
    inc = em_stats['incidents'].iloc[0] or 0
    resp_t = em_stats['resp'].iloc[0] or 0
    st.markdown(f"""<div class="metric-card">
        <div class="metric-title">🚨 Emergency Center</div>
        <div class="metric-value">{inc:,} Calls</div>
        <div class="metric-sub" style="color: #F87171;">{resp_t:.1f} Min Avg Response Time</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------
# DASHBOARD TABS
# ---------------------------------------------------
tabs = st.tabs([
    "📍 Live Command Map & Mobility", 
    "🍃 Air & Utilities Grid", 
    "🚨 Emergency Center Dispatches", 
    "🔮 Predictive Digital Twin (ML)", 
    "📶 IoT Sensor Network Status"
])

# ===================================================
# TAB 1: Live Command Map & Mobility
# ===================================================
with tabs[0]:
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.subheader("Geographical Distribution: City Zones Command Map")
        # Load geographic positions
        geo_q = "SELECT Zone_ID, Zone, Latitude, Longitude, Population, Hospitals, Police_Stations FROM dim_city"
        geo_df = query_db(geo_q)
        
        # Pull latest daily AQI per zone to display on map hover
        latest_aqi = query_db("SELECT Zone_ID, AQI, AQI_Category FROM fact_air_quality WHERE Date = (SELECT MAX(Date) FROM fact_air_quality)")
        map_df = pd.merge(geo_df, latest_aqi, on="Zone_ID")
        
        # Render bubble map
        fig_map = px.scatter_mapbox(
            map_df, 
            lat="Latitude", 
            lon="Longitude",
            color="AQI",
            size="Population",
            hover_name="Zone",
            hover_data=["Population", "AQI", "Hospitals", "Police_Stations"],
            color_continuous_scale="RdYlGn_r",
            size_max=35,
            zoom=11.5,
            mapbox_style="carto-darkmatter"
        )
        fig_map.update_layout(
            template="plotly_dark",
            margin={"r":0,"t":0,"l":0,"b":0}, 
            height=500,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_map, use_container_width=True)
        
    with col2:
        st.subheader("Junction Volume & Traffic Flow Analytics")
        # Daily aggregated traffic curve
        traffic_trend = query_db(f"""
            SELECT Time, AVG(Vehicle_Count) as avg_vehicles, AVG(Average_Speed) as avg_speed 
            FROM fact_traffic 
            WHERE {' AND '.join(where_clause_parts)}
            GROUP BY Time
            ORDER BY Time
        """, where_clause_args)
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=traffic_trend["Time"], y=traffic_trend["avg_vehicles"], 
            name="Avg Vehicle Count", marker_color="#E50914", yaxis="y"
        ))
        fig_trend.add_trace(go.Scatter(
            x=traffic_trend["Time"], y=traffic_trend["avg_speed"], 
            name="Avg Speed (kmph)", line=dict(color="#06B6D4", width=3), yaxis="y2"
        ))
        
        fig_trend.update_layout(
            template="plotly_dark",
            height=450,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(title="Vehicle Count", gridcolor="#1F2937"),
            yaxis2=dict(title="Speed (kmph)", overlaying="y", side="right", gridcolor="#1F2937"),
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_trend, use_container_width=True)

# ===================================================
# TAB 2: Air & Utilities Grid
# ===================================================
with tabs[1]:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("AQI Categories Profile")
        aqi_dist = query_db(f"""
            SELECT AQI_Category, COUNT(*) as count 
            FROM fact_air_quality 
            WHERE {' AND '.join(where_clause_parts)}
            GROUP BY AQI_Category
        """, where_clause_args)
        
        fig_aqi = px.pie(
            aqi_dist, names="AQI_Category", values="count",
            color_discrete_sequence=["#10B981", "#F59E0B", "#E50914", "#8B5CF6"]
        )
        fig_aqi.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_aqi, use_container_width=True)
        
    with col2:
        st.subheader("Clean Water Production vs. Consumption")
        water_trend = query_db(f"""
            SELECT Date, SUM(Water_Produced) as prod, SUM(Water_Consumed) as cons, SUM(Leakage) as leak
            FROM fact_water
            WHERE {' AND '.join(where_clause_parts)}
            GROUP BY Date
            ORDER BY Date
        """, where_clause_args)
        
        fig_wat = go.Figure()
        fig_wat.add_trace(go.Scatter(x=water_trend["Date"], y=water_trend["prod"]/1e6, fill='tozeroy', name="Produced (ML)", line_color="#1E3A8A"))
        fig_wat.add_trace(go.Scatter(x=water_trend["Date"], y=water_trend["cons"]/1e6, name="Consumed (ML)", line_color="#38BDF8"))
        fig_wat.update_layout(
            template="plotly_dark",
            height=400, 
            yaxis_title="Volume (Million Liters)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#1F2937"),
            xaxis=dict(gridcolor="#1F2937")
        )
        st.plotly_chart(fig_wat, use_container_width=True)
        
    with col3:
        st.subheader("Solar Generation Grid Offset")
        power_trend = query_db(f"""
            SELECT Date, SUM(Consumption) as cons, SUM(Solar_Generation) as solar
            FROM fact_electricity
            WHERE {' AND '.join(where_clause_parts)}
            GROUP BY Date
            ORDER BY Date
        """, where_clause_args)
        
        fig_pow = go.Figure()
        fig_pow.add_trace(go.Scatter(x=power_trend["Date"], y=power_trend["cons"]/1e3, name="Grid Load (MWh)", line_color="#E50914"))
        fig_pow.add_trace(go.Scatter(x=power_trend["Date"], y=power_trend["solar"]/1e3, name="Solar Offset (MWh)", fill='tozeroy', line_color="#FBBF24"))
        fig_pow.update_layout(
            template="plotly_dark",
            height=400, 
            yaxis_title="Energy Load (MWh)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#1F2937"),
            xaxis=dict(gridcolor="#1F2937")
        )
        st.plotly_chart(fig_pow, use_container_width=True)

# ===================================================
# TAB 3: Emergency Center Dispatches
# ===================================================
with tabs[2]:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Incident Types Profile")
        em_dist = query_db(f"""
            SELECT Incident_Type, COUNT(*) as count 
            FROM fact_emergency 
            WHERE {' AND '.join(where_clause_parts)}
            GROUP BY Incident_Type
        """, where_clause_args)
        fig_em_pie = px.pie(
            em_dist, names="Incident_Type", values="count", hole=0.4, 
            color_discrete_sequence=["#E50914", "#F87171", "#EF4444", "#FCA5A5", "#FEE2E2"]
        )
        fig_em_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_em_pie, use_container_width=True)
        
    with col2:
        st.subheader("Dispatch Severity & Speed by Incident Category")
        em_sev = query_db(f"""
            SELECT Incident_Type, Severity, COUNT(*) as count, AVG(Response_Time) as resp
            FROM fact_emergency
            WHERE {' AND '.join(where_clause_parts)}
            GROUP BY Incident_Type, Severity
        """, where_clause_args)
        fig_em_bar = px.bar(
            em_sev, x="Incident_Type", y="count", color="Severity", 
            color_discrete_map={"Critical": "#E50914", "High": "#F59E0B", "Medium": "#3B82F6", "Low": "#10B981"}
        )
        fig_em_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#1F2937"),
            xaxis=dict(gridcolor="#1F2937")
        )
        st.plotly_chart(fig_em_bar, use_container_width=True)

# ===================================================
# TAB 4: Predictive Digital Twin (ML)
# ===================================================
with tabs[3]:
    st.subheader("🔮 Forecasting January 2026 Operational Metrics")
    st.markdown("This module maps actual 2025 metrics to a **scikit-learn** model, forecasting the first 30 days of 2026 based on weather simulations.")
    
    if not FORECAST_PATH.exists():
        st.warning("⚠️ Forecasting outputs file ml_forecasts.csv not found in data/processed/. Run python Python/Forecasting/train_models.py first.")
    else:
        df_forecast = pd.read_csv(FORECAST_PATH)
        df_forecast["Date"] = pd.to_datetime(df_forecast["Date"])
        
        # Metric Selector
        metric_options = {
            "Traffic Volume": "Traffic_Volume",
            "Air Quality Index (AQI)": "AQI",
            "Electricity Demand (kWh)": "Electricity_Demand",
            "Water Consumption (Liters)": "Water_Consumption"
        }
        selected_metric = st.selectbox("Select Metric to Display", list(metric_options.keys()))
        db_metric = metric_options[selected_metric]
        
        # Filter predictions by metric and zone (if selected)
        df_m = df_forecast[df_forecast["Metric_Name"] == db_metric]
        if selected_zone_id != 0:
            df_m = df_m[df_m["Zone_ID"] == selected_zone_id]
            
        # Group to daily sum/mean based on the metric
        agg_func = "sum" if "Volume" in selected_metric or "Demand" in selected_metric or "Consumption" in selected_metric else "mean"
        df_chart = df_m.groupby(["Date", "Scenario"]).agg({"Forecast_Value": agg_func}).reset_index()
        
        # Plotly chart showing actuals vs forecast
        fig_fore = px.line(
            df_chart, x="Date", y="Forecast_Value", color="Scenario",
            color_discrete_map={"Actual": "#4B5563", "Forecast (ML)": "#E50914"},
            labels={"Forecast_Value": selected_metric}
        )
        fig_fore.update_layout(
            template="plotly_dark",
            height=450, 
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="#1F2937"),
            xaxis=dict(gridcolor="#1F2937")
        )
        st.plotly_chart(fig_fore, use_container_width=True)

# ===================================================
# TAB 5: IoT Sensor Network Status
# ===================================================
with tabs[4]:
    st.subheader("📡 Municipal IoT Transceiver Dashboard")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <div class="metric-card" style="border-left: 5px solid #10B981;">
                <div class="metric-title">Online Sensors</div>
                <div class="metric-value">{iot_online:,}</div>
                <div class="metric-sub">Normal / Warning Status</div>
            </div>
            <div class="metric-card" style="border-left: 5px solid #EF4444;">
                <div class="metric-title">Critical Offline</div>
                <div class="metric-value">{iot_critical:,}</div>
                <div class="metric-sub">Battery Deficits & Spikes</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.subheader("Live Isolation Forest Outlier Feed (Anomaly Log)")
        if not ANOMALIES_PATH.exists():
            st.warning("⚠️ Anomalies file iot_anomalies.csv not found in data/processed/. Run python Python/Forecasting/anomaly_detection.py first.")
        else:
            df_anomalies = pd.read_csv(ANOMALIES_PATH)
            
            # Select specific sensor type filter
            sensor_filter = st.selectbox("Filter Anomalies by Sensor Category", ["All"] + list(df_anomalies["Sensor_Type"].unique()))
            df_a_show = df_anomalies.copy()
            if sensor_filter != "All":
                df_a_show = df_a_show[df_a_show["Sensor_Type"] == sensor_filter]
                
            st.dataframe(
                df_a_show[["Sensor_ID", "Timestamp", "Zone", "Sensor_Type", "Reading", "Unit", "Battery_Level", "Anomaly_Score"]].head(25),
                use_container_width=True,
                height=300
            )

# ---------------------------------------------------
# Footer Info
# ---------------------------------------------------
st.markdown("---")
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 11px;'>Smart City Digital Twin Command Center Dashboard © 2026. Made with Python, Streamlit, SQLite, and scikit-learn.</p>", unsafe_allow_html=True)
