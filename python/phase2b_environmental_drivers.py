"""
Phase 2b: Environmental Drivers of Foraging Behaviour
Grey-headed Albatross Foraging Ecology Project

Downloads monthly SST and chlorophyll-a for the study region via direct
ERDDAP HTTP (no OPeNDAP), matches each GPS point to the nearest satellite
observation, then fits a Random Forest to test whether ocean conditions
predict foraging behaviour.

Outputs:
    data/environmental/sst_2013.nc       — downloaded SST grid (local)
    data/environmental/chla_2013.nc      — downloaded chlorophyll grid (local)
    data/processed/tracks_with_env.csv   — GPS data + sst, chla columns
    outputs/figures/phase2b_drivers.png  — feature importance + SST plots
"""

import time as time_module
import pandas as pd
import numpy as np
import xarray as xr
import requests
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# --- Portfolio colours (light theme) ---
MAUVE     = "#B794D9"
GREEN     = "#7FAD87"
WARM_RED  = "#D9947F"
TEAL      = "#9BC4CB"
MID_GREY  = "#AAAAAA"
DARK_TEXT = "#1a1a1a"

print("\n" + "=" * 70)
print("PHASE 2b: ENVIRONMENTAL DRIVERS OF FORAGING BEHAVIOUR")
print("=" * 70)


# ============================================================================
# PART 1: LOAD TRACK DATA AND DEFINE SPATIAL/TEMPORAL BOUNDS
# ============================================================================

print("\nLoading track data...")

df = pd.read_csv('data/processed/tracks_with_behaviour.csv',
                 parse_dates=['timestamp'])

lat_min = df['location-lat'].min() - 2.0
lat_max = df['location-lat'].max() + 2.0
lon_min = -180.0   # birds cross dateline — full longitude range required
lon_max =  180.0
time_min = df['timestamp'].min()
time_max = df['timestamp'].max()

print(f"  GPS points:   {len(df):,}")
print(f"  Latitude:     {lat_min:.1f} to {lat_max:.1f}")
print(f"  Longitude:    {lon_min} to {lon_max} (full range — dateline crossing)")
print(f"  Time:         {time_min.date()} to {time_max.date()}")


# ============================================================================
# PART 2: DOWNLOAD ENVIRONMENTAL DATA VIA DIRECT ERDDAP HTTP
# ============================================================================
#
# We use ERDDAP's griddap .nc endpoint directly with value-based bracket
# syntax: var[(time_start):time_stride:(time_end)][(lat_min):spatial_stride:(lat_max)]
# This is a plain HTTP download — no OPeNDAP/DAP2 protocol involved.
# The spatial stride subsamples the grid server-side, so only a small file
# is transferred despite the datasets being global at high resolution.
#
# SST:  jplMURSST41mday — NASA JPL MUR monthly, 0.01°, 2002-present
#        variable 'sst', units Kelvin (converted to Celsius after download)
# Chla: pmlEsaCCI60OceanColorMonthly — ESA CCI monthly, ~0.04°, long record
#        variable 'chlor_a', units mg/m³

SST_URL  = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41mday"
CHLA_URL = "https://coastwatch.pfeg.noaa.gov/erddap/griddap/pmlEsaCCI60OceanColorMonthly"

# Spatial stride — index steps, not degrees.
# At 0.01°/point: stride=10 → ~0.1° resolution (fine enough for GPS matching)
# At ~0.04°/point: stride=3  → ~0.12° resolution
SST_STRIDE  = 10
CHLA_STRIDE = 3

sst_path  = Path('data/environmental/sst_2013.nc')
chla_path = Path('data/environmental/chla_2013.nc')


def erddap_download(base_url, var_name, time_min, time_max,
                    lat_min, lat_max, lon_min, lon_max,
                    time_stride, spatial_stride, out_path):
    """
    Download a variable from ERDDAP griddap as a netCDF file using
    value-based bracket syntax for time/lat/lon bounds and index-based
    stride for spatial subsampling. Streams the response with progress.

    Args:
        base_url:        ERDDAP griddap base URL (no file extension)
        var_name:        Variable name in the dataset
        time_min/max:    Temporal bounds (pandas Timestamps)
        lat/lon min/max: Spatial bounds (degrees)
        time_stride:     Time index stride (1 = every time step)
        spatial_stride:  Spatial index stride (10 = every 10th grid cell)
        out_path:        Local path to save the .nc file
    """
    t0 = pd.Timestamp(time_min).strftime('%Y-%m-%dT%H:%M:%SZ')
    t1 = pd.Timestamp(time_max).strftime('%Y-%m-%dT%H:%M:%SZ')

    url = (
        f"{base_url}.nc?{var_name}"
        f"[({t0}):{time_stride}:({t1})]"
        f"[({lat_min:.4f}):{spatial_stride}:({lat_max:.4f})]"
        f"[({lon_min:.4f}):{spatial_stride}:({lon_max:.4f})]"
    )

    print(f"\n  Dataset:  {base_url.split('/')[-1]}")
    print(f"  Variable: {var_name}")
    print(f"  URL:      {url}")
    print(f"  Sending request to ERDDAP server...")

    start = time_module.time()

    try:
        response = requests.get(url, timeout=600, stream=True)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"\n  ✗ HTTP error: {e}")
        print(f"  Response text (first 500 chars): {response.text[:500]}")
        raise

    total_bytes = 0
    last_print  = start

    with open(out_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024 * 256):  # 256KB chunks
            f.write(chunk)
            total_bytes += len(chunk)
            now = time_module.time()
            if now - last_print >= 2.0:
                elapsed = now - start
                speed   = total_bytes / elapsed / 1e6
                print(f"    ... {total_bytes / 1e6:.1f} MB received "
                      f"({elapsed:.0f}s, {speed:.1f} MB/s)")
                last_print = now

    elapsed = time_module.time() - start
    print(f"  ✓ Done: {total_bytes / 1e6:.1f} MB in {elapsed:.0f}s → {out_path}")


