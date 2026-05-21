# Urban Mobility Analytics Project

## Overview
This project analyzes urban mobility data from Metro City to understand traffic patterns, air quality correlations, public transit efficiency, and environmental factors affecting city movement.

---

## Data Sources

| Source | Provider | Data Type |
|--------|----------|-----------|
| **Traffic Flow** | Metro City Highways Department - Smart Traffic Camera Network (STCN-v2) | Vehicle speed, congestion levels |
| **Air Quality** | Environment Agency - IoT Sensor Grid (Project GreenAir) | PM2.5 particulate matter readings |
| **Public Transit** | Metro Transit Authority - Fleet Telemetry System | Bus delay reporting |
| **Weather** | OpenMeteo API & Government Meteorological Department | Weather conditions |

**Data Period:** January 2025 - December 2025  
**Geographic Coverage:** 5 City Zones (Downtown, Industrial Hub, Suburb North, Suburb South, Airport Road)

---

## Project Structure

```
CODE/
├── master_data_creator.py      # Data extraction script
├── urban_mobility_raw.csv      # Raw collected data
├── split_data.py               # Data splitting utility
├── raw_sources/                # Split source files
│   ├── source_traffic_raw.csv
│   ├── source_aqi_raw.csv
│   ├── source_transit_raw.csv
│   └── source_weather_raw.csv
├── cleaning_scripts/           # Team cleaning scripts
│   ├── member1_traffic_cleaning.py
│   ├── member2_aqi_cleaning.py
│   ├── member3_transit_cleaning.py
│   └── member4_weather_cleaning.py
├── cleaned_data/               # Processed clean data
├── merge_and_engineer.py       # Feature engineering
├── Clean_Master_Data.csv       # Final analysis-ready dataset
├── visualize_data.py           # Python visualizations
├── visualizations/             # Generated charts
└── POWERBI_DASHBOARD.md        # Dashboard documentation
```

---

## Quick Start

### 1. Data Cleaning
```bash
cd cleaning_scripts
python member1_traffic_cleaning.py
python member2_aqi_cleaning.py
python member3_transit_cleaning.py
python member4_weather_cleaning.py
```

### 2. Merge & Feature Engineering
```bash
python merge_and_engineer.py
```

### 3. Generate Visualizations
```bash
python visualize_data.py
```

---

## Final Dataset Columns

| Column | Description |
|--------|-------------|
| `Timestamp` | Date and time of observation |
| `City_Zone` | Geographic zone within the city |
| `Day_Of_Week` | Day name (Monday-Sunday) |
| `Hour_Of_Day` | Hour (0-23) |
| `Is_Rush_Hour` | True if 08:00-10:00 or 17:00-19:00 |
| `Avg_Speed_kmh` | Average traffic speed |
| `Congestion_Level` | Free Flow / Light / Moderate / Heavy / Severe |
| `PM2_5_Level` | Air quality particulate reading |
| `AQI_Category` | Good / Moderate / Unhealthy / Hazardous |
| `Delay_Minutes` | Bus delay in minutes |
| `Weather` | Weather condition |
| `Environmental_Risk` | Composite risk score |

---

## Team Responsibilities

| Member | Data Domain | Script | PowerBI Page |
|--------|-------------|--------|--------------|
| 1 | Traffic | `member1_traffic_cleaning.py` | Traffic Analytics |
| 2 | Air Quality | `member2_aqi_cleaning.py` | Environmental |
| 3 | Transit | `member3_transit_cleaning.py` | Trend Analysis |
| 4 | Weather | `member4_weather_cleaning.py` | Executive Summary |

---

## Requirements

- Python 3.8+
- pandas
- numpy
- matplotlib
- seaborn
- PowerBI Desktop (for dashboard)

---

## Power BI Dashboard (4 Pages)

| Page | Member | Charts |
|------|--------|--------|
| **Traffic Analytics** | Sanskruti | Speed trend lines by zone, congestion level donut, speed by hour bar |
| **Environmental** | Sakshi | PM2.5 gauge by zone, AQI category pie, pollution vs weather scatter |
| **Trend Analysis** | Digvijay | Bus delay trend over months, delay by day-of-week, zone comparison table |
| **Executive Summary** | Shrey | KPI cards (avg speed, avg PM2.5, avg delay), weather distribution, all-zones overview |

---
> *In **Phase 3**, we generated 7 Python charts and built a 4-page Power BI dashboard.*
>
> *Our key finding: PM2.5 pollution peaks during rush hours (8–10 AM, 5–7 PM), and stormy weather significantly increases both congestion and bus delays."*
