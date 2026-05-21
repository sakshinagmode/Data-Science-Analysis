"""
MEMBER 4: Weather Data Cleaning Script
========================================
Source: OpenMeteo External Feed
Input: raw_sources/source_weather_raw.csv
Output: cleaned_data/weather_cleaned.csv

Cleaning Steps:
1. Deduplication - Remove duplicate (Timestamp, Zone) pairs
2. HTML Tag Removal - Strip scraping artifacts
3. Special Character Cleaning - Remove encoding issues
4. Synonym Standardization - Map all variants to standard terms
5. Case Standardization - Lowercase all weather values
6. Validation - Ensure only valid weather categories
"""

import pandas as pd
import numpy as np
import re
import os

# --- Configuration ---
INPUT_FILE = "../raw_sources/source_weather_raw.csv"
OUTPUT_DIR = "../cleaned_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "weather_cleaned.csv")

# Standard weather categories (lowercase)
VALID_WEATHER = ['sunny', 'rainy', 'cloudy', 'stormy', 'windy', 'foggy', 'clear', 'overcast']

# Synonym mapping
WEATHER_SYNONYMS = {
    # Sunny variants
    'sunny': 'sunny',
    'bright': 'sunny',
    'mostly sunny': 'sunny',
    'sun?ny': 'sunny',
    
    # Rainy variants
    'rainy': 'rainy',
    'rain': 'rainy',
    'rain_heavy': 'rainy',
    'drizzle': 'rainy',
    'light rain': 'rainy',
    'precipitation': 'rainy',
    'wet': 'rainy',
    'heavy rain': 'rainy',
    'downpour': 'rainy',
    
    # Cloudy variants
    'cloudy': 'cloudy',
    'partly cloudy': 'cloudy',
    'partly_cloudy': 'cloudy',
    
    # Stormy variants
    'stormy': 'stormy',
    'storm': 'stormy',
    'storm*warning': 'stormy',
    'thunderstorm': 'stormy',
    
    # Windy variants
    'windy': 'windy',
    'wind%strong': 'windy',
    
    # Foggy variants
    'foggy': 'foggy',
    'fog': 'foggy',
    'fog+mist': 'foggy',
    'mist': 'foggy',
    'hazy': 'foggy',
    'smoggy': 'foggy',
    
    # Clear variants
    'clear': 'clear',
    'clear//skies': 'clear',
    
    # Overcast
    'overcast': 'overcast',
}


def load_data():
    """Load raw weather data."""
    print("Loading raw weather data...")
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


def step2_html_removal(df):
    """Step 2: Remove HTML tags from scraping artifacts."""
    print("\n[STEP 2] HTML Tag Removal")
    
    def remove_html(text):
        if pd.isna(text):
            return text
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', str(text))
        # Remove HTML entities
        clean = re.sub(r'&nbsp;', '', clean)
        clean = re.sub(r'&\w+;', '', clean)
        return clean.strip()
    
    df['Weather'] = df['Weather'].apply(remove_html)
    print("  Removed HTML tags and entities")
    
    return df


def step3_special_char_cleaning(df):
    """Step 3: Remove special characters and encoding issues."""
    print("\n[STEP 3] Special Character Cleaning")
    
    def clean_special_chars(text):
        if pd.isna(text):
            return text
        text = str(text)
        # Replace underscores with spaces
        text = text.replace('_', ' ')
        # Replace special chars with nothing
        text = re.sub(r'[?*/%+]', '', text)
        # Remove extra spaces
        text = ' '.join(text.split())
        return text.strip()
    
    df['Weather'] = df['Weather'].apply(clean_special_chars)
    print("  Cleaned special characters")
    
    return df


def step4_lowercase(df):
    """Step 4: Convert all weather values to lowercase."""
    print("\n[STEP 4] Case Standardization")
    
    df['Weather'] = df['Weather'].str.lower().str.strip()
    print("  Converted all values to lowercase")
    
    return df