# Download SST — skip if already downloaded from a previous run
if sst_path.exists():
    print(f"\nSST file already exists, skipping download: {sst_path}")
else:
    print("\nDownloading SST...")
    erddap_download(SST_URL, 'sst', time_min, time_max,
                    lat_min, lat_max, lon_min, lon_max,
                    time_stride=1, spatial_stride=SST_STRIDE,
                    out_path=sst_path)

# Download chlorophyll — skip if already downloaded
if chla_path.exists():
    print(f"\nChlorophyll file already exists, skipping download: {chla_path}")
else:
    print("\nDownloading chlorophyll...")
    erddap_download(CHLA_URL, 'chlor_a', time_min, time_max,
                    lat_min, lat_max, lon_min, lon_max,
                    time_stride=1, spatial_stride=CHLA_STRIDE,
                    out_path=chla_path)


# ============================================================================
# PART 3: OPEN LOCAL GRIDS AND MATCH TO GPS POINTS
# ============================================================================

print("\nOpening local environmental grids...")

sst_ds  = xr.open_dataset(sst_path)
chla_ds = xr.open_dataset(chla_path)

print(f"  SST  — dims: {dict(sst_ds.sizes)}, "
      f"vars: {list(sst_ds.data_vars)}")
print(f"  Chla — dims: {dict(chla_ds.sizes)}, "
      f"vars: {list(chla_ds.data_vars)}")

# Identify lat/lon dimension names (varies by dataset)
def dim_names(ds):
    lat = 'latitude' if 'latitude' in ds.dims else 'lat'
    lon = 'longitude' if 'longitude' in ds.dims else 'lon'
    return lat, lon

sst_lat,  sst_lon  = dim_names(sst_ds)
chla_lat, chla_lon = dim_names(chla_ds)

print(f"\nMatching {len(df):,} GPS points to nearest satellite observation...")
print("  (This takes a few minutes — progress printed every 10,000 points)")


def match_env(row, data_array, lat_dim, lon_dim, idx):
    """
    For a single GPS point, select the nearest grid cell in space and the
    nearest time step in the satellite composite. Returns the scalar value
    or NaN if the lookup fails (e.g. cloud-masked or out of range).
    """
    if idx % 10000 == 0:
        print(f"    ... {idx:,} / {len(df):,} "
              f"({idx / len(df) * 100:.0f}%)")
    try:
        val = data_array.sel(
            time=row['timestamp'],
            **{lat_dim: row['location-lat'],
               lon_dim: row['location-long']},
            method='nearest'
        ).values
        val = np.squeeze(val)
        return float(val) if not np.isnan(val) else np.nan
    except Exception:
        return np.nan


# Reset index so we can use integer position for progress counting
df = df.reset_index(drop=True)

df['sst'] = [
    match_env(df.iloc[i], sst_ds['sst'], sst_lat, sst_lon, i)
    for i in range(len(df))
]

df['chla'] = [
    match_env(df.iloc[i], chla_ds['chlor_a'], chla_lat, chla_lon, i)
    for i in range(len(df))
]

n_sst  = df['sst'].notna().sum()
n_chla = df['chla'].notna().sum()

print(f"\n  SST matched:  {n_sst:,} / {len(df):,} ({n_sst/len(df)*100:.1f}%)")
print(f"  Chla matched: {n_chla:,} / {len(df):,} ({n_chla/len(df)*100:.1f}%)")

if n_sst < len(df) * 0.5:
    print("  ⚠ WARNING: < 50% SST matches — check grid dimensions printed above")
if n_chla < len(df) * 0.5:
    print("  ⚠ WARNING: < 50% chlorophyll matches — check grid dimensions above")


