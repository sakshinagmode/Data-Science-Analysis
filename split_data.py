"""
Data Splitter for Urban Mobility Project
=========================================
This script takes the master raw dataset and splits it into 4 separate
"source" files, simulating how data would arrive from 4 different systems.

This creates the foundation for the 4-member team cleaning workflow.

Output Files:
1. source_traffic_raw.csv   (Member 1) - Timestamp, Zone, Traffic Speed
2. source_aqi_raw.csv       (Member 2) - Timestamp, Zone, PM2.5 Level
3. source_transit_raw.csv   (Member 3) - Timestamp, Zone, Bus Delay Status
4. source_weather_raw.csv   (Member 4) - Timestamp, Zone, Weather
"""

import pandas as pd
import os

# --- Configuration ---
INPUT_FILE = "urban_mobility_raw.csv"
OUTPUT_DIR = "raw_sources"

SOURCE_CONFIGS = {
    "source_traffic_raw.csv": {
        "columns": ["Timestamp", "City_Zone", "Avg_Speed_kmh"],
        "description": "Traffic Camera Network Data (Member 1)"
    },
    "source_aqi_raw.csv": {
        "columns": ["Timestamp", "City_Zone", "PM2_5_Level"],
        "description": "Air Quality Sensor Data (Member 2)"
    },
    "source_transit_raw.csv": {
        "columns": ["Timestamp", "City_Zone", "Bus_Delay_Status"],
        "description": "Public Transit Telemetry Data (Member 3)"
    },
    "source_weather_raw.csv": {
        "columns": ["Timestamp", "City_Zone", "Weather"],
        "description": "Weather Feed Data (Member 4)"
    }
}


def main():
    print("=" * 60)
    print("URBAN MOBILITY DATA SPLITTER")
    print("=" * 60)
    
    # Create output directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")
    
    # Load master data
    print(f"\nLoading master data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df):,} rows")
    
    # Split into source files
    print(f"\nSplitting into {len(SOURCE_CONFIGS)} source files...")
    print("-" * 60)
    
    for filename, config in SOURCE_CONFIGS.items():
        output_path = os.path.join(OUTPUT_DIR, filename)
        columns = config["columns"]
        description = config["description"]
        
        # Extract columns
        source_df = df[columns].copy()
        
        # Save to CSV
        source_df.to_csv(output_path, index=False)
        
        print(f"✓ {filename}")
        print(f"  └─ Description: {description}")
        print(f"  └─ Columns: {columns}")
        print(f"  └─ Rows: {len(source_df):,}")
        print(f"  └─ Saved to: {output_path}")
        print()
    
    print("=" * 60)
    print("DATA SPLITTING COMPLETE!")
    print(f"All source files saved to: {OUTPUT_DIR}/")
    print("=" * 60)
    
    # Summary table
    print("\nSUMMARY TABLE:")
    print("-" * 60)
    print(f"{'Source File':<30} {'Team Member':<15} {'Rows':>10}")
    print("-" * 60)
    for filename, config in SOURCE_CONFIGS.items():
        member = config["description"].split("(")[1].replace(")", "")
        print(f"{filename:<30} {member:<15} {len(df):>10,}")
    print("-" * 60)


if __name__ == "__main__":
    main()
