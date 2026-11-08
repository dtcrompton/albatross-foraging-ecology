# rerun_v2: repair of bird 90494 timestamps and pipeline rerun

Branch: `fix/bird-90494-dates`. Original scripts in `python/`, `data/raw/albatross_tracks.csv`, `data/processed/` and `outputs/` are untouched.

## Repair rule

For `individual-local-identifier == 90494` and `event-id` from 2172899175 to 2172902497 inclusive (3,323 contiguous rows, all stored on day 11 with seconds 00): month becomes 11 and day becomes the stored month. Time of day is unchanged.

- 3,056 rows change value and have `timestamp_repaired = true`.
- 267 rows stored as `2013-11-11` swap to themselves and have `timestamp_repaired = false`.
- All other rows, including every other bird, are unchanged.
- `data/raw/original_movebank_download.csv` is byte-identical to `data/raw/albatross_tracks.csv`, so the swap is present in the downloaded file.

## Checksums

| File | SHA-256 | In git? |
|---|---|---|
| `data/raw/albatross_tracks.csv` | `7149906a043f18d3a179cedc240cfcf6c106a7f9ca172fa2647939e7ea82dda6` | No (`.gitignore`) |
| `data/raw/albatross_tracks_corrected.csv` | `0c0fe63b54d9aad176823f24c769c3fb4db2d286625cd0ef26f217ab9bbb56e4` | No (`.gitignore`) |

The corrected file is not in any commit. Run `repair_90494_timestamps.py` to recreate it and compare with the checksum above.

## Files created

In git:

- `rerun_v2/repair_90494_timestamps.py`: writes the corrected file; refuses to overwrite.
- `rerun_v2/make_copies.py`: generates the per-run script copies by exact-string replacement and writes `rerun_v2/diffs/<run>.diff`.
- `rerun_v2/run_pipeline.sh`: runs Phases 1, 2a, 2b and 3 for one run.
- `rerun_v2/strip_audit_columns.py`: removes `timestamp_original` and `timestamp_repaired` from finished track CSVs (not used for control).
- `rerun_v2/compare_control.py`: writes `outputs_v2/control_comparison.md`.
- `rerun_v2/compare_versions.py`: writes `outputs_v2/comparison_report.md` and `outputs_v2/per_bird_comparison.csv`.
- `rerun_v2/control/`, `rerun_v2/v2/`, `rerun_v2/v3/`: script copies. `explore_data.py`, `phase2a_figures.py` and `phase4_interactive_map.py` are copied with changes applied but not run.
- `rerun_v2/logs/`: stdout of each phase.
- `outputs_v2/control/figures/`, `outputs_v2/figures/`, `outputs_v2/v3/figures/`: figures from each run.
- `outputs_v2/control_comparison.md`, `outputs_v2/comparison_report.md`, `outputs_v2/per_bird_comparison.csv`.

Local only:

- `data/raw/albatross_tracks_corrected.csv` (ignored by `.gitignore`).
- `data/processed_v2/`, `data/processed_v2/control/` and `data/processed_v3/` (listed in `.git/info/exclude`, which is untracked; `data/processed_v3/` was added to it at the start).

## Runs

| Run | Raw input | Colony point | Processed output | Figures |
|---|---|---|---|---|
| control | `albatross_tracks.csv` | 169.15E, 52.55S | `data/processed_v2/control/` | `outputs_v2/control/figures/` |
| v2 | `albatross_tracks_corrected.csv` | 169.15E, 52.55S | `data/processed_v2/` | `outputs_v2/figures/` |
| v3 | `albatross_tracks_corrected.csv` | 169.224E, 52.474S | `data/processed_v3/` | `outputs_v2/v3/figures/` |

SST and chlorophyll are read from the cached `data/environmental/*.nc` files, so Phase 2b makes no network request.

## Colony point: every hard-coded use found before any change

Changed in the v3 copies only:

- `python/phase1_movement_metrics.py:95-96`: `CAMPBELL_LON`, `CAMPBELL_LAT` (feeds `dist_from_campbell` at line 99, `at_colony` at 175, and the map marker at 256)
- `python/phase2a_behaviour_classification.py:239`: map marker
- `python/phase2a_figures.py:27-28`: constants for the map markers at lines 60 and 200
- `python/phase3_conservation_risk.py:306`: map marker
- `python/phase4_interactive_map.py:41-42`: constants for the map centre (110), colony marker (131) and fallbacks (197-198)
- `python/explore_data.py:100-101`: constants for the distance check at line 122 and printed text at 103

Left unchanged in the v3 copies:

- `python/phase3_conservation_risk.py:118,121`: comment and `NZ_EEZ_BOUNDARY = -48.8`, which the comment derives from Campbell Island's latitude. The zone logic is kept unchanged as instructed.
- `python/phase3_conservation_risk.py:148,305`: comments mentioning 169 degrees.
- `python/phase4_interactive_map.py:90`: `CENTER_LON = 169`, the longitude-normalisation centre, not a distance reference.
- `python/phase4_interactive_map.py:135`: popup text "52.5°S, 169.2°E", which is the same at this rounding for the new point.

