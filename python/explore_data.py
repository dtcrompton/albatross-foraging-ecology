"""
Phase 1: Grey-headed Albatross Data Exploration
Inspect Movebank GPS tracking data structure and basic statistics
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("\n" + "="*70)
print("Loading albatross tracking data...")
print("="*70)

# Load data
df = pd.read_csv('data/raw/Grey-headed albatross, New Zealand (data from Torres et al. 2017).csv')

print("\n" + "="*70)
print("DATASET OVERVIEW")
print("="*70)

# Basic info
print(f"\nTotal records: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print(f"\nColumn names:")
for col in df.columns:
    print(f"  - {col}")

# Display first few rows
print("\n" + "="*70)
print("FIRST 5 RECORDS")
print("="*70)
print(df.head())

# Check data types
print("\n" + "="*70)
print("DATA TYPES")
print("="*70)
print(df.dtypes)

# Missing values
print("\n" + "="*70)
print("MISSING VALUES")
print("="*70)
missing = df.isnull().sum()
missing_pct = (missing / len(df)) * 100
missing_df = pd.DataFrame({
    'Missing': missing,
    'Percent': missing_pct
}).sort_values('Missing', ascending=False)
print(missing_df[missing_df['Missing'] > 0])

# Individual birds
if 'individual-local-identifier' in df.columns:
    print("\n" + "="*70)
    print("INDIVIDUAL BIRDS")
    print("="*70)
    
    individuals = df['individual-local-identifier'].unique()
    print(f"\nTotal individuals tracked: {len(individuals)}")
    
    # Points per individual
    points_per_bird = df.groupby('individual-local-identifier').size().sort_values(ascending=False)
    print(f"\nPoints per bird (top 10):")
    print(points_per_bird.head(10))
    
    print(f"\nMean points per bird: {points_per_bird.mean():.0f}")
    print(f"Median points per bird: {points_per_bird.median():.0f}")
    print(f"Max points (single bird): {points_per_bird.max():,}")
    print(f"Min points (single bird): {points_per_bird.min():,}")

# Temporal coverage
if 'timestamp' in df.columns:
    print("\n" + "="*70)
    print("TEMPORAL COVERAGE")
    print("="*70)
    
    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print(f"\nFirst record: {df['timestamp'].min()}")
    print(f"Last record: {df['timestamp'].max()}")
    print(f"Duration: {(df['timestamp'].max() - df['timestamp'].min()).days} days")
    
    # Records per year
    df['year'] = df['timestamp'].dt.year
    records_per_year = df.groupby('year').size()
    print(f"\nRecords per year:")
    print(records_per_year)

# Spatial extent
if 'location-long' in df.columns and 'location-lat' in df.columns:
    print("\n" + "="*70)
    print("SPATIAL EXTENT")
    print("="*70)
    
    print(f"\nLongitude range: {df['location-long'].min():.2f}° to {df['location-long'].max():.2f}°")
    print(f"Latitude range: {df['location-lat'].min():.2f}° to {df['location-lat'].max():.2f}°")
    
    # Campbell Island location (breeding site)
    campbell_lat = -52.55
    campbell_lon = 169.15
    
    print(f"\nCampbell Island (breeding site): {campbell_lat}°, {campbell_lon}°")
    
    # Calculate max distance from Campbell Island
    from math import radians, sin, cos, sqrt, atan2
    
    def haversine(lon1, lat1, lon2, lat2):
        """Calculate distance between two points on Earth (km)"""
        R = 6371  # Earth radius in km
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    # Calculate distances from Campbell Island
    df['dist_from_campbell'] = df.apply(
        lambda row: haversine(campbell_lon, campbell_lat, 
                             row['location-long'], row['location-lat']), 
        axis=1
    )
    
    print(f"\nMax distance from Campbell Island: {df['dist_from_campbell'].max():.0f} km")
    print(f"Mean distance from Campbell Island: {df['dist_from_campbell'].mean():.0f} km")

print("\n" + "="*70)
print("EXPLORATION COMPLETE")
print("="*70)
print("\nReady for Phase 2: Visualisation and spatial analysis\n")