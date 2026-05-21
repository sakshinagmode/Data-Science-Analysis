"""
MEMBER 3: Transit Data Cleaning Script
========================================
Source: Bus Fleet Telemetry API (Legacy)
Input: raw_sources/source_transit_raw.csv
Output: cleaned_data/transit_cleaned.csv

Cleaning Steps:
1. Deduplication - Remove duplicate (Timestamp, Zone) pairs
2. JSON Parsing - Extract delay minutes from JSON strings
3. Text Parsing - Extract numbers from SMS-style text
4. Unit Standardization - Convert all to minutes
5. Type Conversion - Ensure numeric Delay_Minutes column
6. Outlier Handling - Cap extreme delays
"""

import pandas as pd
import numpy as np
import re
import json
import os

# --- Configuration ---
INPUT_FILE = "../raw_sources/source_transit_raw.csv"
OUTPUT_DIR = "../cleaned_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "transit_cleaned.csv")

MAX_DELAY_MINUTES = 120  # Maximum realistic delay


def load_data():
    """Load raw transit data."""
    print("Loading raw transit data...")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df):,} rows")
    return df


def step1_deduplication(df):
    """Step 1: Remove duplicate (Timestamp, Zone) pairs."""
    print("\n[STEP 1] Deduplication")
    before_count = len(df)
    
    df = df.drop_duplicates(subset=['Timestamp', 'City_Zone'], keep='first')
    
    print(f"  Removed {before_count - len(df):,} duplicates")
    return df


def parse_delay_value(value):
    """
    Parse delay value from various formats:
    - Integer: 5 -> 5
    - JSON: {"status": "late", "min": 5} -> 5
    - Duration strings: "5 min", "5m", "300s" -> 5
    - SMS texts: "Late by 5 ish" -> 5
    - Status texts: "On Time" -> 0, "Major Delay" -> 30 (default)
    """
    if pd.isna(value):
        return np.nan
    
    # Convert to string for processing
    val_str = str(value).strip()
    
    # Handle pure integers/floats
    try:
        num = float(val_str)
        return num if num >= 0 else np.nan
    except ValueError:
        pass
    
    # Handle JSON strings
    if val_str.startswith('{'):
        try:
            data = json.loads(val_str)
            if 'min' in data:
                return float(data['min'])
            elif 'delay' in data:
                return float(data['delay'])
        except json.JSONDecodeError:
            pass
    
    # Handle status texts
    val_lower = val_str.lower()
    if val_lower in ['on time', 'ok', 'almost there']:
        return 0
    if val_lower in ['major delay', 'major breakdown on route']:
        return 30  # Default major delay
    if val_lower in ['n/a', '---', 'unknown']:
        return np.nan
    
    # Handle seconds: "300s"
    seconds_match = re.search(r'(\d+)\s*s(?:ec)?', val_str, re.IGNORECASE)
    if seconds_match:
        return float(seconds_match.group(1)) / 60
    
    # Handle minutes: "5 min", "5m", "~5min", "5 minutes"
    minutes_match = re.search(r'(\d+)\s*m(?:in)?', val_str, re.IGNORECASE)
    if minutes_match:
        return float(minutes_match.group(1))
    
    # Handle SMS texts: "Late by 5 ish", "Approx 10 min late"
    number_match = re.search(r'(\d+)', val_str)
    if number_match:
        return float(number_match.group(1))
    
    # Handle generic delay texts (assign default delay)
    if 'delay' in val_lower or 'stuck' in val_lower or 'behind' in val_lower:
        return 15  # Default delay estimate
    
    return np.nan


def step2_parse_delays(df):
    """Step 2: Parse delay values from all formats."""
    print("\n[STEP 2] Parse Delay Values (JSON, SMS, Duration)")
    
    # Create new column with parsed values
    df['Delay_Minutes'] = df['Bus_Delay_Status'].apply(parse_delay_value)
    
    parsed_count = df['Delay_Minutes'].notna().sum()
    print(f"  Successfully parsed {parsed_count:,} delay values")
    print(f"  Failed to parse {len(df) - parsed_count:,} values")
    
    return df


def step3_outlier_handling(df):
    """Step 3: Handle outliers (negative and extreme delays)."""
    print("\n[STEP 3] Outlier Handling")
    
    # Mark negative values as NaN
    negative_mask = df['Delay_Minutes'] < 0
    negative_count = negative_mask.sum()
    df.loc[negative_mask, 'Delay_Minutes'] = np.nan
    
    # Cap extreme delays
    extreme_mask = df['Delay_Minutes'] > MAX_DELAY_MINUTES
    extreme_count = extreme_mask.sum()
    df.loc[extreme_mask, 'Delay_Minutes'] = MAX_DELAY_MINUTES
    
    print(f"  Marked {negative_count:,} negative values as NaN")
    print(f"  Capped {extreme_count:,} extreme values at {MAX_DELAY_MINUTES} min")
    
    return df


def step4_imputation(df):
    """Step 4: Impute missing delay values."""
    print("\n[STEP 4] Missing Value Imputation")
    
    before_nan = df['Delay_Minutes'].isna().sum()
    print(f"  Missing values before: {before_nan:,}")
    
    # Forward fill within each zone
    df = df.sort_values(['City_Zone', 'Timestamp'])
    df['Delay_Minutes'] = df.groupby('City_Zone')['Delay_Minutes'].ffill()
    
    # Fill remaining with zone median
    zone_medians = df.groupby('City_Zone')['Delay_Minutes'].transform('median')
    df['Delay_Minutes'] = df['Delay_Minutes'].fillna(zone_medians)
    
    # Final fallback: global median
    global_median = df['Delay_Minutes'].median()
    df['Delay_Minutes'] = df['Delay_Minutes'].fillna(global_median)
    
    after_nan = df['Delay_Minutes'].isna().sum()
    print(f"  Missing values after: {after_nan:,}")
    
    return df


def step5_standardization(df):
    """Step 5: Final standardization."""
    print("\n[STEP 5] Standardization")
    
    # Round to 1 decimal place
    df['Delay_Minutes'] = df['Delay_Minutes'].round(1)
    
    # Ensure timestamp is datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Drop original messy column
    df = df.drop(columns=['Bus_Delay_Status'])
    
    # Sort by timestamp
    df = df.sort_values('Timestamp').reset_index(drop=True)
    
    print("  Rounded values to 1 decimal place")
    print("  Dropped original Bus_Delay_Status column")
    print("  Created clean Delay_Minutes column")
    
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
    print("CLEANING SUMMARY - MEMBER 3 (Transit)")
    print("=" * 60)
    print(f"Original rows:  {original_count:,}")
    print(f"Final rows:     {final_count:,}")
    print(f"Retention rate: {(final_count / original_count * 100):.2f}%")
    print("=" * 60)


def main():
    print("=" * 60)
    print("MEMBER 3: TRANSIT DATA CLEANING")
    print("=" * 60)
    
    df = load_data()
    original_count = len(df)
    
    df = step1_deduplication(df)
    df = step2_parse_delays(df)
    df = step3_outlier_handling(df)
    df = step4_imputation(df)
    df = step5_standardization(df)
    
    save_data(df)
    generate_summary(original_count, len(df))
    
    print("\nSample of cleaned data:")
    print(df.head(10).to_string())


if __name__ == "__main__":
    main()