Generated outputs containing the old point, not edited or regenerated:

- `albatross_interactive_map.html` lines 185, 208, 311, 323, 407, 455, 527 (lines with the marker, centre or popup text)
- `outputs/maps/albatross_interactive_map.html` lines 160, 183, 286, 298, 382, 430, 502
- `outputs/figures/*.png` that plot the marker, and the `data/processed/` columns computed from the point

Column `dist_from_campbell` keeps its name in v3 so the outputs have the same columns.

## Reproduce

From the repository root:

```
python3 rerun_v2/repair_90494_timestamps.py   # only if the corrected file is absent
python3 rerun_v2/make_copies.py control
python3 rerun_v2/make_copies.py v2
python3 rerun_v2/make_copies.py v3
mkdir -p data/processed_v2/control data/processed_v3
sh rerun_v2/run_pipeline.sh control
python3 rerun_v2/compare_control.py
sh rerun_v2/run_pipeline.sh v2
sh rerun_v2/run_pipeline.sh v3
python3 rerun_v2/compare_versions.py
```

## Lines that differ from the originals

Each copy differs from `python/` only in the lines below. Paths include those in docstrings and print statements. In v3, the coordinate lines listed above also differ.

### control

```diff
--- python/explore_data.py
+++ rerun_v2/control/explore_data.py
@@ -15 +15 @@
-df = pd.read_csv('data/raw/Grey-headed albatross, New Zealand (data from Torres et al. 2017).csv')
+df = pd.read_csv('data/raw/albatross_tracks.csv')
--- python/phase1_movement_metrics.py
+++ rerun_v2/control/phase1_movement_metrics.py
@@ -9,3 +9,3 @@
-    data/processed/tracks_with_metrics.csv  — full GPS data with calculated metrics
-    data/processed/trip_statistics.csv      — summary statistics per trip
-    outputs/figures/phase1_overview.png     — 4-panel summary figure
+    data/processed_v2/control/tracks_with_metrics.csv  — full GPS data with calculated metrics
+    data/processed_v2/control/trip_statistics.csv      — summary statistics per trip
+    outputs_v2/control/figures/phase1_overview.png     — 4-panel summary figure
@@ -313,2 +313,2 @@
-plt.savefig('outputs/figures/phase1_overview.png', dpi=150, bbox_inches='tight')
-print("  ✓ Saved: outputs/figures/phase1_overview.png")
+plt.savefig('outputs_v2/control/figures/phase1_overview.png', dpi=150, bbox_inches='tight')
+print("  ✓ Saved: outputs_v2/control/figures/phase1_overview.png")
@@ -323,5 +323,5 @@
-df.to_csv('data/processed/tracks_with_metrics.csv', index=False)
-print("  ✓ Saved: data/processed/tracks_with_metrics.csv")
-
-trip_stats.to_csv('data/processed/trip_statistics.csv', index=False)
-print("  ✓ Saved: data/processed/trip_statistics.csv")
+df.to_csv('data/processed_v2/control/tracks_with_metrics.csv', index=False)
+print("  ✓ Saved: data/processed_v2/control/tracks_with_metrics.csv")
+
+trip_stats.to_csv('data/processed_v2/control/trip_statistics.csv', index=False)
+print("  ✓ Saved: data/processed_v2/control/trip_statistics.csv")
--- python/phase2a_behaviour_classification.py
+++ rerun_v2/control/phase2a_behaviour_classification.py
@@ -14,3 +14,3 @@
-    data/processed/tracks_with_behaviour.csv  — GPS data + behaviour state
-    data/processed/bird_profiles.csv          — per-bird summary metrics
-    outputs/figures/phase2a_behaviour.png     — 4-panel behaviour overview
+    data/processed_v2/control/tracks_with_behaviour.csv  — GPS data + behaviour state
+    data/processed_v2/control/bird_profiles.csv          — per-bird summary metrics
+    outputs_v2/control/figures/phase2a_behaviour.png     — 4-panel behaviour overview
@@ -44 +44 @@
-df = pd.read_csv('data/processed/tracks_with_metrics.csv',
+df = pd.read_csv('data/processed_v2/control/tracks_with_metrics.csv',
@@ -311 +311 @@
-plt.savefig('outputs/figures/phase2a_behaviour.png', dpi=150,
+plt.savefig('outputs_v2/control/figures/phase2a_behaviour.png', dpi=150,
@@ -313 +313 @@
-print("  ✓ Saved: outputs/figures/phase2a_behaviour.png")
+print("  ✓ Saved: outputs_v2/control/figures/phase2a_behaviour.png")
@@ -322,5 +322,5 @@
-df.to_csv('data/processed/tracks_with_behaviour.csv', index=False)
-print("  ✓ Saved: data/processed/tracks_with_behaviour.csv")
-
-bird_profiles.to_csv('data/processed/bird_profiles.csv', index=False)
-print("  ✓ Saved: data/processed/bird_profiles.csv")
+df.to_csv('data/processed_v2/control/tracks_with_behaviour.csv', index=False)
+print("  ✓ Saved: data/processed_v2/control/tracks_with_behaviour.csv")
+
+bird_profiles.to_csv('data/processed_v2/control/bird_profiles.csv', index=False)
+print("  ✓ Saved: data/processed_v2/control/bird_profiles.csv")
--- python/phase2a_figures.py
+++ rerun_v2/control/phase2a_figures.py
@@ -6,2 +6,2 @@
-    outputs/figures/phase2a_behaviour.png   — 4-panel technical overview
-    outputs/figures/linkedin_tracks_map.png — standalone single-panel map
+    outputs_v2/control/figures/phase2a_behaviour.png   — 4-panel technical overview
+    outputs_v2/control/figures/linkedin_tracks_map.png — standalone single-panel map
@@ -31,2 +31,2 @@
-df = pd.read_csv('data/processed/tracks_with_behaviour.csv', parse_dates=['timestamp'])
-bird_profiles = pd.read_csv('data/processed/bird_profiles.csv')
+df = pd.read_csv('data/processed_v2/control/tracks_with_behaviour.csv', parse_dates=['timestamp'])
+bird_profiles = pd.read_csv('data/processed_v2/control/bird_profiles.csv')
@@ -155 +155 @@
-plt.savefig('outputs/figures/phase2a_behaviour.png', dpi=150,
+plt.savefig('outputs_v2/control/figures/phase2a_behaviour.png', dpi=150,
@@ -157 +157 @@
-print("  ✓ Saved: outputs/figures/phase2a_behaviour.png")
+print("  ✓ Saved: outputs_v2/control/figures/phase2a_behaviour.png")
@@ -233 +233 @@
-plt.savefig('outputs/figures/linkedin_tracks_map.png', dpi=200,
+plt.savefig('outputs_v2/control/figures/linkedin_tracks_map.png', dpi=200,
@@ -235 +235 @@
-print("  ✓ Saved: outputs/figures/linkedin_tracks_map.png")
+print("  ✓ Saved: outputs_v2/control/figures/linkedin_tracks_map.png")
--- python/phase2b_environmental_drivers.py
+++ rerun_v2/control/phase2b_environmental_drivers.py
@@ -13,2 +13,2 @@
-    data/processed/tracks_with_env.csv   — GPS data + sst, chla columns
-    outputs/figures/phase2b_drivers.png  — feature importance + SST plots
+    data/processed_v2/control/tracks_with_env.csv   — GPS data + sst, chla columns
+    outputs_v2/control/figures/phase2b_drivers.png  — feature importance + SST plots
@@ -47 +47 @@
-df = pd.read_csv('data/processed/tracks_with_behaviour.csv',
+df = pd.read_csv('data/processed_v2/control/tracks_with_behaviour.csv',
@@ -337 +337 @@
-plt.savefig('outputs/figures/phase2b_drivers.png', dpi=150,
+plt.savefig('outputs_v2/control/figures/phase2b_drivers.png', dpi=150,
@@ -339 +339 @@
-print("  ✓ Saved: outputs/figures/phase2b_drivers.png")
+print("  ✓ Saved: outputs_v2/control/figures/phase2b_drivers.png")
@@ -348,2 +348,2 @@
-df.to_csv('data/processed/tracks_with_env.csv', index=False)
-print("  ✓ Saved: data/processed/tracks_with_env.csv")
+df.to_csv('data/processed_v2/control/tracks_with_env.csv', index=False)
+print("  ✓ Saved: data/processed_v2/control/tracks_with_env.csv")
--- python/phase3_conservation_risk.py
+++ rerun_v2/control/phase3_conservation_risk.py
@@ -17,3 +17,3 @@
-    outputs/figures/phase3_risk_analysis.png  — 4-panel conservation figure
-    data/processed/bird_risk_profiles.csv     — per-bird risk metrics
-    data/processed/foraging_kde_grid.csv      — KDE density grid
+    outputs_v2/control/figures/phase3_risk_analysis.png  — 4-panel conservation figure
+    data/processed_v2/control/bird_risk_profiles.csv     — per-bird risk metrics
+    data/processed_v2/control/foraging_kde_grid.csv      — KDE density grid
@@ -52 +52 @@
-df       = pd.read_csv('data/processed/tracks_with_env.csv',
+df       = pd.read_csv('data/processed_v2/control/tracks_with_env.csv',
@@ -54 +54 @@
-profiles = pd.read_csv('data/processed/bird_profiles.csv')
+profiles = pd.read_csv('data/processed_v2/control/bird_profiles.csv')
@@ -184,2 +184,2 @@
-kde_df.to_csv('data/processed/foraging_kde_grid.csv', index=False)
-print("  ✓ Saved: data/processed/foraging_kde_grid.csv")
+kde_df.to_csv('data/processed_v2/control/foraging_kde_grid.csv', index=False)
+print("  ✓ Saved: data/processed_v2/control/foraging_kde_grid.csv")
@@ -275,2 +275,2 @@
-profiles.to_csv('data/processed/bird_risk_profiles.csv', index=False)
-print("\n  ✓ Saved: data/processed/bird_risk_profiles.csv")
+profiles.to_csv('data/processed_v2/control/bird_risk_profiles.csv', index=False)
+print("\n  ✓ Saved: data/processed_v2/control/bird_risk_profiles.csv")
@@ -420 +420 @@
-plt.savefig('outputs/figures/phase3_risk_analysis.png', dpi=150,
+plt.savefig('outputs_v2/control/figures/phase3_risk_analysis.png', dpi=150,
@@ -422 +422 @@
-print("  ✓ Saved: outputs/figures/phase3_risk_analysis.png")
+print("  ✓ Saved: outputs_v2/control/figures/phase3_risk_analysis.png")
--- python/phase4_interactive_map.py
+++ rerun_v2/control/phase4_interactive_map.py
@@ -14 +14 @@
-    outputs/maps/albatross_interactive_map.html
+    outputs_v2/control/maps/albatross_interactive_map.html
@@ -23 +23 @@
-Path('outputs/maps').mkdir(parents=True, exist_ok=True)
+Path('outputs_v2/control/maps').mkdir(parents=True, exist_ok=True)
@@ -55 +55 @@
-df       = pd.read_csv('data/processed/tracks_with_behaviour.csv',
+df       = pd.read_csv('data/processed_v2/control/tracks_with_behaviour.csv',
@@ -57 +57 @@
-profiles = pd.read_csv('data/processed/bird_risk_profiles.csv')
+profiles = pd.read_csv('data/processed_v2/control/bird_risk_profiles.csv')
@@ -401 +401 @@
-out_path = 'outputs/maps/albatross_interactive_map.html'
+out_path = 'outputs_v2/control/maps/albatross_interactive_map.html'
@@ -424 +424 @@
-    open outputs/maps/albatross_interactive_map.html
+    open outputs_v2/control/maps/albatross_interactive_map.html
```

