import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
GENERATORS_DIR = BASE_DIR / "Python" / "Data_Generator"

scripts = [
    "city_master_generator.py",
    "weather_generator.py",
    "traffic_generator.py",
    "air_quality_generator.py",
    "electricity_generator.py",
    "water_generator.py",
    "emergency_generator.py",
    "iot_generator.py",
    "database_loader.py"
]

def run_script(script_name):
    script_path = GENERATORS_DIR / script_name
    print(f"\n▶️ Running {script_name}...")
    
    # Run the script as a separate process to maintain scoping and clean imports
    result = subprocess.run([sys.executable, str(script_path)], capture_output=False)
    
    if result.returncode != 0:
        print(f"❌ Error: {script_name} failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    else:
        print(f"✅ Finished {script_name}")

def main():
    print("=" * 70)
    print("🏙️ SMART CITY DIGITAL TWIN DATA PIPELINE ORCHESTRATOR")
    print("=" * 70)
    
    for script in scripts:
        run_script(script)
        
    print("\n" + "=" * 70)
    print("🎉 ALL DATA GENERATED AND LOADED INTO DWH SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
