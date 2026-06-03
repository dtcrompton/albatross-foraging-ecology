"""
Phase 1: Movement Metrics & Trip Segmentation
Grey-headed Albatross Foraging Ecology Project

Calculates step length, speed, bearing, and turning angle for each GPS point,
segments tracks into foraging trips, and produces overview visualisations.

Outputs:
    data/processed/tracks_with_metrics.csv  — full GPS data with calculated metrics
    data/processed/trip_statistics.csv      — summary statistics per trip
    outputs/figures/phase1_overview.png     — 4-panel summary figure
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import radians, sin, cos, sqrt, atan2, pi

plt.style.use('dark_background')

print("\n" + "=" * 70)
print("PHASE 1: MOVEMENT METRICS & TRIP SEGMENTATION")
print("=" * 70)


# ============================================================================
# PART 1: LOAD AND PREPARE DATA
# ============================================================================

print("\nLoading data...")

df = pd.read_csv('data/raw/albatross_tracks.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values(['individual-local-identifier', 'timestamp']).reset_index(drop=True)

print(f"Loaded {len(df):,} GPS points from "
      f"{df['individual-local-identifier'].nunique()} birds")


# ============================================================================
# PART 2: DISTANCE AND SPEED FUNCTIONS
# ============================================================================

def haversine(lon1, lat1, lon2, lat2):
    """
    Great-circle distance between two points on Earth (km).
    Accounts for Earth's curvature using the haversine formula.
    Returns 0.0 if any coordinate is NaN.
    """
    if any(pd.isna(v) for v in [lon1, lat1, lon2, lat2]):
        return 0.0
    R = 6371
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def calculate_bearing(lon1, lat1, lon2, lat2):
    """
    Compass bearing (radians, -pi to pi) from point 1 to point 2.
    Returns NaN if any coordinate is missing.
    """
    if any(pd.isna(v) for v in [lon1, lat1, lon2, lat2]):
        return np.nan
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    return atan2(x, y)


def turning_angle(bearing_in, bearing_out):
    """
    Signed turning angle (radians) between incoming and outgoing bearings.
    Normalised to [-pi, pi]:
        near 0   = straight line (transit behaviour)
        near +/-pi = U-turn (area-restricted search / foraging)
    Returns NaN if either bearing is missing.
    """
    if pd.isna(bearing_in) or pd.isna(bearing_out):
        return np.nan
    angle = bearing_out - bearing_in
    return (angle + pi) % (2 * pi) - pi


# ============================================================================
# PART 3: CALCULATE MOVEMENT METRICS
# ============================================================================

print("\nCalculating movement metrics...")

# Campbell Island breeding colony coordinates
CAMPBELL_LON = 169.15
CAMPBELL_LAT = -52.55

# --- Distance from colony ---
df['dist_from_campbell'] = df.apply(
    lambda r: haversine(CAMPBELL_LON, CAMPBELL_LAT,
                        r['location-long'], r['location-lat']),
    axis=1
)

# --- Previous and next point coordinates (within same bird) ---
grp = df.groupby('individual-local-identifier')

df['prev_lat'] = grp['location-lat'].shift(1)
df['prev_lon'] = grp['location-long'].shift(1)
df['next_lat'] = grp['location-lat'].shift(-1)    # ← NEW
df['next_lon'] = grp['location-long'].shift(-1)   # ← NEW

# --- Step length: distance moved since previous point ---
df['step_length_km'] = df.apply(
    lambda r: haversine(r['prev_lon'], r['prev_lat'],
                        r['location-long'], r['location-lat']),
    axis=1
)

# --- Time elapsed since previous point (hours) ---
df['prev_timestamp'] = grp['timestamp'].shift(1)
df['time_elapsed_h'] = (
    (df['timestamp'] - df['prev_timestamp']).dt.total_seconds() / 3600
)

# --- Speed (km/h) ---
df['speed_kmh'] = np.where(
    df['time_elapsed_h'] > 0,
    df['step_length_km'] / df['time_elapsed_h'],
    np.nan
)

# --- Incoming bearing: direction from previous point to current point ---  # ← NEW
df['bearing_in'] = df.apply(
    lambda r: calculate_bearing(r['prev_lon'], r['prev_lat'],
                                r['location-long'], r['location-lat']),
    axis=1
)

# --- Outgoing bearing: direction from current point to next point ---       # ← NEW
df['bearing_out'] = df.apply(
    lambda r: calculate_bearing(r['location-long'], r['location-lat'],
                                r['next_lon'], r['next_lat']),
    axis=1
)

# --- Turning angle at each point ---                                        # ← NEW
df['turning_angle_rad'] = df.apply(
    lambda r: turning_angle(r['bearing_in'], r['bearing_out']),
    axis=1
)

# Absolute turning angle (0 to pi) — used as HMM feature in Phase 2         # ← NEW
df['abs_turning_angle'] = df['turning_angle_rad'].abs()

# Drop intermediate columns no longer needed
df = df.drop(columns=['prev_lat', 'prev_lon', 'next_lat', 'next_lon',
                       'prev_timestamp', 'bearing_in', 'bearing_out'])

print(f"  Average speed:          {df['speed_kmh'].mean():.1f} km/h")
print(f"  Max speed:              {df['speed_kmh'].max():.1f} km/h")
print(f"  Mean step length:       {df['step_length_km'].mean():.1f} km")
print(f"  Mean abs turning angle: "
      f"{np.degrees(df['abs_turning_angle'].mean()):.1f}°")


# ============================================================================
# PART 4: TRIP SEGMENTATION
# ============================================================================

print("\nSegmenting foraging trips...")

COLONY_THRESHOLD_KM = 50

df['at_colony'] = df['dist_from_campbell'] <= COLONY_THRESHOLD_KM

# Detect each crossing of the colony boundary within each bird's track
df['trip_boundary'] = (
    df.groupby('individual-local-identifier')['at_colony']
    .transform(lambda x: (x != x.shift()).astype(int))
)

df['trip_id'] = df.groupby('individual-local-identifier')['trip_boundary'].cumsum()

foraging_pts = df[~df['at_colony']].copy()

print(f"  Colony threshold:   {COLONY_THRESHOLD_KM} km")
print(f"  Points at colony:   {df['at_colony'].sum():,}")
print(f"  Points foraging:    {len(foraging_pts):,}")


# ============================================================================
# PART 5: TRIP STATISTICS
# ============================================================================

print("\nCalculating trip statistics...")

trip_stats = (
    foraging_pts
    .groupby(['individual-local-identifier', 'trip_id'])
    .agg(
        start_time      = ('timestamp',          'min'),
        end_time        = ('timestamp',          'max'),
        max_dist_km     = ('dist_from_campbell', 'max'),
        total_dist_km   = ('step_length_km',     'sum'),
        mean_speed_kmh  = ('speed_kmh',          'mean'),
        n_points        = ('location-lat',       'count'),
    )
    .reset_index()
)

trip_stats.columns.name = None
trip_stats.rename(columns={'individual-local-identifier': 'bird_id'},
                  inplace=True)

trip_stats['duration_days'] = (
    (trip_stats['end_time'] - trip_stats['start_time'])
    .dt.total_seconds() / 86400
)

trip_stats['month'] = trip_stats['start_time'].dt.month

# Filter out sub-day excursions (measurement noise)
trip_stats = trip_stats[trip_stats['duration_days'] >= 1].reset_index(drop=True)

print(f"  Trips lasting 1+ days:      {len(trip_stats)}")
print(f"  Average trip duration:      {trip_stats['duration_days'].mean():.1f} days")
print(f"  Longest trip:               {trip_stats['duration_days'].max():.1f} days")
print(f"  Average max distance:       {trip_stats['max_dist_km'].mean():.0f} km")
print(f"  Farthest point from colony: {trip_stats['max_dist_km'].max():.0f} km")


# ============================================================================
# PART 6: VISUALISATIONS
# ============================================================================

print("\nGenerating visualisations...")

fig = plt.figure(figsize=(20, 12))
fig.suptitle('Grey-headed Albatross — Phase 1 Overview',
             fontsize=18, fontweight='bold', y=1.01)

PURPLE = '#B794D9'
GREEN  = '#7FAD87'
SALMON = '#e8a899'

# --- Subplot 1: All tracks map ---
ax1 = fig.add_subplot(2, 2, 1)
colours = plt.cm.tab20(np.linspace(0, 1, df['individual-local-identifier'].nunique()))

for i, bird_id in enumerate(df['individual-local-identifier'].unique()):
    bird_data = df[df['individual-local-identifier'] == bird_id]
    ax1.plot(bird_data['location-long'], bird_data['location-lat'],
             alpha=0.5, linewidth=0.4, color=colours[i])

ax1.scatter(CAMPBELL_LON, CAMPBELL_LAT, c='red', s=200,
            marker='*', edgecolors='white', linewidths=1.5,
            label='Campbell Island', zorder=5)
ax1.set_xlabel('Longitude (°E)', fontsize=11)
ax1.set_ylabel('Latitude (°S)', fontsize=11)
ax1.set_title('All 24 Bird Tracks', fontsize=13, fontweight='bold')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.2)

# --- Subplot 2: Distance from colony over time (3 example birds) ---
ax2 = fig.add_subplot(2, 2, 2)
example_birds = df['individual-local-identifier'].unique()[:3]
colours_3 = [PURPLE, GREEN, SALMON]

for bird_id, col in zip(example_birds, colours_3):
    bird_data = df[df['individual-local-identifier'] == bird_id]
    ax2.plot(bird_data['timestamp'], bird_data['dist_from_campbell'],
             alpha=0.8, linewidth=0.8, color=col, label=f'Bird {bird_id}')

ax2.axhline(y=COLONY_THRESHOLD_KM, color='red', linestyle='--',
            linewidth=1.5, label=f'Colony boundary ({COLONY_THRESHOLD_KM} km)')
ax2.set_xlabel('Date (2013)', fontsize=11)
ax2.set_ylabel('Distance from Campbell Island (km)', fontsize=11)
ax2.set_title('Distance from Colony Over Time (3 Birds)', fontsize=13, fontweight='bold')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.2)

# --- Subplot 3: Trip duration histogram ---
ax3 = fig.add_subplot(2, 2, 3)
ax3.hist(trip_stats['duration_days'], bins=20,
         color=GREEN, edgecolor='white', alpha=0.85)
ax3.axvline(x=trip_stats['duration_days'].mean(), color=PURPLE,
            linestyle='--', linewidth=2,
            label=f"Mean: {trip_stats['duration_days'].mean():.1f} days")
ax3.set_xlabel('Trip Duration (days)', fontsize=11)
ax3.set_ylabel('Number of Trips', fontsize=11)
ax3.set_title('Foraging Trip Duration Distribution', fontsize=13, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.2, axis='y')

# --- Subplot 4: Monthly trip departures ---
ax4 = fig.add_subplot(2, 2, 4)
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
trips_per_month = trip_stats['month'].value_counts().sort_index()

ax4.bar(trips_per_month.index, trips_per_month.values,
        color=PURPLE, edgecolor='white', alpha=0.85)
ax4.set_xlabel('Month (2013)', fontsize=11)
ax4.set_ylabel('Trip Departures', fontsize=11)
ax4.set_title('When Do Foraging Trips Begin?', fontsize=13, fontweight='bold')
ax4.set_xticks(trips_per_month.index)
ax4.set_xticklabels([month_names[m - 1] for m in trips_per_month.index],
                    rotation=45)
ax4.grid(True, alpha=0.2, axis='y')

plt.tight_layout()
plt.savefig('outputs/figures/phase1_overview.png', dpi=150, bbox_inches='tight')
print("  ✓ Saved: outputs/figures/phase1_overview.png")


# ============================================================================
# PART 7: SAVE PROCESSED DATA
# ============================================================================

print("\nSaving processed data...")

df.to_csv('data/processed/tracks_with_metrics.csv', index=False)
print("  ✓ Saved: data/processed/tracks_with_metrics.csv")

trip_stats.to_csv('data/processed/trip_statistics.csv', index=False)
print("  ✓ Saved: data/processed/trip_statistics.csv")


# ============================================================================
# PART 8: SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("PHASE 1 SUMMARY")
print("=" * 70)

print(f"""
  GPS points:           {len(df):,}
  Birds tracked:        {df['individual-local-identifier'].nunique()}
  Study period:         {df['timestamp'].min().date()} → {df['timestamp'].max().date()}
  Duration:             {(df['timestamp'].max() - df['timestamp'].min()).days} days

  Avg speed:            {df['speed_kmh'].mean():.1f} km/h
  Max distance:         {df['dist_from_campbell'].max():.0f} km from Campbell Island

  Foraging trips:       {len(trip_stats)}
  Avg trip duration:    {trip_stats['duration_days'].mean():.1f} days
  Longest trip:         {trip_stats['duration_days'].max():.1f} days

  Turning angle data:   ✓ (ready for HMM in Phase 2)
""")

print("=" * 70)
print("PHASE 1 COMPLETE")
print("=" * 70)