"""
Phase 3: Conservation Risk Analysis
Grey-headed Albatross Foraging Ecology Project

Identifies where and when grey-headed albatrosses from Campbell Island
face highest risk of overlap with longline fishing effort in the
Southern Ocean and New Zealand EEZ.

Key finding from data exploration:
    99.1% of foraging occurs north of 60°S — primarily in New Zealand's
    EEZ and FAO Area 81, not the CCAMLR Convention Area. A complete
    spatial risk analysis requires NZ MPI fisheries data; Phase 3 uses
    CCAMLR data for temporal pattern analysis and KDE/individual
    profiling for the spatial component.

Outputs:
    outputs/figures/phase3_risk_analysis.png  — 4-panel conservation figure
    data/processed/bird_risk_profiles.csv     — per-bird risk metrics
    data/processed/foraging_kde_grid.csv      — KDE density grid
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path
from scipy.stats import gaussian_kde
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- Portfolio colours (light theme) ---
MAUVE     = "#B794D9"
GREEN     = "#7FAD87"
WARM_RED  = "#D9947F"
TEAL      = "#9BC4CB"
MID_GREY  = "#AAAAAA"
DARK_TEXT = "#1a1a1a"

CCAMLR_DIR = Path('data/raw/ccamlr/CCAMLR_statistical bulletin_V37')

print("\n" + "=" * 70)
print("PHASE 3: CONSERVATION RISK ANALYSIS")
print("=" * 70)


# ============================================================================
# PART 1: LOAD DATA
# ============================================================================

print("\nLoading data...")

df       = pd.read_csv('data/processed/tracks_with_env.csv',
                        parse_dates=['timestamp'])
profiles = pd.read_csv('data/processed/bird_profiles.csv')
effort   = pd.read_csv(CCAMLR_DIR / 'Effort.csv')
# Convert anything that can't be parsed as a number to NaN rather than raising an error, so can be treated as string
for col in ['hook_count', 'fishing_days', 'vessel_count',
            'trawl_duration_hours', 'haul_count', 'month', 'year']:
    effort[col] = pd.to_numeric(effort[col], errors='coerce').fillna(0)
gear_df  = pd.read_csv(CCAMLR_DIR / 'FishingGear.csv')

print(f"  GPS points:     {len(df):,}")
print(f"  Birds:          {len(profiles)}")
print(f"  CCAMLR records: {len(effort):,}")

# Add month column to tracks
df['month'] = df['timestamp'].dt.month


# ============================================================================
# PART 2: CCAMLR FISHING EFFORT — EXPLORE AND FILTER
# ============================================================================

print("\nCCAMLR data exploration...")

# All gear types in dataset
print("\n  All gear types in CCAMLR Effort.csv:")
gear_counts = effort['gear_type_code'].value_counts()
for code, count in gear_counts.items():
    gear_name = gear_df.set_index('gear_type_code')['Gear_type'].get(code, 'Unknown')
    print(f"    {code:6s}: {count:6,} records  ({gear_name})")

# Identify hook-and-line/longline gear types
# LLS = set longlines — primary albatross bycatch risk
LONGLINE_CODES = ['LLS', 'LL', 'LP', 'DLL', 'SSL', 'LHP', 'LHM']
longline_present = [c for c in LONGLINE_CODES if c in effort['gear_type_code'].values]
print(f"\n  Longline gear codes present: {longline_present}")

# Filter to 2013 and longline gear
effort_2013 = effort[
    (effort['year'] == 2013) &
    (effort['gear_type_code'].isin(longline_present))
].copy()

print(f"\n  CCAMLR longline effort (2013):")
print(f"    Records:     {len(effort_2013):,}")
print(f"    Total hooks: {effort_2013['hook_count'].sum():,.0f}")
print(f"    Areas:       {effort_2013['asd_code'].nunique()}")

# Monthly effort distribution
monthly_effort = effort_2013.groupby('month').agg(
    hook_count   = ('hook_count',   'sum'),
    fishing_days = ('fishing_days', 'sum'),
    vessel_count = ('vessel_count', 'sum')
).reindex(range(1, 13), fill_value=0)


# ============================================================================
# PART 3: MANAGEMENT ZONE BREAKDOWN
# ============================================================================

print("\nClassifying foraging points by management zone...")

foraging_pts = df[df['behaviour'] == 1].copy()

# Define zones by latitude
# CCAMLR Convention Area: roughly south of 60°S in the Pacific sector
# NZ EEZ: Campbell Island (52.5°S) extends ~200nm = ~3.7° latitude
# High seas: north of NZ EEZ, south of 60°S
CCAMLR_BOUNDARY = -60.0
NZ_EEZ_BOUNDARY = -48.8  # approximate northern extent of NZ subantarctic EEZ

def zone(lat):
    if lat < CCAMLR_BOUNDARY:
        return 'CCAMLR Convention Area'
    elif lat < NZ_EEZ_BOUNDARY:
        return 'NZ EEZ / Subantarctic'
    else:
        return 'High Seas / FAO 81'

foraging_pts['zone'] = foraging_pts['location-lat'].apply(zone)

zone_counts = foraging_pts['zone'].value_counts()
total_forage = len(foraging_pts)

print("\n  Foraging point distribution by management zone:")
for zone_name, count in zone_counts.items():
    print(f"    {zone_name:35s}: {count:6,} ({count/total_forage*100:.1f}%)")


# ============================================================================
# PART 4: KDE FORAGING HOTSPOT ANALYSIS
# ============================================================================

print("\nCalculating foraging hotspot KDE...")

# Convert longitudes to 0–360 range to avoid dateline split
# Campbell Island at 169°E stays at 169°
# South American foraging region at ~-100° to -60° becomes 260°–300°
forage_lon_360 = foraging_pts['location-long'].values % 360
forage_lat     = foraging_pts['location-lat'].values

# Fit KDE on foraging points
kde = gaussian_kde(
    np.vstack([forage_lon_360, forage_lat]),
    bw_method = 'scott'  # automatic bandwidth selection
)

# Evaluate on regular grid covering the study region
# 100°E (100) to 300°E (= 60°W) — covers Campbell Island to South America
lon_grid = np.linspace(100, 310, 300)
lat_grid = np.linspace(-65, -40, 150)
LON_MESH, LAT_MESH = np.meshgrid(lon_grid, lat_grid)

print("  Evaluating KDE on grid (takes ~30 seconds)...")
ZZ = kde(np.vstack([LON_MESH.ravel(), LAT_MESH.ravel()])).reshape(LON_MESH.shape)

# Identify peak hotspot location
peak_idx = np.unravel_index(ZZ.argmax(), ZZ.shape)
peak_lon_360 = lon_grid[peak_idx[1]]
peak_lat     = lat_grid[peak_idx[0]]
# Convert back to ±180 for display
peak_lon = peak_lon_360 if peak_lon_360 <= 180 else peak_lon_360 - 360

lon_dir = 'E' if peak_lon >= 0 else 'W'
print(f"  Peak foraging hotspot: {peak_lat:.1f}°S, {abs(peak_lon):.1f}°{lon_dir}")

# Save KDE grid for later use (artwork)
kde_df = pd.DataFrame({
    'longitude_360': LON_MESH.ravel(),
    'latitude':      LAT_MESH.ravel(),
    'kde_density':   ZZ.ravel()
})
kde_df.to_csv('data/processed/foraging_kde_grid.csv', index=False)
print("  ✓ Saved: data/processed/foraging_kde_grid.csv")


# ============================================================================
# PART 5: TEMPORAL RISK ANALYSIS
# ============================================================================

print("\nTemporal risk analysis...")

# Monthly foraging activity — all birds combined
monthly_foraging = foraging_pts.groupby('month').size().reindex(
    range(1, 13), fill_value=0
)

# Temporal synchrony: in each month, are fishing effort and
# foraging activity occurring simultaneously?
# Normalise both series to 0–1 for comparison
forage_norm = monthly_foraging / monthly_foraging.max()
max_hooks = max(monthly_effort['hook_count'].max(), 1)
effort_norm = monthly_effort['hook_count'] / max_hooks

# Synchrony = sum of minimum overlap per month
temporal_synchrony = (forage_norm * effort_norm).sum() / forage_norm.sum()

print(f"  Temporal synchrony index: {temporal_synchrony:.3f}")
print(f"  (0 = no overlap, 1 = perfect overlap)")
print(f"\n  Monthly foraging peaks:")
for m, v in monthly_foraging.sort_values(ascending=False).head(3).items():
    print(f"    Month {m:2d}: {v:,} foraging points")

print(f"\n  CCAMLR longline effort peaks (2013):")
effort_sorted = monthly_effort['hook_count'].sort_values(ascending=False)
for m, v in effort_sorted.head(3).items():
    if v > 0:
        print(f"    Month {m:2d}: {v:,.0f} hooks")


# ============================================================================
# PART 6: INDIVIDUAL BIRD RISK PROFILING AND CLUSTERING
# ============================================================================

print("\nIndividual bird risk profiling...")

# Risk-relevant features from bird profiles:
# - max_dist_km: birds that range further encounter more fishing zones
# - prop_foraging: more time foraging = more exposure
# - forage_centre_lat: more southerly foraging = more CCAMLR exposure
# - total_dist_km: more ocean covered = more risk exposure

risk_features = ['max_dist_km', 'prop_foraging', 'forage_centre_lat', 'total_dist_km']

X = profiles[risk_features].copy()

# Invert forage_centre_lat: more negative = further south = higher risk
# Multiply by -1 so higher values = higher risk
X['forage_centre_lat'] = X['forage_centre_lat'] * -1

scaler   = StandardScaler()
X_scaled = scaler.fit_transform(X)

# K-means with 3 clusters (low / medium / high risk)
N_CLUSTERS = 3
kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=20)
profiles['risk_cluster'] = kmeans.fit_predict(X_scaled)

# Label clusters by mean max_dist (proxy for overall risk exposure)
cluster_means = profiles.groupby('risk_cluster')['max_dist_km'].mean()
cluster_rank  = cluster_means.rank().astype(int)
risk_labels   = {k: ['Low risk', 'Medium risk', 'High risk'][v - 1]
                 for k, v in cluster_rank.items()}
profiles['risk_label'] = profiles['risk_cluster'].map(risk_labels)

# Composite risk score (normalised, higher = higher risk)
profiles['risk_score'] = (
    (profiles['max_dist_km']   / profiles['max_dist_km'].max())   * 0.35 +
    (profiles['prop_foraging'] / profiles['prop_foraging'].max()) * 0.25 +
    (profiles['forage_centre_lat'] * -1 /
     (profiles['forage_centre_lat'] * -1).max())                  * 0.25 +
    (profiles['total_dist_km'] / profiles['total_dist_km'].max()) * 0.15
)

print("\n  Risk cluster summary:")
for label in ['Low risk', 'Medium risk', 'High risk']:
    grp = profiles[profiles['risk_label'] == label]
    print(f"\n  {label} ({len(grp)} birds):")
    print(f"    Mean max distance:  {grp['max_dist_km'].mean():.0f} km")
    print(f"    Mean prop foraging: {grp['prop_foraging'].mean():.2f}")
    print(f"    Mean forage lat:    {grp['forage_centre_lat'].mean():.1f}°")

# Save risk profiles
profiles.to_csv('data/processed/bird_risk_profiles.csv', index=False)
print("\n  ✓ Saved: data/processed/bird_risk_profiles.csv")


# ============================================================================
# PART 7: VISUALISATIONS
# ============================================================================

print("\nGenerating visualisations...")

fig = plt.figure(figsize=(20, 16), facecolor='white')
fig.suptitle('Grey-headed Albatross — Phase 3: Conservation Risk Analysis',
             fontsize=16, fontweight='bold', color=DARK_TEXT, y=1.01)

month_names = ['Jan','Feb','Mar','Apr','May','Jun',
               'Jul','Aug','Sep','Oct','Nov','Dec']

RISK_COLOURS = {'Low risk': GREEN, 'Medium risk': TEAL, 'High risk': WARM_RED}

# --- Panel 1: KDE foraging hotspot map ---
ax1 = fig.add_subplot(2, 2, 1, facecolor='#e8f4f8')

# Convert back for plotting: longitudes > 180 → subtract 360
# Plot KDE as filled contours
levels = np.percentile(ZZ[ZZ > 0], np.linspace(10, 99, 12))
cf = ax1.contourf(LON_MESH, LAT_MESH, ZZ, levels=levels,
                  cmap='YlOrRd', alpha=0.85)
ax1.contour(LON_MESH, LAT_MESH, ZZ, levels=levels,
            colors='white', alpha=0.3, linewidths=0.5)

# Campbell Island (in 0-360 space it's at 169°)
ax1.scatter(169.15, -52.55, c=DARK_TEXT, s=200, marker='*',
            edgecolors='white', linewidths=1.5, zorder=5,
            label='Campbell Island')

# CCAMLR boundary
ax1.axhline(y=-60, color=MAUVE, linestyle='--', linewidth=1.5,
            label='CCAMLR boundary (60°S)', alpha=0.8)

# Fix x-axis tick labels: convert 0-360 back to ±180 for display
xticks = [120, 150, 180, 210, 240, 270, 300]
xlabels = [f'{t}°E' if t <= 180 else f'{360-t}°W' for t in xticks]
ax1.set_xticks(xticks)
ax1.set_xticklabels(xlabels, fontsize=9, color=DARK_TEXT)
ax1.set_ylabel('Latitude (°S)', fontsize=11, color=DARK_TEXT)
ax1.set_title('Foraging Hotspots (KDE)', fontsize=13,
              fontweight='bold', color=DARK_TEXT, pad=10)
ax1.legend(fontsize=9, frameon=True, framealpha=0.8, loc='upper right')
ax1.tick_params(colors=DARK_TEXT)

from matplotlib import ticker
cb = plt.colorbar(cf, ax=ax1, label='Foraging density', shrink=0.8)
cb.formatter = ticker.ScalarFormatter(useMathText=True)
cb.formatter.set_powerlimits((-4, -4))
cb.update_ticks()

# --- Panel 2: Management zone breakdown ---
ax2 = fig.add_subplot(2, 2, 2, facecolor='white')

zone_order  = ['CCAMLR Convention Area', 'NZ EEZ / Subantarctic', 'High Seas / FAO 81']
zone_values = [zone_counts.get(z, 0) / total_forage * 100 for z in zone_order]
zone_colours= [MAUVE, GREEN, TEAL]

bars = ax2.barh(zone_order, zone_values, color=zone_colours, alpha=0.85,
                edgecolor='white')

for bar, val in zip(bars, zone_values):
    ax2.text(val + 0.5, bar.get_y() + bar.get_height() / 2,
             f'{val:.1f}%', va='center', fontsize=11,
             color=DARK_TEXT, fontweight='bold')

ax2.set_xlabel('% of Foraging Points', fontsize=11, color=DARK_TEXT)
ax2.set_title('Foraging Zone — Management Context',
              fontsize=13, fontweight='bold', color=DARK_TEXT, pad=10)
ax2.set_xlim(0, 105)
ax2.tick_params(colors=DARK_TEXT)
ax2.grid(True, alpha=0.2, color=MID_GREY, axis='x')
for spine in ax2.spines.values():
    spine.set_color(MID_GREY)

# --- Panel 3: Temporal synchrony ---
ax3 = fig.add_subplot(2, 2, 3, facecolor='white')

months = list(range(1, 13))
ax3_twin = ax3.twinx()

ax3.bar(months, monthly_foraging.values, color=GREEN, alpha=0.7,
        label='Foraging points', width=0.4,
        align='center')
ax3_twin.plot(months,
              [monthly_effort.loc[m, 'hook_count'] if m in monthly_effort.index
               else 0 for m in months],
              color=WARM_RED, linewidth=2.5, marker='o',
              markersize=7, label='Longline hooks (CCAMLR)', zorder=5)

ax3.set_xlabel('Month (2013)', fontsize=11, color=DARK_TEXT)
ax3.set_ylabel('Foraging GPS points', fontsize=11, color=GREEN)
ax3_twin.set_ylabel('CCAMLR hooks set', fontsize=11, color=WARM_RED)
ax3.set_title(f'Temporal Synchrony (index = {temporal_synchrony:.2f})',
              fontsize=13, fontweight='bold', color=DARK_TEXT, pad=10)
ax3.set_xticks(months)
ax3.set_xticklabels(month_names, rotation=45, fontsize=9)
ax3.tick_params(colors=DARK_TEXT)
ax3_twin.tick_params(colors=WARM_RED)
ax3.grid(True, alpha=0.2, color=MID_GREY, axis='y')

lines1, labels1 = ax3.get_legend_handles_labels()
lines2, labels2 = ax3_twin.get_legend_handles_labels()
ax3.legend(lines1 + lines2, labels1 + labels2, fontsize=9,
           frameon=False, loc='upper left')
for spine in ax3.spines.values():
    spine.set_color(MID_GREY)

# --- Panel 4: Individual risk scatter ---
ax4 = fig.add_subplot(2, 2, 4, facecolor='white')

for label, colour in RISK_COLOURS.items():
    grp = profiles[profiles['risk_label'] == label]
    ax4.scatter(grp['max_dist_km'], grp['prop_foraging'],
                c=colour, s=120, alpha=0.85, edgecolors='white',
                linewidths=1, label=label, zorder=3)
    for _, row in grp.iterrows():
        ax4.annotate(str(row['bird_id']),
                     (row['max_dist_km'], row['prop_foraging']),
                     fontsize=6, color=DARK_TEXT,
                     xytext=(4, 4), textcoords='offset points')

ax4.set_xlabel('Max Distance from Colony (km)', fontsize=11, color=DARK_TEXT)
ax4.set_ylabel('Proportion of Track Foraging', fontsize=11, color=DARK_TEXT)
ax4.set_title('Individual Risk Profiling (k-means, k=3)',
              fontsize=13, fontweight='bold', color=DARK_TEXT, pad=10)
ax4.legend(fontsize=10, frameon=False)
ax4.tick_params(colors=DARK_TEXT)
ax4.grid(True, alpha=0.2, color=MID_GREY)
for spine in ax4.spines.values():
    spine.set_color(MID_GREY)

fig.text(
    0.5, -0.01,
    "Data: Torres et al. 2017 (Movebank) · CCAMLR Statistical Bulletin Vol. 37 · "
    "Analysis: D. Crompton — dtcrompton.github.io",
    ha='center', fontsize=8, color=MID_GREY, style='italic'
)

plt.tight_layout()
plt.savefig('outputs/figures/phase3_risk_analysis.png', dpi=150,
            bbox_inches='tight', facecolor='white')
print("  ✓ Saved: outputs/figures/phase3_risk_analysis.png")
plt.close()


# ============================================================================
# PART 8: SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("PHASE 3 SUMMARY")
print("=" * 70)

high_risk = profiles[profiles['risk_label'] == 'High risk']

print(f"""
  Foraging zone distribution:
    NZ EEZ / Subantarctic (primary zone): {zone_counts.get('NZ EEZ / Subantarctic', 0)/total_forage*100:.1f}%
    CCAMLR Convention Area:               {zone_counts.get('CCAMLR Convention Area', 0)/total_forage*100:.1f}%
    High Seas / FAO 81:                   {zone_counts.get('High Seas / FAO 81', 0)/total_forage*100:.1f}%

  lon_dir = 'E' if peak_lon >= 0 else 'W'
  ...
  Peak foraging hotspot: {peak_lat:.1f}°S, {abs(peak_lon):.1f}°{lon_dir}

  Temporal synchrony index: {temporal_synchrony:.3f}

  Individual risk clusters:
    High risk birds ({len(high_risk)}):
      Mean max distance:  {high_risk['max_dist_km'].mean():.0f} km
      Mean prop foraging: {high_risk['prop_foraging'].mean():.2f}
      Bird IDs: {[int(x) for x in high_risk['bird_id'].values]}

  Conservation note:
    99.1% of foraging occurs in NZ EEZ / subantarctic waters not
    covered by CCAMLR. A complete bycatch risk assessment requires
    NZ Ministry for Primary Industries fisheries data (FAO Area 81 /
    SPRFMO Convention Area).
""")

print("=" * 70)
print("PHASE 3 COMPLETE")
print("=" * 70 + "\n")