def step5_synonym_standardization(df):
    """Step 5: Map synonyms to standard weather terms."""
    print("\n[STEP 5] Synonym Standardization")
    
    def standardize_weather(weather):
        if pd.isna(weather) or weather == '':
            return np.nan
        
        weather_clean = str(weather).lower().strip()
        
        # Direct match in synonym map
        if weather_clean in WEATHER_SYNONYMS:
            return WEATHER_SYNONYMS[weather_clean]
        
        # Partial match (e.g., "rainy" in "light rainy")
        for synonym, standard in WEATHER_SYNONYMS.items():
            if synonym in weather_clean or weather_clean in synonym:
                return standard
        
        # Check if it's already a valid weather type
        if weather_clean in VALID_WEATHER:
            return weather_clean
        
        return np.nan  # Unknown weather type
    
    before_nan = df['Weather'].isna().sum()
    df['Weather'] = df['Weather'].apply(standardize_weather)
    after_nan = df['Weather'].isna().sum()
    
    print(f"  Standardized weather terms")
    print(f"  New unmapped values: {after_nan - before_nan:,}")
    
    return df


def step6_validation_and_imputation(df):
    """Step 6: Validate and impute missing weather values."""
    print("\n[STEP 6] Validation & Imputation")
    
    nan_count = df['Weather'].isna().sum()
    print(f"  Missing values before imputation: {nan_count:,}")
    
    # Forward fill within each zone
    df = df.sort_values(['City_Zone', 'Timestamp'])
    df['Weather'] = df.groupby('City_Zone')['Weather'].ffill()
    
    # Backward fill for any remaining
    df['Weather'] = df.groupby('City_Zone')['Weather'].bfill()
    
    # Final fallback: most common weather
    if df['Weather'].isna().any():
        mode_weather = df['Weather'].mode()[0]
        df['Weather'] = df['Weather'].fillna(mode_weather)
        print(f"  Used mode ({mode_weather}) for remaining NaN")
    
    after_nan = df['Weather'].isna().sum()
    print(f"  Missing values after: {after_nan:,}")
    
    return df


def step7_final_standardization(df):
    """Step 7: Final cleanup and standardization."""
    print("\n[STEP 7] Final Standardization")
    
    # Ensure timestamp is datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Sort by timestamp
    df = df.sort_values('Timestamp').reset_index(drop=True)
    
    # Verify only valid weather types
    valid_count = df['Weather'].isin(VALID_WEATHER).sum()
    print(f"  Valid weather entries: {valid_count:,} / {len(df):,}")
    
    return df


def save_data(df):
    """Save cleaned data to CSV."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved cleaned data to: {OUTPUT_FILE}")


def generate_summary(original_count, final_count, df):
    """Generate cleaning summary."""
    print("\n" + "=" * 60)
    print("CLEANING SUMMARY - MEMBER 4 (Weather)")
    print("=" * 60)
    print(f"Original rows:  {original_count:,}")
    print(f"Final rows:     {final_count:,}")
    print(f"Retention rate: {(final_count / original_count * 100):.2f}%")
    print("\nWeather Distribution:")
    print(df['Weather'].value_counts().to_string())
    print("=" * 60)


def main():
    print("=" * 60)
    print("MEMBER 4: WEATHER DATA CLEANING")
    print("=" * 60)
    
    df = load_data()
    original_count = len(df)
    
    df = step1_deduplication(df)
    df = step2_html_removal(df)
    df = step3_special_char_cleaning(df)
    df = step4_lowercase(df)
    df = step5_synonym_standardization(df)
    df = step6_validation_and_imputation(df)
    df = step7_final_standardization(df)
    
    save_data(df)
    generate_summary(original_count, len(df), df)
    
    print("\nSample of cleaned data:")
    print(df.head(10).to_string())


if __name__ == "__main__":
    main()
