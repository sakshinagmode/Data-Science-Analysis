"""
MEMBER 1: Traffic Data Cleaning Script
========================================
Source: Smart Traffic Camera Network (STCN-v2)
Input: raw_sources/source_traffic_raw.csv
Output: cleaned_data/traffic_cleaned.csv

Cleaning Steps:
1. Deduplication - Remove duplicate (Timestamp, Zone) pairs
2. Outlier Handling - Remove/cap impossible values (9999, negative)
3. OCR Error Removal - Filter out string error messages
4. Type Conversion - Convert to numeric
5. Standardization - Ensure consistent units (km/h)
"""

import pandas as pd
import numpy as np
import os

# --- Configuration ---
INPUT_FILE = "../raw_sources/source_traffic_raw.csv"
OUTPUT_DIR = "../cleaned_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "traffic_cleaned.csv")

# Speed constraints (km/h)
MIN_SPEED = 0
MAX_SPEED = 200  # Maximum realistic speed


def load_data():
    """Load raw traffic data."""
    print("Loading raw traffic data...")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df):,} rows")
    return df


def step1_deduplication(df):
    """Step 1: Remove duplicate (Timestamp, Zone) pairs."""
    print("\n[STEP 1] Deduplication")
    print(f"  Before: {len(df):,} rows")
    
    # Keep first occurrence of duplicate timestamp-zone pairs
    df = df.drop_duplicates(subset=['Timestamp', 'City_Zone'], keep='first')
    
    print(f"  After: {len(df):,} rows")
    print(f"  Removed: {len(df) - len(df):,} duplicates")
    return df


def step2_ocr_error_removal(df):
    """Step 2: Remove OCR error strings."""
    print("\n[STEP 2] OCR Error Removal")
    
    # Known OCR error strings
    ocr_errors = ['Camera_Err', 'Maintenance', 'GLARE_FAULT', 'OCR_FAIL', 'Sensor_Offline']
    
    before_count = len(df)
    
    # Filter out rows where speed is an OCR error string
    df = df[~df['Avg_Speed_kmh'].astype(str).isin(ocr_errors)]
    
    print(f"  Removed {before_count - len(df):,} OCR error rows")
    return df


def step3_type_conversion(df):
    """Step 3: Convert speed column to numeric."""
    print("\n[STEP 3] Type Conversion")
    
    # Convert to numeric, coercing errors to NaN
    df['Avg_Speed_kmh'] = pd.to_numeric(df['Avg_Speed_kmh'], errors='coerce')
    
    # Count NaN values introduced
    nan_count = df['Avg_Speed_kmh'].isna().sum()
    print(f"  Converted to numeric. NaN values: {nan_count:,}")
    
    return df


def step4_outlier_handling(df):
    """Step 4: Handle outliers (9999, negative values)."""
    print("\n[STEP 4] Outlier Handling")
    
    before_count = len(df)
    
    # Remove negative speeds
    negative_mask = df['Avg_Speed_kmh'] < MIN_SPEED
    negative_count = negative_mask.sum()
    
    # Remove extreme outliers (9999 and above MAX_SPEED)
    outlier_mask = df['Avg_Speed_kmh'] > MAX_SPEED
    outlier_count = outlier_mask.sum()
    
    # Remove NaN values
    nan_mask = df['Avg_Speed_kmh'].isna()
    nan_count = nan_mask.sum()
    
    # Apply filters
    df = df[~(negative_mask | outlier_mask | nan_mask)]
    
    print(f"  Removed {negative_count:,} negative values")
    print(f"  Removed {outlier_count:,} extreme outliers (>{MAX_SPEED} km/h)")
    print(f"  Removed {nan_count:,} NaN values")
    print(f"  After: {len(df):,} rows")
    
    return df


def step5_standardization(df):
    """Step 5: Standardize data format."""
    print("\n[STEP 5] Standardization")
    
    # Round speed to 2 decimal places
    df['Avg_Speed_kmh'] = df['Avg_Speed_kmh'].round(2)
    
    # Ensure timestamp is datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Sort by timestamp
    df = df.sort_values('Timestamp').reset_index(drop=True)
    
    print("  Rounded speeds to 2 decimal places")
    print("  Converted timestamps to datetime")
    print("  Sorted by timestamp")
    
    return df


def save_data(df):
    """Save cleaned data to CSV."""
    # Create output directory if needed
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved cleaned data to: {OUTPUT_FILE}")


def generate_summary(original_count, final_count):
    """Generate cleaning summary."""
    print("\n" + "=" * 60)
    print("CLEANING SUMMARY - MEMBER 1 (Traffic)")
    print("=" * 60)
    print(f"Original rows:  {original_count:,}")
    print(f"Final rows:     {final_count:,}")
    print(f"Rows removed:   {original_count - final_count:,}")
    print(f"Retention rate: {(final_count / original_count * 100):.2f}%")
    print("=" * 60)


def main():
    print("=" * 60)
    print("MEMBER 1: TRAFFIC DATA CLEANING")
    print("=" * 60)
    
    # Load data
    df = load_data()
    original_count = len(df)
    
    # Apply cleaning steps
    df = step1_deduplication(df)
    df = step2_ocr_error_removal(df)
    df = step3_type_conversion(df)
    df = step4_outlier_handling(df)
    df = step5_standardization(df)
    
    # Save cleaned data
    save_data(df)
    
    # Generate summary
    generate_summary(original_count, len(df))
    
    # Show sample
    print("\nSample of cleaned data:")
    print(df.head(10).to_string())


if __name__ == "__main__":
    main()
