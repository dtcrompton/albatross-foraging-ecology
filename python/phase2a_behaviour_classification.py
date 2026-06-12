"""
Phase 2a: Behavioural State Classification via Hidden Markov Model
Grey-headed Albatross Foraging Ecology Project

Classifies each GPS point into one of three behavioural states:
    0 — Resting    (very low step length, variable turning angle)
    1 — Foraging   (low–moderate step length, high turning angle)
    2 — Transiting (high step length, low turning angle)

Uses a Gaussian HMM fitted to log-transformed step length and
absolute turning angle across all 24 birds simultaneously.

Outputs:
    data/processed/tracks_with_behaviour.csv  — GPS data + behaviour state
    data/processed/bird_profiles.csv          — per-bird summary metrics
    outputs/figures/phase2a_behaviour.png     — 4-panel behaviour overview
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from hmmlearn import hmm

plt.style.use('dark_background')

PURPLE = '#B794D9'
GREEN  = '#7FAD87'
SALMON = '#e8a899'
STATE_COLOURS = {0: SALMON, 1: GREEN, 2: PURPLE}
STATE_LABELS  = {0: 'Resting', 1: 'Foraging', 2: 'Transiting'}

print("\n" + "=" * 70)
print("PHASE 2a: HMM BEHAVIOUR CLASSIFICATION")
print("=" * 70)


# ============================================================================
# PART 1: LOAD AND PREPARE DATA
# ============================================================================

print("\nLoading data...")

df = pd.read_csv('data/processed/tracks_with_metrics.csv',
                 parse_dates=['timestamp'])
df = df.sort_values(['individual-local-identifier', 'timestamp']
                    ).reset_index(drop=True)

print(f"  {len(df):,} GPS points, {df['individual-local-identifier'].nunique()} birds")


# ============================================================================
# PART 2: BUILD HMM FEATURE MATRIX
# ============================================================================

print("\nBuilding feature matrix...")

# Log-transform step length: step lengths follow a right-skewed distribution
# Log makes it approximately Gaussian, which the HMM emission model assumes.
# Add 0.01 to avoid log(0) on stationary points.
df['log_step'] = np.log(df['step_length_km'] + 0.01)

# Replace NaN turning angles (first/last point of each bird) with 0
# (straight-ahead — neutral, won't bias the model)
df['hmm_angle'] = df['abs_turning_angle'].fillna(0.0)

# Replace any remaining NaN log_step values with log of a near-zero value
df['hmm_log_step'] = df['log_step'].fillna(np.log(0.01))

# Feature matrix: shape (n_points, 2)
features = df[['hmm_log_step', 'hmm_angle']].values

# Record the number of GPS points per bird, in order
# hmmlearn needs this to treat each bird as a separate sequence
bird_ids   = df['individual-local-identifier'].unique()
lengths    = [len(df[df['individual-local-identifier'] == b]) for b in bird_ids]

print(f"  Feature matrix shape: {features.shape}")
print(f"  Sequence lengths: min={min(lengths)}, max={max(lengths)}, "
      f"mean={np.mean(lengths):.0f}")


# ============================================================================
# PART 3: FIT GAUSSIAN HMM
# ============================================================================

print("\nFitting HMM (3 states, Gaussian emissions)...")

model = hmm.GaussianHMM(
    n_components  = 3,      # resting, foraging, transiting
    covariance_type = 'full',
    n_iter        = 200,    # max EM iterations
    random_state  = 42,
    tol           = 1e-4
)

model.fit(features, lengths)

print(f"  Converged: {model.monitor_.converged}")
print(f"  Log-likelihood: {model.score(features, lengths):.1f}")

# Predict most likely state sequence for all birds
raw_states = model.predict(features, lengths)
df['hmm_state_raw'] = raw_states


# ============================================================================
# PART 4: LABEL STATES BY BIOLOGICAL MEANING
# ============================================================================

# The HMM assigns arbitrary state numbers (0, 1, 2).
# We assign biological meaning by ranking states on mean step length:
#   lowest mean step length  → Resting (0)
#   middle mean step length  → Foraging (1)
#   highest mean step length → Transiting (2)

print("\nLabelling states by mean step length...")

state_means = {}
for s in range(3):
    mask = df['hmm_state_raw'] == s
    state_means[s] = df.loc[mask, 'step_length_km'].mean()
    print(f"  Raw state {s}: mean step = {state_means[s]:.2f} km, "
          f"mean turning = "
          f"{np.degrees(df.loc[mask, 'abs_turning_angle'].mean()):.1f}°  "
          f"({mask.sum():,} points)")

# Sort raw states by ascending mean step length → [resting, foraging, transiting]
sorted_states = sorted(state_means, key=state_means.get)
state_map = {raw: labelled for labelled, raw in enumerate(sorted_states)}

df['behaviour'] = df['hmm_state_raw'].map(state_map)

# Summary of labelled states
print("\nLabelled state summary:")
for s in [0, 1, 2]:
    mask = df['behaviour'] == s
    pct  = mask.sum() / len(df) * 100
    print(f"  {STATE_LABELS[s]:12s}: {mask.sum():6,} points ({pct:.1f}%) | "
          f"mean step = {df.loc[mask, 'step_length_km'].mean():.2f} km | "
          f"mean turning = "
          f"{np.degrees(df.loc[mask, 'abs_turning_angle'].mean()):.1f}°")


# ============================================================================
# PART 5: PER-BIRD PROFILE GENERATION
# ============================================================================

print("\nBuilding per-bird profiles...")

profiles = []

for bird_id in bird_ids:
    bdf = df[df['individual-local-identifier'] == bird_id].copy()

    # Proportion of time in each state
    n_pts   = len(bdf)
    p_rest  = (bdf['behaviour'] == 0).sum() / n_pts
    p_forage= (bdf['behaviour'] == 1).sum() / n_pts
    p_trans = (bdf['behaviour'] == 2).sum() / n_pts

    # Spatial extent
    lat_min = bdf['location-lat'].min()
    lat_max = bdf['location-lat'].max()
    lon_min = bdf['location-long'].min()
    lon_max = bdf['location-long'].max()

    # Movement characteristics
    max_dist   = bdf['dist_from_campbell'].max()
    mean_speed = bdf['speed_kmh'].mean()
    total_dist = bdf['step_length_km'].sum()
    mean_angle = bdf['abs_turning_angle'].mean()

    # Foraging centre of mass (mean location of foraging points)
    forage_pts = bdf[bdf['behaviour'] == 1]
    forage_lat = forage_pts['location-lat'].mean()
    forage_lon = forage_pts['location-long'].mean()

    # Temporal range
    start = bdf['timestamp'].min()
    end   = bdf['timestamp'].max()

    profiles.append({
        'bird_id':          bird_id,
        'n_points':         n_pts,
        'start_date':       start,
        'end_date':         end,
        'prop_resting':     round(p_rest,  3),
        'prop_foraging':    round(p_forage,3),
        'prop_transiting':  round(p_trans, 3),
        'max_dist_km':      round(max_dist,   1),
        'total_dist_km':    round(total_dist, 1),
        'mean_speed_kmh':   round(mean_speed, 2),
        'mean_turning_deg': round(np.degrees(mean_angle), 2),
        'lat_min':          round(lat_min, 4),
        'lat_max':          round(lat_max, 4),
        'lon_min':          round(lon_min, 4),
        'lon_max':          round(lon_max, 4),
        'forage_centre_lat':round(forage_lat, 4),
        'forage_centre_lon':round(forage_lon, 4),
    })

bird_profiles = pd.DataFrame(profiles)

print(f"  Profiles built for {len(bird_profiles)} birds")
print(f"\n  Foraging strategy range:")
print(f"    Prop. foraging: {bird_profiles['prop_foraging'].min():.2f} – "
      f"{bird_profiles['prop_foraging'].max():.2f}")
print(f"    Max distance:   {bird_profiles['max_dist_km'].min():.0f} – "
      f"{bird_profiles['max_dist_km'].max():.0f} km")
print(f"    Total distance: {bird_profiles['total_dist_km'].min():.0f} – "
      f"{bird_profiles['total_dist_km'].max():.0f} km")


# ============================================================================
# PART 6: VISUALISATIONS
# ============================================================================

print("\nGenerating visualisations...")

fig = plt.figure(figsize=(20, 12))
fig.suptitle('Grey-headed Albatross — Phase 2a: Behavioural Classification',
             fontsize=16, fontweight='bold', y=1.01)

legend_patches = [
    mpatches.Patch(color=STATE_COLOURS[s], label=STATE_LABELS[s])
    for s in [0, 1, 2]
]

# --- Subplot 1: Spatial distribution of behaviour states (all birds) ---
ax1 = fig.add_subplot(2, 2, 1)

for state in [0, 1, 2]:
    pts = df[df['behaviour'] == state]
    ax1.scatter(pts['location-long'], pts['location-lat'],
                c=STATE_COLOURS[state], s=0.3, alpha=0.4,
                label=STATE_LABELS[state])

ax1.scatter(169.15, -52.55, c='white', s=200, marker='*',
            edgecolors='red', linewidths=1.5, zorder=5,
            label='Campbell Island')
ax1.set_xlabel('Longitude (°E)', fontsize=11)
ax1.set_ylabel('Latitude (°S)', fontsize=11)
ax1.set_title('Spatial Distribution of Behaviour States', fontsize=13,
              fontweight='bold')
ax1.legend(handles=legend_patches + [
    plt.scatter([], [], c='white', s=100, marker='*', label='Campbell Island')],
    fontsize=9)
ax1.grid(True, alpha=0.2)

# --- Subplot 2: Example bird — behaviour over time ---
ax2 = fig.add_subplot(2, 2, 2)

# Use the bird with the most points
example_bird = bird_profiles.loc[bird_profiles['n_points'].idxmax(), 'bird_id']
bdf = df[df['individual-local-identifier'] == example_bird]

for state in [0, 1, 2]:
    pts = bdf[bdf['behaviour'] == state]
    ax2.scatter(pts['timestamp'], pts['dist_from_campbell'],
                c=STATE_COLOURS[state], s=1.5, alpha=0.7)

ax2.axhline(y=50, color='red', linestyle='--', linewidth=1,
            label='Colony boundary (50 km)')
ax2.set_xlabel('Date (2013)', fontsize=11)
ax2.set_ylabel('Distance from Campbell Island (km)', fontsize=11)
ax2.set_title(f'Bird {example_bird} — Behaviour Over Time', fontsize=13,
              fontweight='bold')
ax2.legend(handles=legend_patches, fontsize=9)
ax2.grid(True, alpha=0.2)

# --- Subplot 3: Step length distribution by state ---
ax3 = fig.add_subplot(2, 2, 3)

for state in [0, 1, 2]:
    vals = df.loc[df['behaviour'] == state, 'step_length_km']
    ax3.hist(vals.clip(upper=200), bins=60, alpha=0.6,
             color=STATE_COLOURS[state], label=STATE_LABELS[state],
             density=True)

ax3.set_xlabel('Step Length (km, clipped at 200)', fontsize=11)
ax3.set_ylabel('Density', fontsize=11)
ax3.set_title('Step Length Distribution by State', fontsize=13,
              fontweight='bold')
ax3.legend(handles=legend_patches, fontsize=9)
ax3.grid(True, alpha=0.2, axis='y')

# --- Subplot 4: Per-bird foraging proportion ---
ax4 = fig.add_subplot(2, 2, 4)

sorted_profiles = bird_profiles.sort_values('prop_foraging', ascending=True)
y_pos = range(len(sorted_profiles))

ax4.barh(list(y_pos), sorted_profiles['prop_resting'],
         color=SALMON, alpha=0.85, label='Resting')
ax4.barh(list(y_pos), sorted_profiles['prop_foraging'],
         left=sorted_profiles['prop_resting'],
         color=GREEN, alpha=0.85, label='Foraging')
ax4.barh(list(y_pos), sorted_profiles['prop_transiting'],
         left=sorted_profiles['prop_resting'] + sorted_profiles['prop_foraging'],
         color=PURPLE, alpha=0.85, label='Transiting')

ax4.set_yticks(list(y_pos))
ax4.set_yticklabels([str(b) for b in sorted_profiles['bird_id']], fontsize=7)
ax4.set_xlabel('Proportion of Track', fontsize=11)
ax4.set_title('Time Budget per Bird', fontsize=13, fontweight='bold')
ax4.legend(handles=legend_patches, fontsize=9, loc='lower right')
ax4.grid(True, alpha=0.2, axis='x')

plt.tight_layout()
plt.savefig('outputs/figures/phase2a_behaviour.png', dpi=150,
            bbox_inches='tight')
print("  ✓ Saved: outputs/figures/phase2a_behaviour.png")


# ============================================================================
# PART 7: SAVE OUTPUTS
# ============================================================================

print("\nSaving outputs...")

df.to_csv('data/processed/tracks_with_behaviour.csv', index=False)
print("  ✓ Saved: data/processed/tracks_with_behaviour.csv")

bird_profiles.to_csv('data/processed/bird_profiles.csv', index=False)
print("  ✓ Saved: data/processed/bird_profiles.csv")


# ============================================================================
# PART 8: SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("PHASE 2a SUMMARY")
print("=" * 70)

total = len(df)
for s in [0, 1, 2]:
    n = (df['behaviour'] == s).sum()
    print(f"  {STATE_LABELS[s]:12s}: {n:6,} points ({n/total*100:.1f}%)")

print(f"\n  Individual variation (prop. foraging):")
print(f"    Range:  {bird_profiles['prop_foraging'].min():.2f} – "
      f"{bird_profiles['prop_foraging'].max():.2f}")
print(f"    StdDev: {bird_profiles['prop_foraging'].std():.3f}")

print("\n  bird_profiles.csv ready for Phase 5 artwork generation")
print("\n" + "=" * 70)
print("PHASE 2a COMPLETE")
print("=" * 70 + "\n")