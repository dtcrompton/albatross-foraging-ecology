"""
Phase 3: Foraging hotspots, EEZ classification and clustering
Grey-headed Albatross Foraging Ecology Project

Maps foraging hotspots, compares the timing of foraging with CCAMLR longline
effort, and clusters the birds into foraging-strategy groups A / B / C.

Foraging fixes are classified by point-in-polygon against World EEZ v12, and against
the 60S line for CCAMLR (see eez_classification.py). Every share is computed below.

Outputs (file names are kept because other sites link to them):
    outputs/figures/phase3_risk_analysis.png  — 4-panel figure
    data/processed/bird_risk_profiles.csv     — per-bird metrics and strategy_group
    data/processed/foraging_kde_grid.csv      — KDE density grid
    data/processed/eez_zone_summary.csv       — zone shares by behaviour state
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter
from pathlib import Path
from scipy.stats import gaussian_kde
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from colony import COLONY_LAT, COLONY_LON
from eez_classification import ZONES, Z_GAP, Z_NZ, Z_OUT, classify_fixes
from strategy_groups import GROUP_COLOURS, GROUP_FROM_RISK_LABEL

# --- Portfolio colours (light theme) ---
MAUVE     = "#B794D9"
GREEN     = "#7FAD87"
WARM_RED  = "#D9947F"
TEAL      = "#9BC4CB"
MID_GREY  = "#AAAAAA"
DARK_TEXT = "#1a1a1a"

CCAMLR_DIR = Path('data/raw/ccamlr/CCAMLR_statistical bulletin_V37')

print("\n" + "=" * 70)
print("PHASE 3: FORAGING HOTSPOTS, EEZ CLASSIFICATION AND CLUSTERING")
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

print("\nClassifying fixes against World EEZ v12...")

foraging_pts = df[df['behaviour'] == 1].copy()

zone_all, south_all = classify_fixes(df['location-long'], df['location-lat'])
df['zone'] = zone_all
df['south_of_60S'] = south_all
foraging_pts['zone'] = df.loc[foraging_pts.index, 'zone']
foraging_pts['south_of_60S'] = df.loc[foraging_pts.index, 'south_of_60S']

total_forage = len(foraging_pts)
n_nz = int((foraging_pts['zone'] == Z_NZ).sum())
n_out = int((foraging_pts['zone'] == Z_OUT).sum())
n_south = int(foraging_pts['south_of_60S'].sum())
n_out_north = int(((foraging_pts['zone'] == Z_OUT) & ~foraging_pts['south_of_60S']).sum())
n_gap = int((foraging_pts['zone'] == Z_GAP).sum())

print(f"\n  Foraging fixes: {total_forage:,}")
print(f"    Inside New Zealand EEZ:         {n_nz:6,} ({n_nz/total_forage*100:.2f}%)")
print(f"    Outside all EEZs:               {n_out:6,} ({n_out/total_forage*100:.2f}%)")
print(f"    South of 60S:                   {n_south:6,} ({n_south/total_forage*100:.2f}%)")
print(f"    North of or on 60S:             {total_forage-n_south:6,} ({(total_forage-n_south)/total_forage*100:.2f}%)")

summary_rows = []
for state, group in [('Foraging', df[df['behaviour'] == 1]),
                     ('Transiting', df[df['behaviour'] == 2]),
                     ('Resting', df[df['behaviour'] == 0]),
                     ('All fixes', df)]:
    for z in ZONES:
        count = int((group['zone'] == z).sum())
        summary_rows.append({'state': state, 'measure': z, 'count': count,
                             'percent': count / len(group) * 100})
    count = int(group['south_of_60S'].sum())
    summary_rows.append({'state': state, 'measure': 'South of 60S', 'count': count,
                         'percent': count / len(group) * 100})
pd.DataFrame(summary_rows).to_csv('data/processed/eez_zone_summary.csv', index=False)
print("  ✓ Saved: data/processed/eez_zone_summary.csv")


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
# PART 5: TEMPORAL SYNCHRONY
# ============================================================================

print("\nTemporal synchrony...")

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
# PART 6: FORAGING-STRATEGY GROUPS (K-MEANS)
# ============================================================================
# The risk_* names below are legacy column and variable names. They are kept so the
# CSV stays compatible; the groups use no fishing data and do not measure risk.

print("\nForaging-strategy groups...")

# Foraging-strategy metrics from bird profiles:
# - max_dist_km, prop_foraging, forage_centre_lat, total_dist_km

risk_features = ['max_dist_km', 'prop_foraging', 'forage_centre_lat', 'total_dist_km']

X = profiles[risk_features].copy()

# Invert forage_centre_lat: multiply by -1 so higher values = further south
X['forage_centre_lat'] = X['forage_centre_lat'] * -1

scaler   = StandardScaler()
X_scaled = scaler.fit_transform(X)

# K-means with 3 clusters
N_CLUSTERS = 3
kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=20)
profiles['risk_cluster'] = kmeans.fit_predict(X_scaled)

# Rank clusters by mean max_dist; risk_label holds the legacy names for those ranks
cluster_means = profiles.groupby('risk_cluster')['max_dist_km'].mean()
cluster_rank  = cluster_means.rank().astype(int)
risk_labels   = {k: ['Low risk', 'Medium risk', 'High risk'][v - 1]
                 for k, v in cluster_rank.items()}
profiles['risk_label'] = profiles['risk_cluster'].map(risk_labels)

# Legacy composite score (normalised)
profiles['risk_score'] = (
    (profiles['max_dist_km']   / profiles['max_dist_km'].max())   * 0.35 +
    (profiles['prop_foraging'] / profiles['prop_foraging'].max()) * 0.25 +
    (profiles['forage_centre_lat'] * -1 /
     (profiles['forage_centre_lat'] * -1).max())                  * 0.25 +
    (profiles['total_dist_km'] / profiles['total_dist_km'].max()) * 0.15
)

# New last column, so every existing column keeps its position and values
profiles['strategy_group'] = profiles['risk_label'].map(GROUP_FROM_RISK_LABEL)

print("\n  Foraging-strategy group summary:")
for group in GROUP_COLOURS:
    grp = profiles[profiles['strategy_group'] == group]
    print(f"\n  Foraging-strategy group {group} ({len(grp)} birds):")
    print(f"    Mean max distance:  {grp['max_dist_km'].mean():.0f} km")
    print(f"    Mean prop foraging: {grp['prop_foraging'].mean():.2f}")
    print(f"    Mean forage lat:    {grp['forage_centre_lat'].mean():.1f}°")

# Save bird profiles
profiles.to_csv('data/processed/bird_risk_profiles.csv', index=False)
print("\n  ✓ Saved: data/processed/bird_risk_profiles.csv")


# ============================================================================
# PART 7: VISUALISATIONS
# ============================================================================

print("\nGenerating visualisations...")

fig = plt.figure(figsize=(20, 16), facecolor='white')
fig.suptitle('Grey-headed Albatross — Phase 3: Foraging hotspots, EEZ classification and clustering',
             fontsize=16, fontweight='bold', color=DARK_TEXT, y=1.01)

month_names = ['Jan','Feb','Mar','Apr','May','Jun',
               'Jul','Aug','Sep','Oct','Nov','Dec']

# --- Panel 1: KDE foraging hotspot map ---
ax1 = fig.add_subplot(2, 2, 1, facecolor='#e8f4f8')

# Highest-density regions, for display only: the smallest real-world areas holding each
# share of the density. ZZ is per square degree, so a cell's mass is ZZ x its degree area.
# Its real-world area scales with cos(latitude), so cells are ranked by mass per unit area.
cell_mass = ZZ * (lon_grid[1] - lon_grid[0]) * (lat_grid[1] - lat_grid[0])
mass_per_area = ZZ / np.cos(np.radians(LAT_MESH))
rank_order = np.argsort(mass_per_area.ravel())[::-1]
ranked_values = mass_per_area.ravel()[rank_order]
cumulative_mass = np.cumsum(cell_mass.ravel()[rank_order]) / cell_mass.sum()

HDR_COLOURS = {90: '#FDD0A2', 75: '#FD8D3C', 50: '#A63603'}  # one hue, darkest for 50%
hdr_levels = [ranked_values[np.searchsorted(cumulative_mass, share / 100)]
              for share in HDR_COLOURS]
ax1.contourf(LON_MESH, LAT_MESH, mass_per_area,
             levels=hdr_levels + [mass_per_area.max() * 1.01],
             colors=list(HDR_COLOURS.values()))

# Campbell Island (in 0-360 space it's at 169°)
ax1.scatter(COLONY_LON, COLONY_LAT, c=DARK_TEXT, s=200, marker='*',
            edgecolors='white', linewidths=1.5, zorder=5,
            label='Campbell Island')

# CCAMLR boundary
ax1.axhline(y=-60, color=MAUVE, linestyle='--', linewidth=1.5,
            label='CCAMLR boundary (60°S)', alpha=0.8)

# Fix x-axis tick labels: convert 0-360 back to ±180 for display
xticks = [160, 170, 180, 190, 200, 210, 220]
xlabels = [f'{t}°E' if t <= 180 else f'{360-t}°W' for t in xticks]
ax1.set_xlim(155, 220)  # display only: the KDE grid is unchanged
ax1.set_xticks(xticks)
ax1.set_xticklabels(xlabels, fontsize=9, color=DARK_TEXT)
ax1.set_ylabel('Latitude (°S)', fontsize=11, color=DARK_TEXT)
ax1.set_title('Foraging Hotspots (KDE)', fontsize=13,
              fontweight='bold', color=DARK_TEXT, pad=10)
hdr_handles = [mpatches.Patch(color=HDR_COLOURS[share], label=f'{share}% of density')
               for share in (50, 75, 90)]
ax1.legend(handles=hdr_handles + ax1.get_legend_handles_labels()[0],
           fontsize=9, frameon=True, framealpha=0.8, loc='upper right')
ax1.tick_params(colors=DARK_TEXT)
ax1.text(0.5, -0.075,
         'Kernel density of foraging fixes. Shading marks the smallest areas '
         'holding 50%, 75% and 90% of the density.',
         transform=ax1.transAxes, ha='center', fontsize=9.5, color=DARK_TEXT)

# --- Panel 2: Management zone breakdown ---
ax2 = fig.add_subplot(2, 2, 2, facecolor='white')

# Three exclusive groups; south of 60S is also outside all EEZs
assert n_nz + n_out_north + n_south + n_gap == total_forage
zone_order  = ['South of 60°S\n(outside all EEZs)', 'Outside all EEZs,\nnorth of 60°S', 'Inside New Zealand EEZ']
zone_values = [n_south / total_forage * 100, n_out_north / total_forage * 100, n_nz / total_forage * 100]
zone_colours= [MAUVE, GREEN, TEAL]

bars = ax2.barh(zone_order, zone_values, color=zone_colours, alpha=0.85,
                edgecolor='white')

for bar, val in zip(bars, zone_values):
    ax2.text(val + 0.5, bar.get_y() + bar.get_height() / 2,
             f'{val:.2f}%', va='center', fontsize=11,
             color=DARK_TEXT, fontweight='bold')

ax2.set_xlabel(f'% of {total_forage:,} Foraging Fixes', fontsize=11, color=DARK_TEXT)
ax2.set_title('Foraging Fixes by Zone — World EEZ v12 and 60°S',
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
ax3_twin.set_ylabel('CCAMLR hooks set (millions)', fontsize=11, color=WARM_RED)
ax3_twin.set_ylim(bottom=0)  # both axes start at zero
ax3_twin.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f'{value / 1e6:.0f}'))
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
           frameon=False, loc='upper center')
for spine in ax3.spines.values():
    spine.set_color(MID_GREY)

# --- Panel 4: Foraging-strategy groups scatter ---
ax4 = fig.add_subplot(2, 2, 4, facecolor='white')

for group, colour in GROUP_COLOURS.items():
    grp = profiles[profiles['strategy_group'] == group]
    ax4.scatter(grp['max_dist_km'], grp['prop_foraging'],
                c=colour, s=120, edgecolors='white',
                linewidths=1, label=f'Foraging-strategy group {group}', zorder=3)
    for _, row in grp.iterrows():
        # These two would sit on a neighbouring bird, so their labels go to the left
        label_left = row['bird_id'] in (90407, 90494)
        ax4.annotate(str(row['bird_id']),
                     (row['max_dist_km'], row['prop_foraging']),
                     fontsize=6, color=DARK_TEXT,
                     xytext=(-6, 4) if label_left else (4, 4),
                     ha='right' if label_left else 'left',
                     textcoords='offset points')

ax4.set_xlabel('Max Distance from Colony (km)', fontsize=11, color=DARK_TEXT)
ax4.set_ylabel('Proportion of Track Foraging', fontsize=11, color=DARK_TEXT)
ax4.set_title('Foraging-strategy groups (k-means)',
              fontsize=13, fontweight='bold', color=DARK_TEXT, pad=10)
ax4.legend(fontsize=10, frameon=False)
ax4.tick_params(colors=DARK_TEXT)
ax4.grid(True, alpha=0.2, color=MID_GREY)
for spine in ax4.spines.values():
    spine.set_color(MID_GREY)

fig.text(
    0.5, -0.01,
    "Data: Thompson et al. (2017), Movebank Data Repository · CCAMLR Statistical Bulletin Vol. 37 · "
    "EEZ: Flanders Marine Institute (2023), World EEZ v12, CC BY 4.0 · "
    "Analysis: D. Crompton — dtcrompton.github.io",
    ha='center', fontsize=8, color=MID_GREY, style='italic'
)

plt.tight_layout(h_pad=3)  # room for the caption under the KDE panel
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

group_c = profiles[profiles['strategy_group'] == 'C']

print(f"""
  Foraging fix classification ({total_forage:,} fixes):
    Inside New Zealand EEZ: {n_nz/total_forage*100:.2f}%
    Outside all EEZs:       {n_out/total_forage*100:.2f}%
    South of 60S:           {n_south/total_forage*100:.2f}%

  lon_dir = 'E' if peak_lon >= 0 else 'W'
  ...
  Peak foraging hotspot: {peak_lat:.1f}°S, {abs(peak_lon):.1f}°{lon_dir}

  Temporal synchrony index: {temporal_synchrony:.3f}

  Foraging-strategy groups:
    Group C birds ({len(group_c)}):
      Mean max distance:  {group_c['max_dist_km'].mean():.0f} km
      Mean prop foraging: {group_c['prop_foraging'].mean():.2f}
      Bird IDs: {[int(x) for x in group_c['bird_id'].values]}
""")

print("=" * 70)
print("PHASE 3 COMPLETE")
print("=" * 70 + "\n")