### v2

```diff
--- python/explore_data.py
+++ rerun_v2/v2/explore_data.py
@@ -15 +15 @@
-df = pd.read_csv('data/raw/Grey-headed albatross, New Zealand (data from Torres et al. 2017).csv')
+df = pd.read_csv('data/raw/albatross_tracks_corrected.csv')
--- python/phase1_movement_metrics.py
+++ rerun_v2/v2/phase1_movement_metrics.py
@@ -9,3 +9,3 @@
-    data/processed/tracks_with_metrics.csv  — full GPS data with calculated metrics
-    data/processed/trip_statistics.csv      — summary statistics per trip
-    outputs/figures/phase1_overview.png     — 4-panel summary figure
+    data/processed_v2/tracks_with_metrics.csv  — full GPS data with calculated metrics
+    data/processed_v2/trip_statistics.csv      — summary statistics per trip
+    outputs_v2/figures/phase1_overview.png     — 4-panel summary figure
@@ -32 +32 @@
-df = pd.read_csv('data/raw/albatross_tracks.csv')
+df = pd.read_csv('data/raw/albatross_tracks_corrected.csv')
@@ -313,2 +313,2 @@
-plt.savefig('outputs/figures/phase1_overview.png', dpi=150, bbox_inches='tight')
-print("  ✓ Saved: outputs/figures/phase1_overview.png")
+plt.savefig('outputs_v2/figures/phase1_overview.png', dpi=150, bbox_inches='tight')
+print("  ✓ Saved: outputs_v2/figures/phase1_overview.png")
@@ -323,5 +323,5 @@
-df.to_csv('data/processed/tracks_with_metrics.csv', index=False)
-print("  ✓ Saved: data/processed/tracks_with_metrics.csv")
-
-trip_stats.to_csv('data/processed/trip_statistics.csv', index=False)
-print("  ✓ Saved: data/processed/trip_statistics.csv")
+df.to_csv('data/processed_v2/tracks_with_metrics.csv', index=False)
+print("  ✓ Saved: data/processed_v2/tracks_with_metrics.csv")
+
+trip_stats.to_csv('data/processed_v2/trip_statistics.csv', index=False)
+print("  ✓ Saved: data/processed_v2/trip_statistics.csv")
--- python/phase2a_behaviour_classification.py
+++ rerun_v2/v2/phase2a_behaviour_classification.py
@@ -14,3 +14,3 @@
-    data/processed/tracks_with_behaviour.csv  — GPS data + behaviour state
-    data/processed/bird_profiles.csv          — per-bird summary metrics
-    outputs/figures/phase2a_behaviour.png     — 4-panel behaviour overview
+    data/processed_v2/tracks_with_behaviour.csv  — GPS data + behaviour state
+    data/processed_v2/bird_profiles.csv          — per-bird summary metrics
+    outputs_v2/figures/phase2a_behaviour.png     — 4-panel behaviour overview
@@ -44 +44 @@
-df = pd.read_csv('data/processed/tracks_with_metrics.csv',
+df = pd.read_csv('data/processed_v2/tracks_with_metrics.csv',
@@ -311 +311 @@
-plt.savefig('outputs/figures/phase2a_behaviour.png', dpi=150,
+plt.savefig('outputs_v2/figures/phase2a_behaviour.png', dpi=150,
@@ -313 +313 @@
-print("  ✓ Saved: outputs/figures/phase2a_behaviour.png")
+print("  ✓ Saved: outputs_v2/figures/phase2a_behaviour.png")
@@ -322,5 +322,5 @@
-df.to_csv('data/processed/tracks_with_behaviour.csv', index=False)
-print("  ✓ Saved: data/processed/tracks_with_behaviour.csv")
-
-bird_profiles.to_csv('data/processed/bird_profiles.csv', index=False)
-print("  ✓ Saved: data/processed/bird_profiles.csv")
+df.to_csv('data/processed_v2/tracks_with_behaviour.csv', index=False)
+print("  ✓ Saved: data/processed_v2/tracks_with_behaviour.csv")
+
+bird_profiles.to_csv('data/processed_v2/bird_profiles.csv', index=False)
+print("  ✓ Saved: data/processed_v2/bird_profiles.csv")
--- python/phase2a_figures.py
+++ rerun_v2/v2/phase2a_figures.py
@@ -6,2 +6,2 @@
-    outputs/figures/phase2a_behaviour.png   — 4-panel technical overview
-    outputs/figures/linkedin_tracks_map.png — standalone single-panel map
+    outputs_v2/figures/phase2a_behaviour.png   — 4-panel technical overview
+    outputs_v2/figures/linkedin_tracks_map.png — standalone single-panel map
@@ -31,2 +31,2 @@
-df = pd.read_csv('data/processed/tracks_with_behaviour.csv', parse_dates=['timestamp'])
-bird_profiles = pd.read_csv('data/processed/bird_profiles.csv')
+df = pd.read_csv('data/processed_v2/tracks_with_behaviour.csv', parse_dates=['timestamp'])
+bird_profiles = pd.read_csv('data/processed_v2/bird_profiles.csv')
@@ -155 +155 @@
-plt.savefig('outputs/figures/phase2a_behaviour.png', dpi=150,
+plt.savefig('outputs_v2/figures/phase2a_behaviour.png', dpi=150,
@@ -157 +157 @@
-print("  ✓ Saved: outputs/figures/phase2a_behaviour.png")
+print("  ✓ Saved: outputs_v2/figures/phase2a_behaviour.png")
@@ -233 +233 @@
-plt.savefig('outputs/figures/linkedin_tracks_map.png', dpi=200,
+plt.savefig('outputs_v2/figures/linkedin_tracks_map.png', dpi=200,
@@ -235 +235 @@
-print("  ✓ Saved: outputs/figures/linkedin_tracks_map.png")
+print("  ✓ Saved: outputs_v2/figures/linkedin_tracks_map.png")
--- python/phase2b_environmental_drivers.py
+++ rerun_v2/v2/phase2b_environmental_drivers.py
@@ -13,2 +13,2 @@
-    data/processed/tracks_with_env.csv   — GPS data + sst, chla columns
-    outputs/figures/phase2b_drivers.png  — feature importance + SST plots
+    data/processed_v2/tracks_with_env.csv   — GPS data + sst, chla columns
+    outputs_v2/figures/phase2b_drivers.png  — feature importance + SST plots
@@ -47 +47 @@
-df = pd.read_csv('data/processed/tracks_with_behaviour.csv',
+df = pd.read_csv('data/processed_v2/tracks_with_behaviour.csv',
@@ -337 +337 @@
-plt.savefig('outputs/figures/phase2b_drivers.png', dpi=150,
+plt.savefig('outputs_v2/figures/phase2b_drivers.png', dpi=150,
@@ -339 +339 @@
-print("  ✓ Saved: outputs/figures/phase2b_drivers.png")
+print("  ✓ Saved: outputs_v2/figures/phase2b_drivers.png")
@@ -348,2 +348,2 @@
-df.to_csv('data/processed/tracks_with_env.csv', index=False)
-print("  ✓ Saved: data/processed/tracks_with_env.csv")
+df.to_csv('data/processed_v2/tracks_with_env.csv', index=False)
+print("  ✓ Saved: data/processed_v2/tracks_with_env.csv")
--- python/phase3_conservation_risk.py
+++ rerun_v2/v2/phase3_conservation_risk.py
@@ -17,3 +17,3 @@
-    outputs/figures/phase3_risk_analysis.png  — 4-panel conservation figure
-    data/processed/bird_risk_profiles.csv     — per-bird risk metrics
-    data/processed/foraging_kde_grid.csv      — KDE density grid
+    outputs_v2/figures/phase3_risk_analysis.png  — 4-panel conservation figure
+    data/processed_v2/bird_risk_profiles.csv     — per-bird risk metrics
+    data/processed_v2/foraging_kde_grid.csv      — KDE density grid
@@ -52 +52 @@
-df       = pd.read_csv('data/processed/tracks_with_env.csv',
+df       = pd.read_csv('data/processed_v2/tracks_with_env.csv',
@@ -54 +54 @@
-profiles = pd.read_csv('data/processed/bird_profiles.csv')
+profiles = pd.read_csv('data/processed_v2/bird_profiles.csv')
@@ -184,2 +184,2 @@
-kde_df.to_csv('data/processed/foraging_kde_grid.csv', index=False)
-print("  ✓ Saved: data/processed/foraging_kde_grid.csv")
+kde_df.to_csv('data/processed_v2/foraging_kde_grid.csv', index=False)
+print("  ✓ Saved: data/processed_v2/foraging_kde_grid.csv")
@@ -275,2 +275,2 @@
-profiles.to_csv('data/processed/bird_risk_profiles.csv', index=False)
-print("\n  ✓ Saved: data/processed/bird_risk_profiles.csv")
+profiles.to_csv('data/processed_v2/bird_risk_profiles.csv', index=False)
+print("\n  ✓ Saved: data/processed_v2/bird_risk_profiles.csv")
@@ -420 +420 @@
-plt.savefig('outputs/figures/phase3_risk_analysis.png', dpi=150,
+plt.savefig('outputs_v2/figures/phase3_risk_analysis.png', dpi=150,
@@ -422 +422 @@
-print("  ✓ Saved: outputs/figures/phase3_risk_analysis.png")
+print("  ✓ Saved: outputs_v2/figures/phase3_risk_analysis.png")
--- python/phase4_interactive_map.py
+++ rerun_v2/v2/phase4_interactive_map.py
@@ -14 +14 @@
-    outputs/maps/albatross_interactive_map.html
+    outputs_v2/maps/albatross_interactive_map.html
@@ -23 +23 @@
-Path('outputs/maps').mkdir(parents=True, exist_ok=True)
+Path('outputs_v2/maps').mkdir(parents=True, exist_ok=True)
@@ -55 +55 @@
-df       = pd.read_csv('data/processed/tracks_with_behaviour.csv',
+df       = pd.read_csv('data/processed_v2/tracks_with_behaviour.csv',
@@ -57 +57 @@
-profiles = pd.read_csv('data/processed/bird_risk_profiles.csv')
+profiles = pd.read_csv('data/processed_v2/bird_risk_profiles.csv')
@@ -401 +401 @@
-out_path = 'outputs/maps/albatross_interactive_map.html'
+out_path = 'outputs_v2/maps/albatross_interactive_map.html'
@@ -424 +424 @@
-    open outputs/maps/albatross_interactive_map.html
+    open outputs_v2/maps/albatross_interactive_map.html
```

