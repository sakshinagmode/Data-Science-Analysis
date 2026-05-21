"""
Phase 5: Python Visualization Script
=====================================
Member 4's Responsibility (as per project plan)

This script generates statistical visualizations from Clean_Master_Data.csv:
1. Heatmap - Correlation between Traffic Speed and PM2.5 levels
2. Time-Series Plot - Pollution peaks during rush hour
3. Boxplots - Delay distributions across city zones

Output: Saved as PNG files in 'visualizations/' folder
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- Configuration ---
INPUT_FILE = "Clean_Master_Data.csv"
OUTPUT_DIR = "visualizations"

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


def load_data():
    """Load the clean master data."""
    print("Loading Clean_Master_Data.csv...")
    df = pd.read_csv(INPUT_FILE)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    print(f"Loaded {len(df):,} rows")
    return df


def plot_correlation_heatmap(df):
    """
    Plot 1: Correlation Heatmap
    Shows correlation between numeric variables including Traffic Speed and PM2.5
    """
    print("\n[PLOT 1] Creating Correlation Heatmap...")
    
    # Select numeric columns
    numeric_cols = ['Avg_Speed_kmh', 'PM2_5_Level', 'Delay_Minutes', 
                    'Environmental_Risk', 'Hour_Of_Day']
    
    # Calculate correlation matrix
    corr_matrix = df[numeric_cols].corr()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create heatmap
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt='.2f',
        cmap='RdYlBu_r',
        center=0,
        square=True,
        linewidths=0.5,
        ax=ax,
        vmin=-1,
        vmax=1
    )
    
    plt.title('Correlation Matrix: Urban Mobility Metrics', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save
    filepath = os.path.join(OUTPUT_DIR, '01_correlation_heatmap.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {filepath}")
    return corr_matrix


def plot_traffic_aqi_scatter(df):
    """
    Plot 2: Traffic Speed vs PM2.5 Scatter Plot with Weather hue
    """
    print("\n[PLOT 2] Creating Traffic vs AQI Scatter Plot...")
    
    # Sample data for performance (full data is too dense)
    sample = df.sample(n=min(50000, len(df)), random_state=42)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    scatter = sns.scatterplot(
        data=sample,
        x='Avg_Speed_kmh',
        y='PM2_5_Level',
        hue='Weather',
        alpha=0.5,
        s=20,
        ax=ax
    )
    
    plt.xlabel('Average Speed (km/h)', fontsize=12)
    plt.ylabel('PM2.5 Level (µg/m³)', fontsize=12)
    plt.title('Traffic Speed vs Air Quality by Weather Condition', fontsize=14, fontweight='bold')
    plt.legend(title='Weather', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    
    filepath = os.path.join(OUTPUT_DIR, '02_traffic_vs_aqi_scatter.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {filepath}")


def plot_rush_hour_pollution(df):
    """
    Plot 3: Time-Series - Pollution by Hour showing Rush Hour peaks
    """
    print("\n[PLOT 3] Creating Rush Hour Pollution Time-Series...")
    
    # Aggregate by hour
    hourly_stats = df.groupby('Hour_Of_Day').agg({
        'PM2_5_Level': 'mean',
        'Avg_Speed_kmh': 'mean',
        'Delay_Minutes': 'mean'
    }).reset_index()
    
    fig, ax1 = plt.subplots(figsize=(14, 7))
    
    # PM2.5 line
    color1 = '#e74c3c'
    ax1.set_xlabel('Hour of Day', fontsize=12)
    ax1.set_ylabel('PM2.5 Level (µg/m³)', color=color1, fontsize=12)
    line1 = ax1.plot(hourly_stats['Hour_Of_Day'], hourly_stats['PM2_5_Level'], 
                     color=color1, linewidth=2.5, marker='o', label='PM2.5 Level')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_xticks(range(0, 24))
    
    # Add rush hour shading
    ax1.axvspan(8, 10, alpha=0.2, color='orange', label='Morning Rush')
    ax1.axvspan(17, 19, alpha=0.2, color='purple', label='Evening Rush')
    
    # Secondary axis for speed
    ax2 = ax1.twinx()
    color2 = '#3498db'
    ax2.set_ylabel('Average Speed (km/h)', color=color2, fontsize=12)
    line2 = ax2.plot(hourly_stats['Hour_Of_Day'], hourly_stats['Avg_Speed_kmh'], 
                     color=color2, linewidth=2.5, marker='s', linestyle='--', label='Avg Speed')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Combined legend
    lines = line1 + line2
    labels = ['PM2.5 Level', 'Avg Speed']
    ax1.legend(lines, labels, loc='upper right')
    
    plt.title('Hourly Pollution and Traffic Patterns (Rush Hour Highlighted)', 
              fontsize=14, fontweight='bold')
    fig.tight_layout()
    
    filepath = os.path.join(OUTPUT_DIR, '03_rush_hour_pollution.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {filepath}")


def plot_zone_delay_boxplot(df):
    """
    Plot 4: Boxplot - Delay distributions across city zones
    """
    print("\n[PLOT 4] Creating Zone Delay Boxplot...")
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Create boxplot
    zone_order = df.groupby('City_Zone')['Delay_Minutes'].median().sort_values(ascending=False).index
    
    sns.boxplot(
        data=df,
        x='City_Zone',
        y='Delay_Minutes',
        order=zone_order,
        palette='Set2',
        ax=ax
    )
    
    plt.xlabel('City Zone', fontsize=12)
    plt.ylabel('Delay (Minutes)', fontsize=12)
    plt.title('Bus Delay Distribution by City Zone', fontsize=14, fontweight='bold')
    plt.xticks(rotation=15)
    plt.tight_layout()
    
    filepath = os.path.join(OUTPUT_DIR, '04_zone_delay_boxplot.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {filepath}")


def plot_congestion_by_weather(df):
    """
    Plot 5: Stacked Bar - Congestion levels by weather
    """
    print("\n[PLOT 5] Creating Weather vs Congestion Stacked Bar...")
    
    # Create crosstab
    ct = pd.crosstab(df['Weather'], df['Congestion_Level'], normalize='index') * 100
    
    # Reorder congestion levels
    level_order = ['Free Flow', 'Light', 'Moderate', 'Heavy', 'Severe']
    ct = ct[[col for col in level_order if col in ct.columns]]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ct.plot(kind='bar', stacked=True, ax=ax, colormap='RdYlGn_r', edgecolor='white')
    
    plt.xlabel('Weather Condition', fontsize=12)
    plt.ylabel('Percentage (%)', fontsize=12)
    plt.title('Congestion Level Distribution by Weather', fontsize=14, fontweight='bold')
    plt.legend(title='Congestion Level', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.xticks(rotation=0)
    plt.tight_layout()
    
    filepath = os.path.join(OUTPUT_DIR, '05_weather_congestion_bar.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {filepath}")


def plot_environmental_risk_histogram(df):
    """
    Plot 6: Histogram - Environmental Risk Score Distribution
    """
    print("\n[PLOT 6] Creating Environmental Risk Histogram...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sns.histplot(
        data=df,
        x='Environmental_Risk',
        hue='Is_Rush_Hour',
        bins=50,
        alpha=0.6,
        ax=ax
    )
    
    plt.xlabel('Environmental Risk Score', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.title('Environmental Risk Distribution: Rush Hour vs Non-Rush Hour', 
              fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    filepath = os.path.join(OUTPUT_DIR, '06_environmental_risk_histogram.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {filepath}")


def plot_day_of_week_heatmap(df):
    """
    Plot 7: Heatmap - Average metrics by Day of Week and Hour
    """
    print("\n[PLOT 7] Creating Day-Hour Heatmap...")
    
    # Order days properly
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Create pivot table
    pivot = df.pivot_table(
        values='PM2_5_Level',
        index='Day_Of_Week',
        columns='Hour_Of_Day',
        aggfunc='mean'
    ).reindex(day_order)
    
    fig, ax = plt.subplots(figsize=(16, 6))
    
    sns.heatmap(
        pivot,
        cmap='YlOrRd',
        annot=False,
        ax=ax,
        cbar_kws={'label': 'PM2.5 Level'}
    )
    
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('Day of Week', fontsize=12)
    plt.title('Average PM2.5 Levels by Day and Hour', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    filepath = os.path.join(OUTPUT_DIR, '07_day_hour_heatmap.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {filepath}")


def main():
    print("=" * 70)
    print("PHASE 5: PYTHON VISUALIZATION")
    print("=" * 70)
    
    # Create output directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")
    
    # Load data
    df = load_data()
    
    # Generate all plots
    plot_correlation_heatmap(df)
    plot_traffic_aqi_scatter(df)
    plot_rush_hour_pollution(df)
    plot_zone_delay_boxplot(df)
    plot_congestion_by_weather(df)
    plot_environmental_risk_histogram(df)
    plot_day_of_week_heatmap(df)
    
    print("\n" + "=" * 70)
    print("VISUALIZATION COMPLETE!")
    print(f"All plots saved to: {OUTPUT_DIR}/")
    print("=" * 70)
    
    # List generated files
    print("\nGenerated files:")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        print(f"  - {f}")


if __name__ == "__main__":
    main()
