"""
Master Data Creator for Urban Mobility Raw Dataset
===================================================
This script generates a 1-million-row synthetic dataset simulating
data from 4 disconnected, messy legacy and modern systems.

Sources Simulated:
1. Smart Traffic Camera Network (STCN-v2) - Traffic Speed
2. IoT Sensor Grid (Project GreenAir) - Air Quality (PM2.5)
3. Bus Fleet Telemetry API (Legacy) - Transit Delays
4. OpenMeteo External Feed - Weather Conditions

The data is intentionally "raw" and "messy" to provide a realistic
data cleaning challenge for a 4-member team project.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json

# --- Configuration ---
ROWS = 1_000_000
SEED = 42  # For reproducibility
OUTPUT_FILE = "urban_mobility_raw.csv"

ZONES = [
    'Downtown',
    'Industrial_Hub',
    'Suburb_North',
    'Suburb_South',
    'Airport_Road'
]

# Set seeds for reproducibility
random.seed(SEED)
np.random.seed(SEED)


def generate_timestamps(n: int) -> list:
    """Generate random timestamps within year 2025."""
    start_date = datetime(2025, 1, 1)
    max_minutes = 365 * 24 * 60  # One year in minutes
    return [start_date + timedelta(minutes=random.randint(0, max_minutes)) for _ in range(n)]


def generate_traffic_speed(n: int) -> list:
    """
    Source 1: Smart Traffic Camera Network (STCN-v2)
    
    Errors injected:
    - ~5% OCR Failures: "Camera_Err", "Maintenance", "GLARE_FAULT"
    - ~3% Sensor Glitches: Negative speeds (-1, -5)
    - ~2% Outliers: 9999 (limit error)
    - ~5% Unit Confusion: Values in mph (lower range, 5-75)
    - ~85% Valid: Random float 5-120 km/h
    """
    data = []
    for _ in range(n):
        roll = random.random()
        if roll < 0.05:
            # OCR Failures
            data.append(random.choice(["Camera_Err", "Maintenance", "GLARE_FAULT", "OCR_FAIL", "Sensor_Offline"]))
        elif roll < 0.08:
            # Sensor Glitches (negative)
            data.append(random.choice([-1, -5, -10, -999]))
        elif roll < 0.10:
            # Outliers (9999 limit)
            data.append(9999)
        elif roll < 0.15:
            # Unit confusion (mph logged as kmh)
            data.append(round(random.uniform(5, 75), 1))  # mph range
        else:
            # Valid speed in km/h
            data.append(round(random.uniform(5, 120), 2))
    return data


def generate_pm25_level(n: int) -> list:
    """
    Source 2: IoT Sensor Grid (Project GreenAir)
    
    Errors injected:
    - ~5% Connection Drops: "Connection_Lost_Retry_3", "TIMEOUT", "NO_SIGNAL"
    - ~5% Missing Data: NaN, None, "", "TBD", "N/A"
    - ~3% Calibration Mode: Negative values or near-zero noise
    - ~2% Sensor Drift: Insanely high values (10000+)
    - ~85% Valid: Random float 10-300 (realistic PM2.5 range)
    """
    data = []
    for _ in range(n):
        roll = random.random()
        if roll < 0.05:
            # Connection Drops
            data.append(random.choice([
                "Connection_Lost_Retry_3",
                "TIMEOUT_ERR",
                "NO_SIGNAL",
                "DEVICE_OFFLINE",
                "BATTERY_LOW_SHUTDOWN"
            ]))
        elif roll < 0.10:
            # Missing Data (various representations)
            data.append(random.choice([np.nan, None, "", "TBD", "N/A", "PENDING", "-"]))
        elif roll < 0.13:
            # Calibration Mode (negative or near-zero)
            data.append(random.choice([-0.01, -5.5, 0.00000001, -999]))
        elif roll < 0.15:
            # Sensor Drift (insanely high)
            data.append(random.uniform(10000, 50000))
        else:
            # Valid PM2.5 reading
            data.append(round(random.uniform(10, 300), 2))
    return data


def generate_bus_delay(n: int) -> list:
    """
    Source 3: Bus Fleet Telemetry API (Legacy)
    
    Errors injected:
    - ~10% API Leaks: Raw JSON strings
    - ~10% SMS Parsing: Driver texts like "Late by 5 ish"
    - ~10% Inconsistent Units: "5 min", "5m", "300s"
    - ~5% Encoding Issues: " 5 ", "  10", extra whitespace
    - ~5% Mixed Status: "On Time", "Major Delay", "N/A"
    - ~60% Valid: Integer minutes (0-60)
    """
    data = []
    for _ in range(n):
        roll = random.random()
        if roll < 0.10:
            # API Leaks (JSON strings)
            delay_val = random.randint(0, 30)
            status = random.choice(["late", "delayed", "behind_schedule"])
            data.append(json.dumps({"status": status, "min": delay_val}))
        elif roll < 0.20:
            # SMS Parsing (driver texts)
            data.append(random.choice([
                "Late by 5 ish",
                "Stuck in traffic",
                "Running behind schedule",
                "Approx 10 min late",
                "Delayed due to accident",
                "Heavy traffic, ETA unknown",
                "Almost there",
                "Major breakdown on route"
            ]))
        elif roll < 0.30:
            # Inconsistent Units
            val = random.randint(1, 30)
            data.append(random.choice([
                f"{val} min",
                f"{val}m",
                f"{val * 60}s",
                f"{val} minutes",
                f"~{val}min"
            ]))
        elif roll < 0.35:
            # Encoding Issues (whitespace)
            val = random.randint(0, 20)
            data.append(random.choice([f" {val} ", f"  {val}", f"{val}  ", f"\t{val}"]))
        elif roll < 0.40:
            # Mixed Status (text)
            data.append(random.choice(["On Time", "Major Delay", "N/A", "OK", "UNKNOWN", "---"]))
        else:
            # Valid integer minutes
            data.append(random.randint(0, 60))
    return data


def generate_weather(n: int) -> list:
    """
    Source 4: OpenMeteo External Feed
    
    Errors injected:
    - ~10% Scraping Artifacts: HTML tags
    - ~10% Encoding Hell: Underscores, special chars
    - ~15% Synonyms: Different words for same weather
    - ~15% Case Chaos: Random casing
    - ~50% Valid: Standard weather terms
    """
    base_weather = ["Sunny", "Rainy", "Cloudy", "Stormy", "Windy", "Foggy", "Clear", "Overcast"]
    
    data = []
    for _ in range(n):
        roll = random.random()
        if roll < 0.10:
            # Scraping Artifacts (HTML tags)
            weather = random.choice(base_weather)
            data.append(random.choice([
                f"<b>{weather}</b>",
                f"<span>{weather}</span>",
                f"<div class='weather'>{weather}</div>",
                f"<p>{weather}</p>",
                f"&nbsp;{weather}"
            ]))
        elif roll < 0.20:
            # Encoding Hell
            data.append(random.choice([
                "Sun?ny",
                "Rain_Heavy",
                "Partly_Cloudy",
                "STORM*WARNING",
                "Clear//Skies",
                "Fog+Mist",
                "Wind%Strong"
            ]))
        elif roll < 0.35:
            # Synonyms
            data.append(random.choice([
                "Drizzle", "Light Rain", "Precipitation", "Wet",
                "Partly Cloudy", "Mostly Sunny", "Bright",
                "Thunderstorm", "Heavy Rain", "Downpour",
                "Mist", "Hazy", "Smoggy"
            ]))
        elif roll < 0.50:
            # Case Chaos
            weather = random.choice(base_weather)
            case_variants = [
                weather.lower(),
                weather.upper(),
                weather.swapcase(),
                weather[0].lower() + weather[1:].upper()
            ]
            data.append(random.choice(case_variants))
        else:
            # Valid standard weather
            data.append(random.choice(base_weather))
    return data


def main():
    print(f"Generating {ROWS:,} rows of raw urban mobility data...")
    print(f"Seed: {SEED}")
    print("-" * 50)
    
    # Generate data
    print("Generating timestamps...")
    timestamps = generate_timestamps(ROWS)
    
    print("Generating city zones...")
    zones = [random.choice(ZONES) for _ in range(ROWS)]
    
    print("Generating traffic speed data (Source 1)...")
    traffic_speed = generate_traffic_speed(ROWS)
    
    print("Generating PM2.5 levels (Source 2)...")
    pm25 = generate_pm25_level(ROWS)
    
    print("Generating bus delay data (Source 3)...")
    bus_delay = generate_bus_delay(ROWS)
    
    print("Generating weather data (Source 4)...")
    weather = generate_weather(ROWS)
    
    # Create DataFrame
    print("Creating DataFrame...")
    df = pd.DataFrame({
        'Timestamp': timestamps,
        'City_Zone': zones,
        'Avg_Speed_kmh': traffic_speed,
        'PM2_5_Level': pm25,
        'Bus_Delay_Status': bus_delay,
        'Weather': weather
    })
    
    # Sort by timestamp for realism
    print("Sorting by timestamp...")
    df = df.sort_values('Timestamp').reset_index(drop=True)
    
    # Save to CSV
    print(f"Saving to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False)
    
    # Summary
    print("-" * 50)
    print("DATA GENERATION COMPLETE!")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Total rows: {len(df):,}")
    print(f"Columns: {list(df.columns)}")
    print("\nSample of generated data (first 10 rows):")
    print(df.head(10).to_string())
    print("\nData types:")
    print(df.dtypes)


if __name__ == "__main__":
    main()