### v3

```diff
--- python/explore_data.py
+++ rerun_v2/v3/explore_data.py
@@ -15 +15 @@
-df = pd.read_csv('data/raw/Grey-headed albatross, New Zealand (data from Torres et al. 2017).csv')
+df = pd.read_csv('data/raw/albatross_tracks_corrected.csv')
@@ -100,2 +100,2 @@
-    campbell_lat = -52.55
-    campbell_lon = 169.15
+    campbell_lat = -52.474
+    campbell_lon = 169.224
--- python/phase1_movement_metrics.py
+++ rerun_v2/v3/phase1_movement_metrics.py
@@ -9,3 +9,3 @@
-    data/processed/tracks_with_metrics.csv  — full GPS data with calculated metrics
-    data/processed/trip_statistics.csv      — summary statistics per trip
-    outputs/figures/phase1_overview.png     — 4-panel summary figure
+    data/processed_v3/tracks_with_metrics.csv  — full GPS data with calculated metrics
+    data/processed_v3/trip_statistics.csv      — summary statistics per trip
+    outputs_v2/v3/figures/phase1_overview.png     — 4-panel summary figure
@@ -32 +32 @@
-df = pd.read_csv('data/raw/albatross_tracks.csv')
+df = pd.read_csv('data/raw/albatross_tracks_corrected.csv')
@@ -95,2 +95,2 @@
-CAMPBELL_LON = 169.15
-CAMPBELL_LAT = -52.55
+CAMPBELL_LON = 169.224
+CAMPBELL_LAT = -52.474
@@ -313,2 +313,2 @@
-plt.savefig('outputs/figures/phase1_overview.png', dpi=150, bbox_inches='tight')
-print("  ✓ Saved: outputs/figures/phase1_overview.png")
+plt.savefig('outputs_v2/v3/figures/phase1_overview.png', dpi=150, bbox_inches='tight')
+print("  ✓ Saved: outputs_v2/v3/figures/phase1_overview.png")
@@ -323,5 +323,5 @@
-df.to_csv('data/processed/tracks_with_metrics.csv', index=False)
-print("  ✓ Saved: data/processed/tracks_with_metrics.csv")
-
-trip_stats.to_csv('data/processed/trip_statistics.csv', index=False)
-print("  ✓ Saved: data/processed/trip_statistics.csv")
+df.to_csv('data/processed_v3/tracks_with_metrics.csv', index=False)
+print("  ✓ Saved: data/processed_v3/tracks_with_metrics.csv")
+
+trip_stats.to_csv('data/processed_v3/trip_statistics.csv', index=False)
+print("  ✓ Saved: data/processed_v3/trip_statistics.csv")
--- python/phase2a_behaviour_classification.py
+++ rerun_v2/v3/phase2a_behaviour_classification.py
@@ -14,3 +14,3 @@
-    data/processed/tracks_with_behaviour.csv  — GPS data + behaviour state
-    data/processed/bird_profiles.csv          — per-bird summary metrics
-    outputs/figures/phase2a_behaviour.png     — 4-panel behaviour overview
+    data/processed_v3/tracks_with_behaviour.csv  — GPS data + behaviour state
+    data/processed_v3/bird_profiles.csv          — per-bird summary metrics
+    outputs_v2/v3/figures/phase2a_behaviour.png     — 4-panel behaviour overview
@@ -44 +44 @@
-df = pd.read_csv('data/processed/tracks_with_metrics.csv',
+df = pd.read_csv('data/processed_v3/tracks_with_metrics.csv',
@@ -239 +239 @@
-ax1.scatter(169.15, -52.55, c='white', s=200, marker='*',
+ax1.scatter(169.224, -52.474, c='white', s=200, marker='*',
@@ -311 +311 @@
-plt.savefig('outputs/figures/phase2a_behaviour.png', dpi=150,
+plt.savefig('outputs_v2/v3/figures/phase2a_behaviour.png', dpi=150,
@@ -313 +313 @@
-print("  ✓ Saved: outputs/figures/phase2a_behaviour.png")
+print("  ✓ Saved: outputs_v2/v3/figures/phase2a_behaviour.png")
@@ -322,5 +322,5 @@
-df.to_csv('data/processed/tracks_with_behaviour.csv', index=False)
-print("  ✓ Saved: data/processed/tracks_with_behaviour.csv")
-
-bird_profiles.to_csv('data/processed/bird_profiles.csv', index=False)
-print("  ✓ Saved: data/processed/bird_profiles.csv")
+df.to_csv('data/processed_v3/tracks_with_behaviour.csv', index=False)
+print("  ✓ Saved: data/processed_v3/tracks_with_behaviour.csv")
+
+bird_profiles.to_csv('data/processed_v3/bird_profiles.csv', index=False)
+print("  ✓ Saved: data/processed_v3/bird_profiles.csv")
--- python/phase2a_figures.py
+++ rerun_v2/v3/phase2a_figures.py
@@ -6,2 +6,2 @@
-    outputs/figures/phase2a_behaviour.png   — 4-panel technical overview
-    outputs/figures/linkedin_tracks_map.png — standalone single-panel map
+    outputs_v2/v3/figures/phase2a_behaviour.png   — 4-panel technical overview
+    outputs_v2/v3/figures/linkedin_tracks_map.png — standalone single-panel map
@@ -27,2 +27,2 @@
-CAMPBELL_LON = 169.15
-CAMPBELL_LAT = -52.55
+CAMPBELL_LON = 169.224
+CAMPBELL_LAT = -52.474
@@ -31,2 +31,2 @@
-df = pd.read_csv('data/processed/tracks_with_behaviour.csv', parse_dates=['timestamp'])
-bird_profiles = pd.read_csv('data/processed/bird_profiles.csv')
+df = pd.read_csv('data/processed_v3/tracks_with_behaviour.csv', parse_dates=['timestamp'])
+bird_profiles = pd.read_csv('data/processed_v3/bird_profiles.csv')
@@ -155 +155 @@
-plt.savefig('outputs/figures/phase2a_behaviour.png', dpi=150,
+plt.savefig('outputs_v2/v3/figures/phase2a_behaviour.png', dpi=150,
@@ -157 +157 @@
-print("  ✓ Saved: outputs/figures/phase2a_behaviour.png")
+print("  ✓ Saved: outputs_v2/v3/figures/phase2a_behaviour.png")
@@ -233 +233 @@
-plt.savefig('outputs/figures/linkedin_tracks_map.png', dpi=200,
+plt.savefig('outputs_v2/v3/figures/linkedin_tracks_map.png', dpi=200,
@@ -235 +235 @@
-print("  ✓ Saved: outputs/figures/linkedin_tracks_map.png")
+print("  ✓ Saved: outputs_v2/v3/figures/linkedin_tracks_map.png")
--- python/phase2b_environmental_drivers.py
+++ rerun_v2/v3/phase2b_environmental_drivers.py
@@ -13,2 +13,2 @@
-    data/processed/tracks_with_env.csv   — GPS data + sst, chla columns
-    outputs/figures/phase2b_drivers.png  — feature importance + SST plots
+    data/processed_v3/tracks_with_env.csv   — GPS data + sst, chla columns
+    outputs_v2/v3/figures/phase2b_drivers.png  — feature importance + SST plots
@@ -47 +47 @@
-df = pd.read_csv('data/processed/tracks_with_behaviour.csv',
+df = pd.read_csv('data/processed_v3/tracks_with_behaviour.csv',
@@ -337 +337 @@
-plt.savefig('outputs/figures/phase2b_drivers.png', dpi=150,
+plt.savefig('outputs_v2/v3/figures/phase2b_drivers.png', dpi=150,
@@ -339 +339 @@
-print("  ✓ Saved: outputs/figures/phase2b_drivers.png")
+print("  ✓ Saved: outputs_v2/v3/figures/phase2b_drivers.png")
@@ -348,2 +348,2 @@
-df.to_csv('data/processed/tracks_with_env.csv', index=False)
-print("  ✓ Saved: data/processed/tracks_with_env.csv")
+df.to_csv('data/processed_v3/tracks_with_env.csv', index=False)
+print("  ✓ Saved: data/processed_v3/tracks_with_env.csv")
--- python/phase3_conservation_risk.py
+++ rerun_v2/v3/phase3_conservation_risk.py
@@ -17,3 +17,3 @@
-    outputs/figures/phase3_risk_analysis.png  — 4-panel conservation figure
-    data/processed/bird_risk_profiles.csv     — per-bird risk metrics
-    data/processed/foraging_kde_grid.csv      — KDE density grid
+    outputs_v2/v3/figures/phase3_risk_analysis.png  — 4-panel conservation figure
+    data/processed_v3/bird_risk_profiles.csv     — per-bird risk metrics
+    data/processed_v3/foraging_kde_grid.csv      — KDE density grid
@@ -52 +52 @@
-df       = pd.read_csv('data/processed/tracks_with_env.csv',
+df       = pd.read_csv('data/processed_v3/tracks_with_env.csv',
@@ -54 +54 @@
-profiles = pd.read_csv('data/processed/bird_profiles.csv')
+profiles = pd.read_csv('data/processed_v3/bird_profiles.csv')
@@ -184,2 +184,2 @@
-kde_df.to_csv('data/processed/foraging_kde_grid.csv', index=False)
-print("  ✓ Saved: data/processed/foraging_kde_grid.csv")
+kde_df.to_csv('data/processed_v3/foraging_kde_grid.csv', index=False)
+print("  ✓ Saved: data/processed_v3/foraging_kde_grid.csv")
@@ -275,2 +275,2 @@
-profiles.to_csv('data/processed/bird_risk_profiles.csv', index=False)
-print("\n  ✓ Saved: data/processed/bird_risk_profiles.csv")
+profiles.to_csv('data/processed_v3/bird_risk_profiles.csv', index=False)
+print("\n  ✓ Saved: data/processed_v3/bird_risk_profiles.csv")
@@ -306 +306 @@
-ax1.scatter(169.15, -52.55, c=DARK_TEXT, s=200, marker='*',
+ax1.scatter(169.224, -52.474, c=DARK_TEXT, s=200, marker='*',
@@ -420 +420 @@
-plt.savefig('outputs/figures/phase3_risk_analysis.png', dpi=150,
+plt.savefig('outputs_v2/v3/figures/phase3_risk_analysis.png', dpi=150,
@@ -422 +422 @@
-print("  ✓ Saved: outputs/figures/phase3_risk_analysis.png")
+print("  ✓ Saved: outputs_v2/v3/figures/phase3_risk_analysis.png")
--- python/phase4_interactive_map.py
+++ rerun_v2/v3/phase4_interactive_map.py
@@ -14 +14 @@
-    outputs/maps/albatross_interactive_map.html
+    outputs_v2/v3/maps/albatross_interactive_map.html
@@ -23 +23 @@
-Path('outputs/maps').mkdir(parents=True, exist_ok=True)
+Path('outputs_v2/v3/maps').mkdir(parents=True, exist_ok=True)
@@ -41,2 +41,2 @@
-CAMPBELL_LAT =  -52.55
-CAMPBELL_LON =  169.15
+CAMPBELL_LAT =  -52.474
+CAMPBELL_LON =  169.224
@@ -55 +55 @@
-df       = pd.read_csv('data/processed/tracks_with_behaviour.csv',
+df       = pd.read_csv('data/processed_v3/tracks_with_behaviour.csv',
@@ -57 +57 @@
-profiles = pd.read_csv('data/processed/bird_risk_profiles.csv')
+profiles = pd.read_csv('data/processed_v3/bird_risk_profiles.csv')
@@ -401 +401 @@
-out_path = 'outputs/maps/albatross_interactive_map.html'
+out_path = 'outputs_v2/v3/maps/albatross_interactive_map.html'
@@ -424 +424 @@
-    open outputs/maps/albatross_interactive_map.html
+    open outputs_v2/v3/maps/albatross_interactive_map.html
```
