"""
Phase 2a Figures — Regenerated with portfolio light theme
Grey-headed Albatross Foraging Ecology Project

Produces:
    outputs/figures/phase2a_behaviour.png   — 4-panel technical overview
    outputs/figures/linkedin_tracks_map.png — standalone single-panel map
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# --- Portfolio colours (light theme) ---
MAUVE     = "#B794D9"
GREEN     = "#7FAD87"
WARM_RED  = "#D9947F"
TEAL      = "#9BC4CB"
MID_GREY  = "#AAAAAA"
DARK_TEXT = "#1a1a1a"

STATE_COLOURS = {0: MID_GREY, 1: GREEN, 2: MAUVE}
STATE_LABELS  = {0: 'Resting', 1: 'Foraging', 2: 'Transiting'}

CAMPBELL_LON = 169.15
CAMPBELL_LAT = -52.55

print("Loading data...")
df = pd.read_csv('data/processed/tracks_with_behaviour.csv', parse_dates=['timestamp'])
bird_profiles = pd.read_csv('data/processed/bird_profiles.csv')

# ============================================================================
# FIGURE 1: 4-PANEL TECHNICAL OVERVIEW (light theme, fixed overplotting)
# ============================================================================

print("Generating phase2a_behaviour.png...")

fig = plt.figure(figsize=(20, 12), facecolor="white")
fig.suptitle('Grey-headed Albatross — Phase 2a: Behavioural Classification',
             fontsize=16, fontweight='bold', y=1.01, color=DARK_TEXT)

legend_patches = [
    mpatches.Patch(color=STATE_COLOURS[s], label=STATE_LABELS[s])
    for s in [0, 1, 2]
]

# --- Subplot 1: Spatial distribution — plot order fixes overplotting ---
ax1 = fig.add_subplot(2, 2, 1, facecolor="white")

# Transiting first (most numerous/spread), then Resting, then Foraging on top
plot_order = [2, 0, 1]
for state in plot_order:
    pts = df[df['behaviour'] == state]
    ax1.scatter(pts['location-long'], pts['location-lat'],
                c=STATE_COLOURS[state], s=0.5, alpha=0.5,
                label=STATE_LABELS[state], edgecolors='none')

ax1.scatter(CAMPBELL_LON, CAMPBELL_LAT, c=DARK_TEXT, s=200, marker='*',
            edgecolors='white', linewidths=1, zorder=5,
            label='Campbell Island')

ax1.set_xlabel('Longitude (°E)', fontsize=11, color=DARK_TEXT)
ax1.set_ylabel('Latitude (°S)', fontsize=11, color=DARK_TEXT)
ax1.set_title('Spatial Distribution of Behaviour States', fontsize=13,
              fontweight='bold', color=DARK_TEXT)
ax1.legend(handles=legend_patches + [
    plt.scatter([], [], c=DARK_TEXT, s=100, marker='*', label='Campbell Island')],
    fontsize=9, frameon=False)
ax1.tick_params(colors=DARK_TEXT)
ax1.grid(True, alpha=0.2, color=MID_GREY)
for spine in ax1.spines.values():
    spine.set_color(MID_GREY)

# --- Subplot 2: Example bird — behaviour over time ---
ax2 = fig.add_subplot(2, 2, 2, facecolor="white")

example_bird = bird_profiles.loc[bird_profiles['n_points'].idxmax(), 'bird_id']
bdf = df[df['individual-local-identifier'] == example_bird]

for state in plot_order:
    pts = bdf[bdf['behaviour'] == state]
    ax2.scatter(pts['timestamp'], pts['dist_from_campbell'],
                c=STATE_COLOURS[state], s=3, alpha=0.7, edgecolors='none')

ax2.axhline(y=50, color=WARM_RED, linestyle='--', linewidth=1.2,
            label='Colony boundary (50 km)')
ax2.set_xlabel('Date (2013)', fontsize=11, color=DARK_TEXT)
ax2.set_ylabel('Distance from Campbell Island (km)', fontsize=11, color=DARK_TEXT)
ax2.set_title(f'Bird {example_bird} — Behaviour Over Time', fontsize=13,
              fontweight='bold', color=DARK_TEXT)
ax2.legend(handles=legend_patches, fontsize=9, frameon=False, loc='upper left')
ax2.tick_params(colors=DARK_TEXT)
ax2.grid(True, alpha=0.2, color=MID_GREY)
for spine in ax2.spines.values():
    spine.set_color(MID_GREY)

# --- Subplot 3: Step length distribution — log scale fixes hidden states ---
ax3 = fig.add_subplot(2, 2, 3, facecolor="white")

for state in [0, 1, 2]:
    vals = df.loc[df['behaviour'] == state, 'step_length_km']
    vals = vals[vals > 0]  # log scale can't handle 0
    ax3.hist(vals, bins=np.logspace(np.log10(0.01), np.log10(50), 60),
             alpha=0.6, color=STATE_COLOURS[state], label=STATE_LABELS[state],
             density=True)

ax3.set_xscale('log')
ax3.set_xlabel('Step Length (km, log scale)', fontsize=11, color=DARK_TEXT)
ax3.set_ylabel('Density', fontsize=11, color=DARK_TEXT)
ax3.set_title('Step Length Distribution by State', fontsize=13,
              fontweight='bold', color=DARK_TEXT)
ax3.legend(handles=legend_patches, fontsize=9, frameon=False)
ax3.tick_params(colors=DARK_TEXT)
ax3.grid(True, alpha=0.2, color=MID_GREY, axis='y')
for spine in ax3.spines.values():
    spine.set_color(MID_GREY)

# --- Subplot 4: Per-bird time budget ---
ax4 = fig.add_subplot(2, 2, 4, facecolor="white")

sorted_profiles = bird_profiles.sort_values('prop_foraging', ascending=True)
y_pos = range(len(sorted_profiles))

ax4.barh(list(y_pos), sorted_profiles['prop_resting'],
         color=STATE_COLOURS[0], alpha=0.9, label='Resting')
ax4.barh(list(y_pos), sorted_profiles['prop_foraging'],
         left=sorted_profiles['prop_resting'],
         color=STATE_COLOURS[1], alpha=0.9, label='Foraging')
ax4.barh(list(y_pos), sorted_profiles['prop_transiting'],
         left=sorted_profiles['prop_resting'] + sorted_profiles['prop_foraging'],
         color=STATE_COLOURS[2], alpha=0.9, label='Transiting')

ax4.set_yticks(list(y_pos))
ax4.set_yticklabels([str(b) for b in sorted_profiles['bird_id']], fontsize=7,
                    color=DARK_TEXT)
ax4.set_xlabel('Proportion of Track', fontsize=11, color=DARK_TEXT)
ax4.set_title('Time Budget per Bird', fontsize=13, fontweight='bold',
              color=DARK_TEXT)
ax4.legend(handles=legend_patches, fontsize=9, frameon=False, loc='lower right')
ax4.tick_params(colors=DARK_TEXT)
ax4.grid(True, alpha=0.2, color=MID_GREY, axis='x')
for spine in ax4.spines.values():
    spine.set_color(MID_GREY)

fig.text(
    0.5, -0.01,
    "Data: Torres et al. 2017, Movebank Data Repository · "
    "Analysis: D. Crompton — dtcrompton.github.io",
    ha="center", fontsize=8, color=MID_GREY, style="italic"
)

plt.tight_layout()
plt.savefig('outputs/figures/phase2a_behaviour.png', dpi=150,
            bbox_inches='tight', facecolor="white")
print("  ✓ Saved: outputs/figures/phase2a_behaviour.png")
plt.close()


# ============================================================================
# FIGURE 2: STANDALONE LINKEDIN MAP
# ============================================================================

print("Generating linkedin_tracks_map.png...")

fig2, ax = plt.subplots(figsize=(12, 9), facecolor="white")
ax.set_facecolor("white")

# All tracks in a single colour, individual lines (not scatter) for a
# cleaner "flight path" look
def split_on_dateline(lons, lats):
    """
    Split coordinate arrays into segments wherever consecutive longitude
    values jump by more than 180 degrees (dateline crossing), so plot()
    doesn't draw a spurious line straight across the map.
    """
    lons = np.array(lons)
    lats = np.array(lats)
    jumps = np.where(np.abs(np.diff(lons)) > 180)[0]

    segments = []
    start = 0
    for j in jumps:
        segments.append((lons[start:j+1], lats[start:j+1]))
        start = j + 1
    segments.append((lons[start:], lats[start:]))
    return segments


# All tracks in a single colour, split at dateline crossings
for bird_id in df['individual-local-identifier'].unique():
    bird_data = df[df['individual-local-identifier'] == bird_id]
    segments = split_on_dateline(bird_data['location-long'].values,
                                 bird_data['location-lat'].values)
    for seg_lon, seg_lat in segments:
        if len(seg_lon) > 1:
            ax.plot(seg_lon, seg_lat, color=MAUVE, alpha=0.5, linewidth=1.2)

ax.scatter(CAMPBELL_LON, CAMPBELL_LAT, c=DARK_TEXT, s=300, marker='*',
           edgecolors='white', linewidths=1.5, zorder=5)

ax.set_title('24 Grey-headed Albatrosses — One Breeding Season\nSouthern Ocean GPS Tracks, 2013',
             fontsize=16, fontweight='bold', color=DARK_TEXT, pad=16)
ax.set_xlabel('Longitude (°E)', fontsize=11, color=DARK_TEXT)
ax.set_ylabel('Latitude (°S)', fontsize=11, color=DARK_TEXT)

track_handle = Line2D([0], [0], color=MAUVE, alpha=0.5, linewidth=1.2,
                       label='Albatross GPS track')
colony_handle = Line2D([0], [0], marker='*', color='none',
                       markerfacecolor=DARK_TEXT, markeredgecolor='white',
                       markersize=14, label='Campbell Island (breeding colony)')

ax.legend(handles=[track_handle, colony_handle],
          fontsize=11, frameon=False, loc='upper right')

ax.tick_params(colors=DARK_TEXT)
ax.grid(True, alpha=0.15, color=MID_GREY)
for spine in ax.spines.values():
    spine.set_color(MID_GREY)

# Replace the fig.text call and add subplots_adjust before savefig, Figure 2:
plt.tight_layout()
fig2.subplots_adjust(bottom=0.05)

fig2.text(
    0.5, -0.02,
    "Data: Torres et al. 2017, Movebank Data Repository · "
    "Analysis: D. Crompton — dtcrompton.github.io",
    ha="center", fontsize=9, color=MID_GREY, style="italic"
)

plt.savefig('outputs/figures/linkedin_tracks_map.png', dpi=200,
            bbox_inches='tight', facecolor="white")
print("  ✓ Saved: outputs/figures/linkedin_tracks_map.png")
plt.close()

print("\nDone.")