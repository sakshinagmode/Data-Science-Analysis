"""
MEMBER 2: Air Quality Data Cleaning Script
============================================
Source: IoT Sensor Grid (Project GreenAir)
Input: raw_sources/source_aqi_raw.csv
Output: cleaned_data/aqi_cleaned.csv

Cleaning Steps:
1. Deduplication - Remove duplicate (Timestamp, Zone) pairs
2. Error String Removal - Filter out connection/device errors
3. Missing Value Imputation - Forward fill + Mean imputation
4. Outlier Handling - Cap extreme values
5. Type Conversion & Standardization
"""

import pandas as pd
import numpy as np
import os

# --- Configuration ---
INPUT_FILE = "../raw_sources/source_aqi_raw.csv"
OUTPUT_DIR = "../cleaned_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "aqi_cleaned.csv")

# PM2.5 constraints (µg/m³)
MIN_PM25 = 0
MAX_PM25 = 500  # WHO hazardous level cap


def load_data():
    """Load raw AQI data."""
    print("Loading raw AQI data...")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df):,} rows")
    return df


def step1_deduplication(df):
    """Step 1: Remove duplicate (Timestamp, Zone) pairs."""
    print("\n[STEP 1] Deduplication")
    before_count = len(df)
    
    df = df.drop_duplicates(subset=['Timestamp', 'City_Zone'], keep='first')
    
    print(f"  Removed {before_count - len(df):,} duplicates")
    print(f"  Remaining: {len(df):,} rows")
    return df


def step2_error_string_removal(df):
    """Step 2: Remove connection/device error strings."""
    print("\n[STEP 2] Error String Removal")
    
    # Known error strings
    error_strings = [
        'Connection_Lost_Retry_3', 'TIMEOUT_ERR', 'NO_SIGNAL',
        'DEVICE_OFFLINE', 'BATTERY_LOW_SHUTDOWN', 'TBD', 'N/A',
        'PENDING', '-', 'None', ''
    ]
    
    before_count = len(df)
    
    # Replace error strings with NaN
    df['PM2_5_Level'] = df['PM2_5_Level'].replace(error_strings, np.nan)
    
    # Also handle string "nan"
    df['PM2_5_Level'] = df['PM2_5_Level'].replace('nan', np.nan)
    
    error_count = df['PM2_5_Level'].isna().sum()
    print(f"  Marked {error_count:,} error values as NaN")
    
    return df


def step3_type_conversion(df):
    """Step 3: Convert to numeric."""
    print("\n[STEP 3] Type Conversion")
    
    df['PM2_5_Level'] = pd.to_numeric(df['PM2_5_Level'], errors='coerce')
    
    nan_count = df['PM2_5_Level'].isna().sum()
    print(f"  Converted to numeric. Total NaN: {nan_count:,}")
    
    return df


def step4_outlier_handling(df):
    """Step 4: Handle outliers (negative and extreme values)."""
    print("\n[STEP 4] Outlier Handling")
    
    # Mark negative values as NaN
    negative_mask = df['PM2_5_Level'] < MIN_PM25
    negative_count = negative_mask.sum()
    df.loc[negative_mask, 'PM2_5_Level'] = np.nan
    
    # Cap extreme outliers at MAX_PM25 (instead of removing)
    extreme_mask = df['PM2_5_Level'] > MAX_PM25
    extreme_count = extreme_mask.sum()
    df.loc[extreme_mask, 'PM2_5_Level'] = MAX_PM25
    
    print(f"  Marked {negative_count:,} negative values as NaN")
    print(f"  Capped {extreme_count:,} extreme values at {MAX_PM25}")
    
    return df


def step5_imputation(df):
    """Step 5: Impute missing values using Forward Fill + Zone Mean."""
    print("\n[STEP 5] Missing Value Imputation")
    
    before_nan = df['PM2_5_Level'].isna().sum()
    print(f"  Missing values before imputation: {before_nan:,}")
    
    # Sort by timestamp first
    df = df.sort_values(['City_Zone', 'Timestamp'])
    
    # Forward fill within each zone
    df['PM2_5_Level'] = df.groupby('City_Zone')['PM2_5_Level'].ffill()
    
    after_ffill = df['PM2_5_Level'].isna().sum()
    print(f"  After forward fill: {after_ffill:,} remaining NaN")
    
    # Fill remaining with zone mean
    zone_means = df.groupby('City_Zone')['PM2_5_Level'].transform('mean')
    df['PM2_5_Level'] = df['PM2_5_Level'].fillna(zone_means)
    
    after_mean = df['PM2_5_Level'].isna().sum()
    print(f"  After zone mean fill: {after_mean:,} remaining NaN")
    
    # Final fallback: global mean
    if after_mean > 0:
        global_mean = df['PM2_5_Level'].mean()
        df['PM2_5_Level'] = df['PM2_5_Level'].fillna(global_mean)
        print(f"  Used global mean ({global_mean:.2f}) for remaining NaN")
    
    return df


def step6_standardization(df):
    """Step 6: Final standardization."""
    print("\n[STEP 6] Standardization")
    
    # Round to 2 decimal places
    df['PM2_5_Level'] = df['PM2_5_Level'].round(2)
    
    # Ensure timestamp is datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Sort by timestamp
    df = df.sort_values('Timestamp').reset_index(drop=True)
    
    print("  Rounded values to 2 decimal places")
    print("  Sorted by timestamp")
    
    return df


def save_data(df):
    """Save cleaned data to CSV."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved cleaned data to: {OUTPUT_FILE}")


def generate_summary(original_count, final_count):
    """Generate cleaning summary."""
    print("\n" + "=" * 60)
    print("CLEANING SUMMARY - MEMBER 2 (AQI)")
    print("=" * 60)
    print(f"Original rows:  {original_count:,}")
    print(f"Final rows:     {final_count:,}")
    print(f"Retention rate: {(final_count / original_count * 100):.2f}%")
    print("=" * 60)


def main():
    print("=" * 60)
    print("MEMBER 2: AIR QUALITY DATA CLEANING")
    print("=" * 60)
    
    df = load_data()
    original_count = len(df)
    
    df = step1_deduplication(df)
    df = step2_error_string_removal(df)
    df = step3_type_conversion(df)
    df = step4_outlier_handling(df)
    df = step5_imputation(df)
    df = step6_standardization(df)
    
    save_data(df)
    generate_summary(original_count, len(df))
    
    print("\nSample of cleaned data:")
    print(df.head(10).to_string())


if __name__ == "__main__":
    main()