# ============================================================================
# PART 4: RANDOM FOREST — DOES ENVIRONMENT PREDICT FORAGING?
# ============================================================================

print("\nFitting Random Forest classifier...")

model_df = df.dropna(subset=['sst', 'chla']).copy()
model_df['is_foraging'] = (model_df['behaviour'] == 1).astype(int)

feature_cols = ['sst', 'chla', 'location-lat', 'location-long',
                'dist_from_campbell']
X = model_df[feature_cols]
y = model_df['is_foraging']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)
rf.fit(X_train, y_train)

train_acc = rf.score(X_train, y_train)
test_acc  = rf.score(X_test,  y_test)

print(f"  Train accuracy: {train_acc:.3f}")
print(f"  Test accuracy:  {test_acc:.3f}")
print()
print(classification_report(y_test, rf.predict(X_test),
                             target_names=['Not foraging', 'Foraging']))

importances = pd.Series(
    rf.feature_importances_, index=feature_cols
).sort_values(ascending=True)

print("  Feature importances:")
for feat, imp in importances.items():
    print(f"    {feat:25s}: {imp:.3f}")


# ============================================================================
# PART 5: VISUALISATIONS
# ============================================================================

print("\nGenerating visualisations...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), facecolor='white')

# --- Feature importance ---
ax1.set_facecolor('white')
ax1.barh(importances.index, importances.values, color=MAUVE, alpha=0.85)
ax1.set_xlabel('Feature Importance (Mean Decrease in Impurity)',
               fontsize=11, color=DARK_TEXT)
ax1.set_title('What Predicts Foraging Behaviour?', fontsize=13,
              fontweight='bold', color=DARK_TEXT, pad=12)
ax1.tick_params(colors=DARK_TEXT)
ax1.grid(True, alpha=0.2, color=MID_GREY, axis='x')
for spine in ax1.spines.values():
    spine.set_color(MID_GREY)

# --- SST distribution: foraging vs not ---
ax2.set_facecolor('white')
ax2.hist(model_df.loc[model_df['is_foraging'] == 0, 'sst'],
         bins=40, alpha=0.6, color=MID_GREY, label='Not foraging',
         density=True)
ax2.hist(model_df.loc[model_df['is_foraging'] == 1, 'sst'],
         bins=40, alpha=0.6, color=GREEN, label='Foraging', density=True)
ax2.set_xlabel('Sea Surface Temperature (°C)', fontsize=11, color=DARK_TEXT)
ax2.set_ylabel('Density', fontsize=11, color=DARK_TEXT)
ax2.set_title('SST at Foraging vs Non-Foraging Locations',
              fontsize=13, fontweight='bold', color=DARK_TEXT, pad=12)
ax2.legend(fontsize=10, frameon=False)
ax2.tick_params(colors=DARK_TEXT)
ax2.grid(True, alpha=0.2, color=MID_GREY, axis='y')
for spine in ax2.spines.values():
    spine.set_color(MID_GREY)

fig.text(
    0.5, -0.02,
    "Data: Torres et al. 2017 (Movebank) · NASA JPL MUR SST · ESA CCI Ocean Colour · "
    "Analysis: D. Crompton — dtcrompton.github.io",
    ha='center', fontsize=8, color=MID_GREY, style='italic'
)

plt.tight_layout()
plt.savefig('outputs/figures/phase2b_drivers.png', dpi=150,
            bbox_inches='tight', facecolor='white')
print("  ✓ Saved: outputs/figures/phase2b_drivers.png")
plt.close()


# ============================================================================
# PART 6: SAVE OUTPUTS
# ============================================================================

print("\nSaving processed data...")
df.to_csv('data/processed/tracks_with_env.csv', index=False)
print("  ✓ Saved: data/processed/tracks_with_env.csv")


# ============================================================================
# PART 7: SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("PHASE 2b SUMMARY")
print("=" * 70)

forage    = model_df['is_foraging'] == 1
not_forage= model_df['is_foraging'] == 0

print(f"""
  Points with full environmental data: {len(model_df):,} / {len(df):,}

  Random Forest performance:
    Train accuracy: {train_acc:.3f}
    Test accuracy:  {test_acc:.3f}

  Top predictor: {importances.index[-1]} ({importances.values[-1]:.3f})

  Mean SST  — foraging:     {model_df.loc[forage,     'sst'].mean():.2f} °C
  Mean SST  — not foraging: {model_df.loc[not_forage, 'sst'].mean():.2f} °C
  Mean Chla — foraging:     {model_df.loc[forage,     'chla'].mean():.4f} mg/m³
  Mean Chla — not foraging: {model_df.loc[not_forage, 'chla'].mean():.4f} mg/m³
""")

print("=" * 70)
print("PHASE 2b COMPLETE")
print("=" * 70 + "\n")