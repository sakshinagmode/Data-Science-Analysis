"""
Data Merger and Feature Engineering Script
===========================================
This script merges all 4 cleaned data streams and creates
feature-engineered columns for the final Clean_Master_Data.csv

Member 3's Responsibility (as per project plan)

Input Files:
- cleaned_data/traffic_cleaned.csv
- cleaned_data/aqi_cleaned.csv
- cleaned_data/transit_cleaned.csv
- cleaned_data/weather_cleaned.csv

Output:
- Clean_Master_Data.csv

Feature Engineering:
1. Is_Rush_Hour (Boolean) - True if 08:00-10:00 or 17:00-19:00
2. Environmental_Risk (Float) - Composite score: (PM2.5/10) + (Speed_Penalty)
3. Day_Of_Week (String) - Extracted from timestamp
4. Hour_Of_Day (Int) - Extracted from timestamp
"""

import pandas as pd
import numpy as np
import os

# --- Configuration ---
CLEANED_DATA_DIR = "cleaned_data"
OUTPUT_FILE = "Clean_Master_Data.csv"

INPUT_FILES = {
    'traffic': os.path.join(CLEANED_DATA_DIR, 'traffic_cleaned.csv'),
    'aqi': os.path.join(CLEANED_DATA_DIR, 'aqi_cleaned.csv'),
    'transit': os.path.join(CLEANED_DATA_DIR, 'transit_cleaned.csv'),
    'weather': os.path.join(CLEANED_DATA_DIR, 'weather_cleaned.csv')
}


def load_cleaned_data():
    """Load all cleaned data streams."""
    print("Loading cleaned data streams...")
    
    dataframes = {}
    for name, filepath in INPUT_FILES.items():
        df = pd.read_csv(filepath)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        dataframes[name] = df
        print(f"  Loaded {name}: {len(df):,} rows")
    
    return dataframes


def merge_data(dataframes):
    """Merge all data streams on Timestamp and City_Zone."""
    print("\nMerging data streams...")
    
    # Start with traffic as base
    merged = dataframes['traffic'].copy()
    print(f"  Base (traffic): {len(merged):,} rows")
    
    # Merge with AQI
    merged = merged.merge(
        dataframes['aqi'][['Timestamp', 'City_Zone', 'PM2_5_Level']],
        on=['Timestamp', 'City_Zone'],
        how='inner'
    )
    print(f"  After AQI merge: {len(merged):,} rows")
    
    # Merge with Transit
    merged = merged.merge(
        dataframes['transit'][['Timestamp', 'City_Zone', 'Delay_Minutes']],
        on=['Timestamp', 'City_Zone'],
        how='inner'
    )
    print(f"  After Transit merge: {len(merged):,} rows")
    
    # Merge with Weather
    merged = merged.merge(
        dataframes['weather'][['Timestamp', 'City_Zone', 'Weather']],
        on=['Timestamp', 'City_Zone'],
        how='inner'
    )
    print(f"  After Weather merge: {len(merged):,} rows")
    
    return merged


def feature_is_rush_hour(df):
    """
    Feature 1: Is_Rush_Hour
    True if time is between 08:00-10:00 or 17:00-19:00
    """
    print("\n[FEATURE] Creating Is_Rush_Hour...")
    
    hour = df['Timestamp'].dt.hour
    df['Is_Rush_Hour'] = ((hour >= 8) & (hour < 10)) | ((hour >= 17) & (hour < 19))
    
    rush_hour_count = df['Is_Rush_Hour'].sum()
    print(f"  Rush hour entries: {rush_hour_count:,} ({rush_hour_count/len(df)*100:.1f}%)")
    
    return df


def feature_environmental_risk(df):
    """
    Feature 2: Environmental_Risk
    Composite score combining PM2.5 levels and traffic conditions.
    Formula: (PM2.5 / 10) + Speed_Penalty
    
    Speed_Penalty:
    - Low speed (< 20 km/h): +3 (congestion = idling = more emissions)
    - Medium speed (20-60 km/h): 0 (optimal)
    - High speed (> 60 km/h): +1 (higher fuel consumption)
    """
    print("\n[FEATURE] Creating Environmental_Risk...")
    
    # Calculate speed penalty
    speed_penalty = np.where(
        df['Avg_Speed_kmh'] < 20, 3,  # Low speed (congestion)
        np.where(df['Avg_Speed_kmh'] > 60, 1, 0)  # High speed
    )
    
    # Calculate environmental risk score
    df['Environmental_Risk'] = (df['PM2_5_Level'] / 10) + speed_penalty
    df['Environmental_Risk'] = df['Environmental_Risk'].round(2)
    
    print(f"  Risk score range: {df['Environmental_Risk'].min():.2f} - {df['Environmental_Risk'].max():.2f}")
    print(f"  Average risk: {df['Environmental_Risk'].mean():.2f}")
    
    return df


