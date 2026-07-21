import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = BASE_DIR / "Documentation"
DOCS_DIR.mkdir(exist_ok=True)

def create_er_diagram():
    print("🎨 Generating ER Diagram...")
    fig, ax = plt.subplots(figsize=(18, 12), dpi=300)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(9, 11.5, "SMART CITY DIGITAL TWIN - STAR SCHEMA DATA WAREHOUSE ERD", 
            fontsize=16, fontweight='bold', ha='center', color='#1F2937', fontname='Segoe UI')
    
    # Helper to draw a table box
    def draw_table(x, y, w, h, title, columns, pk_count=1, fk_count=0):
        # Draw table header
        header = patches.FancyBboxPatch((x, y + h - 0.7), w, 0.7, boxstyle="round,pad=0.03", 
                                       facecolor='#2563EB', edgecolor='none')
        ax.add_patch(header)
        ax.text(x + w/2, y + h - 0.4, title, fontsize=10, fontweight='bold', 
                color='#FFFFFF', ha='center', va='center', fontname='Segoe UI')
        
        # Draw table body
        body = patches.FancyBboxPatch((x, y), w, h - 0.7, boxstyle="round,pad=0.03", 
                                     facecolor='#FFFFFF', edgecolor='#D1D5DB', linewidth=1)
        ax.add_patch(body)
        
        # Draw columns
        for idx, col in enumerate(columns):
            cy = y + h - 1.1 - (idx * 0.4)
            is_pk = idx < pk_count
            is_fk = pk_count <= idx < (pk_count + fk_count)
            
            weight = 'bold' if (is_pk or is_fk) else 'normal'
            color = '#1F2937' if not (is_pk or is_fk) else ('#D97706' if is_pk else '#10B981')
            
            col_text = col.split(" ")[0]
            type_text = " ".join(col.split(" ")[1:])
            
            # Key indicator
            key_icon = "🔑 " if is_pk else ("🔗 " if is_fk else "  ")
            ax.text(x + 0.2, cy, f"{key_icon}{col_text}", fontsize=8, fontweight=weight, color=color, va='center', fontname='Segoe UI')
            ax.text(x + w - 0.2, cy, type_text, fontsize=8, color='#6B7280', ha='right', va='center', fontname='Segoe UI')

    # Dimensions
    dim_city_cols = [
        "Zone_ID INT (PK)", "Zone VARCHAR", "Latitude DOUBLE", "Longitude DOUBLE", 
        "Population INT", "Area_sq_km DOUBLE", "Hospitals INT", "Police_Stations INT", 
        "Fire_Stations INT", "Traffic_Signals INT", "Water_Tanks INT", "Electric_Substations INT"
    ]
    draw_table(0.5, 7.5, 3.2, 3.8, "dim_city", dim_city_cols, pk_count=1)
    
    dim_date_cols = [
        "Date VARCHAR (PK)", "Year INT", "Quarter INT", "Month INT", 
        "Month_Name VARCHAR", "Week INT", "Day INT", "Weekend VARCHAR"
    ]
    draw_table(0.5, 3.5, 3.2, 3.6, "dim_date", dim_date_cols, pk_count=1)
    
    dim_time_cols = [
        "Time VARCHAR (PK)", "Hour INT", "Minute INT", "DayPart VARCHAR"
    ]
    draw_table(0.5, 0.5, 3.2, 2.2, "dim_time", dim_time_cols, pk_count=1)
    
    # Fact tables (Right side)
    # 1. fact_weather
    fw_cols = ["Date VARCHAR (FK)", "Zone_ID INT (FK)", "Temperature REAL", "Humidity REAL", "Rainfall REAL", "WindSpeed REAL", "Weather TEXT"]
    draw_table(5.2, 8.5, 3.2, 2.8, "fact_weather", fw_cols, pk_count=0, fk_count=2)
    
    # 2. fact_air_quality
    fa_cols = ["Date VARCHAR (FK)", "Zone_ID INT (FK)", "AQI INT", "PM2_5 REAL", "PM10 REAL", "CO REAL", "AQI_Category TEXT"]
    draw_table(5.2, 5.0, 3.2, 2.8, "fact_air_quality", fa_cols, pk_count=0, fk_count=2)
    
    # 3. fact_water
    fwa_cols = ["Date VARCHAR (FK)", "Zone_ID INT (FK)", "Water_Produced REAL", "Water_Consumed REAL", "Leakage REAL", "Tank_Level REAL", "Pipe_Burst TEXT"]
    draw_table(5.2, 1.5, 3.2, 2.8, "fact_water", fwa_cols, pk_count=0, fk_count=2)
    
    # 4. fact_electricity
    fe_cols = ["Date VARCHAR (FK)", "Zone_ID INT (FK)", "Consumption REAL", "Peak_Load REAL", "Solar_Generation REAL", "Power_Outage TEXT"]
    draw_table(9.5, 8.5, 3.2, 2.6, "fact_electricity", fe_cols, pk_count=0, fk_count=2)
    
    # 5. fact_traffic
    ft_cols = ["Traffic_ID INT (PK)", "Date VARCHAR (FK)", "Time VARCHAR (FK)", "Zone_ID INT (FK)", "Intersection_ID TEXT", "Vehicle_Count INT", "Average_Speed REAL", "Congestion_Level TEXT", "Accidents INT"]
    draw_table(9.5, 4.3, 3.2, 3.4, "fact_traffic", ft_cols, pk_count=1, fk_count=3)
    
    # 6. fact_emergency
    fem_cols = ["Emergency_ID INT (PK)", "Date VARCHAR (FK)", "Time VARCHAR (FK)", "Zone_ID INT (FK)", "Incident_Type TEXT", "Severity TEXT", "Response_Time REAL", "Hospital TEXT"]
    draw_table(9.5, 0.5, 3.2, 3.2, "fact_emergency", fem_cols, pk_count=1, fk_count=3)
    
    # 7. fact_iot
    fiot_cols = ["Sensor_ID VARCHAR (PK)", "Timestamp TEXT (PK)", "Zone_ID INT (FK)", "Sensor_Type TEXT", "Reading REAL", "Status TEXT", "Battery_Level INT", "Unit VARCHAR"]
    draw_table(13.8, 4.0, 3.4, 3.2, "fact_iot", fiot_cols, pk_count=2, fk_count=1)
    
    # Draw relationship lines (simplified lines)
    def draw_link(start_x, start_y, end_x, end_y, color='#9CA3AF'):
        ax.annotate("", xy=(end_x, end_y), xytext=(start_x, start_y),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2, ls="--", mutation_scale=10))

    # dim_city links
    draw_link(3.7, 9.4, 5.2, 9.9)  # city -> weather
    draw_link(3.7, 9.4, 5.2, 6.4)  # city -> AQI
    draw_link(3.7, 9.4, 5.2, 2.9)  # city -> water
    draw_link(3.7, 9.4, 9.5, 9.8)  # city -> electricity
    draw_link(3.7, 9.4, 9.5, 6.0)  # city -> traffic
    draw_link(3.7, 9.4, 9.5, 2.1)  # city -> emergency
    draw_link(3.7, 9.4, 13.8, 5.6) # city -> iot

    # dim_date links
    draw_link(3.7, 5.3, 5.2, 9.0)  # date -> weather
    draw_link(3.7, 5.3, 5.2, 5.5)  # date -> AQI
    draw_link(3.7, 5.3, 5.2, 2.0)  # date -> water
    draw_link(3.7, 5.3, 9.5, 9.0)  # date -> electricity
    draw_link(3.7, 5.3, 9.5, 5.2)  # date -> traffic
    draw_link(3.7, 5.3, 9.5, 1.3)  # date -> emergency

    # dim_time links
    draw_link(3.7, 1.6, 9.5, 4.8)  # time -> traffic
    draw_link(3.7, 1.6, 9.5, 0.9)  # time -> emergency

    plt.tight_layout()
    plt.savefig(DOCS_DIR / "ER_Diagram.png", bbox_inches='tight')
    plt.close()
    print("✅ ER Diagram saved to Documentation/ER_Diagram.png")

