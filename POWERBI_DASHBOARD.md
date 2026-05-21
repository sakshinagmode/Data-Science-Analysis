# PowerBI Dashboard Documentation

## Data Import

1. Open **PowerBI Desktop**
2. Click **Home** → **Get Data** → **Text/CSV**
3. Select `Clean_Master_Data.csv` → Click **Load**

---

## Dashboard Pages Overview

### Page 1: Executive Summary
High-level city health overview with key performance indicators.

| Visual | Data Field | Purpose |
|--------|-----------|---------|
| Card | Average PM2.5 Level | City-wide air quality index |
| Card | Sum of Delay Minutes | Total transit delays |
| Card | Average Speed | Overall traffic flow health |
| Gauge | Environmental Risk | Risk indicator (0-55 scale) |
| Slicer | City Zone | Filter by geographic area |
| Slicer | Day of Week | Filter by day |

---

### Page 2: Traffic Analytics
Spatial and temporal analysis of traffic patterns across zones.

| Visual | Data Fields | Purpose |
|--------|-------------|---------|
| Clustered Bar Chart | Congestion Level, Count | Distribution of congestion severity |
| Line Chart | Hour of Day, Avg Speed | Hourly traffic flow patterns |
| Matrix | Zone × Congestion Level | Cross-tabulation of zone performance |
| Map (optional) | Zone, Speed, AQI | Geographic hotspot visualization |

---

### Page 3: Environmental Analysis
Air quality trends and correlation with traffic conditions.

| Visual | Data Fields | Purpose |
|--------|-------------|---------|
| Area Chart | Hour of Day, PM2.5 | Daily pollution patterns |
| Pie Chart | AQI Category | Distribution of air quality levels |
| Scatter Chart | Speed vs PM2.5, Weather | Correlation analysis |
| Card | Hazardous Count | Critical air quality events |

---

### Page 4: Trend Analysis
Time-series analysis with interactive filtering.

| Visual | Data Fields | Purpose |
|--------|-------------|---------|
| Line Chart | Date, PM2.5, Speed | Long-term trend comparison |
| Slicer | Day of Week | Day filter |
| Slicer | Weather | Weather condition filter |
| Slicer | Is Rush Hour | Rush hour toggle |

---