def feature_time_components(df):
    """
    Feature 3 & 4: Extract Day_Of_Week and Hour_Of_Day
    """
    print("\n[FEATURE] Extracting time components...")
    
    df['Day_Of_Week'] = df['Timestamp'].dt.day_name()
    df['Hour_Of_Day'] = df['Timestamp'].dt.hour
    
    print("  Created: Day_Of_Week, Hour_Of_Day")
    
    return df


def feature_congestion_level(df):
    """
    Feature 5: Congestion_Level (categorical)
    Based on speed: Free Flow, Light, Moderate, Heavy, Severe
    """
    print("\n[FEATURE] Creating Congestion_Level...")
    
    def categorize_congestion(speed):
        if speed >= 80:
            return 'Free Flow'
        elif speed >= 60:
            return 'Light'
        elif speed >= 40:
            return 'Moderate'
        elif speed >= 20:
            return 'Heavy'
        else:
            return 'Severe'
    
    df['Congestion_Level'] = df['Avg_Speed_kmh'].apply(categorize_congestion)
    
    print("  Congestion distribution:")
    print(df['Congestion_Level'].value_counts().to_string())
    
    return df


def feature_aqi_category(df):
    """
    Feature 6: AQI_Category
    Based on PM2.5: Good, Moderate, Unhealthy for Sensitive, Unhealthy, Very Unhealthy, Hazardous
    """
    print("\n[FEATURE] Creating AQI_Category...")
    
    def categorize_aqi(pm25):
        if pm25 <= 12:
            return 'Good'
        elif pm25 <= 35.4:
            return 'Moderate'
        elif pm25 <= 55.4:
            return 'Unhealthy for Sensitive'
        elif pm25 <= 150.4:
            return 'Unhealthy'
        elif pm25 <= 250.4:
            return 'Very Unhealthy'
        else:
            return 'Hazardous'
    
    df['AQI_Category'] = df['PM2_5_Level'].apply(categorize_aqi)
    
    print("  AQI distribution:")
    print(df['AQI_Category'].value_counts().to_string())
    
    return df


def final_cleanup(df):
    """Final cleanup and column ordering."""
    print("\n[CLEANUP] Final ordering...")
    
    # Desired column order
    column_order = [
        'Timestamp',
        'City_Zone',
        'Day_Of_Week',
        'Hour_Of_Day',
        'Is_Rush_Hour',
        'Avg_Speed_kmh',
        'Congestion_Level',
        'PM2_5_Level',
        'AQI_Category',
        'Delay_Minutes',
        'Weather',
        'Environmental_Risk'
    ]
    
    df = df[column_order]
    df = df.sort_values('Timestamp').reset_index(drop=True)
    
    print(f"  Final columns: {list(df.columns)}")
    
    return df


def save_data(df):
    """Save the final merged and feature-engineered data."""
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved Clean_Master_Data.csv: {len(df):,} rows")


def generate_summary(df):
    """Generate final summary."""
    print("\n" + "=" * 70)
    print("MERGE & FEATURE ENGINEERING COMPLETE")
    print("=" * 70)
    print(f"Total rows: {len(df):,}")
    print(f"Total columns: {len(df.columns)}")
    print("\nColumn Data Types:")
    print(df.dtypes.to_string())
    print("\n" + "=" * 70)
    print("\nSample of final data:")
    print(df.head(10).to_string())


def main():
    print("=" * 70)
    print("DATA MERGER & FEATURE ENGINEERING")
    print("=" * 70)
    
    # Load all cleaned data
    dataframes = load_cleaned_data()
    
    # Merge data streams
    df = merge_data(dataframes)
    
    # Feature Engineering
    df = feature_is_rush_hour(df)
    df = feature_environmental_risk(df)
    df = feature_time_components(df)
    df = feature_congestion_level(df)
    df = feature_aqi_category(df)
    
    # Final cleanup
    df = final_cleanup(df)
    
    # Save
    save_data(df)
    
    # Summary
    generate_summary(df)


if __name__ == "__main__":
    main()