def create_architecture_diagram():
    print("🎨 Generating Architecture Diagram...")
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(7, 7.5, "SMART CITY DIGITAL TWIN - END-TO-END SYSTEM ARCHITECTURE", 
            fontsize=15, fontweight='bold', ha='center', color='#1F2937', fontname='Segoe UI')
    
    # Nodes (draw standard blocks)
    def draw_node(x, y, w, h, title, description, color):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", 
                                     facecolor=color, edgecolor='none')
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 0.4, title, fontsize=11, fontweight='bold', 
                color='#FFFFFF', ha='center', va='center', fontname='Segoe UI')
        
        # Multi-line descriptions
        for idx, line in enumerate(description):
            ax.text(x + w/2, y + h - 0.8 - (idx * 0.35), line, fontsize=8.5, 
                    color='#F9FAFB', ha='center', va='center', fontname='Segoe UI')

    # Layer 1: Data Generation (Python / Faker)
    desc_gen = [
        "Synthetic Data Generators",
        "Weather, Traffic, AQI, Water,",
        "Power Grid & IoT Telemetry",
        "Dependency Engine (Python, Pandas)"
    ]
    draw_node(0.5, 2.5, 2.6, 2.4, "1. DATA SIMULATION", desc_gen, "#4B5563")

    # Layer 2: SQLite DWH (Star Schema)
    desc_db = [
        "Relational SQLite DB",
        "Enforced PK / FK Constraints",
        "Indexes on Join Columns",
        "Pre-aggregated Views"
    ]
    draw_node(4.0, 2.5, 2.6, 2.4, "2. DATA WAREHOUSE", desc_db, "#2563EB")

    # Layer 3: ML Engine (scikit-learn)
    desc_ml = [
        "Regression Forecasting Models",
        "Predicts Jan 2026 Metrics",
        "Isolation Forest Anomaly Detection",
        "Exports outputs to CSV"
    ]
    draw_node(7.5, 2.5, 2.6, 2.4, "3. ML FORECASTING", desc_ml, "#8B5CF6")

    # Layer 4: Analytics BI (Power BI)
    desc_bi = [
        "Executive Dashboard (.pbix)",
        "Direct SQL Queries & CSV Forecasts",
        "Time Intelligence DAX Measures",
        "Corporate Color Theme UI"
    ]
    draw_node(11.0, 2.5, 2.5, 2.4, "4. BUSINESS BI", desc_bi, "#10B981")
    
    # Connecting Arrows
    def draw_arrow(start_x, start_y, end_x, end_y):
        ax.annotate("", xy=(end_x, end_y), xytext=(start_x, start_y),
                    arrowprops=dict(arrowstyle="->", color='#374151', lw=2.5, mutation_scale=15))

    draw_arrow(3.3, 3.7, 3.9, 3.7)
    draw_arrow(6.8, 3.7, 7.4, 3.7)
    draw_arrow(10.3, 3.7, 10.9, 3.7)
    
    # Feedback loop (Optional, but looks professional)
    ax.annotate("Forecasts exported as CSV and re-integrated", xy=(12.2, 2.2), xytext=(5.3, 1.0),
                arrowprops=dict(arrowstyle="->", color='#4B5563', lw=1.2, ls=":", connectionstyle="arc3,rad=-0.3"))

    plt.tight_layout()
    plt.savefig(DOCS_DIR / "Architecture.png", bbox_inches='tight')
    plt.close()
    print("✅ Architecture Diagram saved to Documentation/Architecture.png")

if __name__ == "__main__":
    create_er_diagram()
    create_architecture_diagram()
