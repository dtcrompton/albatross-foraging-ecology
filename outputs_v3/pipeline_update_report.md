# Pipeline update report (8 November 2026)

Numbers and evidence only.

## Commits on `fix/pipeline-corrected`

| Commit | Message |
|---|---|
| `459237f` | Make pipeline use corrected dates, deployment-site colony point and real EEZ classification |
| `7d3b9ea` | Fix foraging-centre longitude to use a circular mean |
| `ca228c7` | Regenerate figures and map with EEZ outlines from corrected pipeline |

The README commit containing this report follows these. Commit messages have no trailer lines.

## Commit message rewrite

Only the messages changed: the `Co-Authored-By` lines were removed from the three existing commits. Trees, authors and dates were preserved, and `git diff` between each branch head and its backup tag was empty at the time of the rewrite. No force flag was used; each branch was moved with `git update-ref` against its expected old value.

| Old commit | New commit | Subject |
|---|---|---|
| `18fcd4abd5a3e3afec9995f2be4ba19e7d653775` | `0b08258610f8e7970666efeff23cf575ee5520b4` | Add pipeline copies, repair script and control run for corrected 90494 timestamps |
| `4de2269a94e426f9370b546e417d928d68b1b1d3` | `40d142bd4ef6b0fdf04c5fd7e8d00581182a0171` | Rerun pipeline on corrected data with deployment-site colony point and add three-way comparison report |
| `0fce43d3032af35722fa46b0bb32b215615e072a` | `da90f8e651d3b78a5a042b090d6f9d5e3a47993f` | Test tracks against World EEZ v12 boundaries and add jurisdiction classification report |

Backup tags (local, not pushed; these keep the old commits with their trailers):

- `backup/fix-bird-90494-dates-pre-message-rewrite` at `4de2269a94e426f9370b546e417d928d68b1b1d3`
- `backup/fix-eez-test-pre-message-rewrite` at `0fce43d3032af35722fa46b0bb32b215615e072a`
- `backup/fix-pipeline-corrected-pre-message-rewrite` at `0fce43d3032af35722fa46b0bb32b215615e072a`

Other tag: `pre-correction-2026-11-08` at `6fa773281baf8bdb60f45260644f42c841005579` (`main`, unchanged; local, not pushed).

## Files changed

New: `python/phase0_repair_dates.py`, `python/colony.py`, `python/eez_classification.py`, `outputs_v3/portfolio_assets/`, this report.

Changed: all scripts in `python/`, the five figures in `outputs/figures/`, `outputs/maps/albatross_interactive_map.html`, `README.md`.

Not in git: `data/raw/albatross_tracks_corrected.csv`, `data/processed/` (now including `eez_zone_summary.csv`), `data/external/`, and the archive below.

Source files unchanged: `data/raw/albatross_tracks.csv` SHA-256 starts `7149906a`.

## Archive

`data/processed/` was not tracked, so its seven CSVs were copied to `data/archive_pre_correction_2026-11-08/` (93 MB, listed in `.git/info/exclude`) and compared with `cmp` before any overwrite.

## Verification

**First run, before the foraging-centre fix** (Phases 0, 1, 2a, 2b, 3 from the raw file), compared with `data/processed_v3/`: all seven CSVs byte-identical, with 93,474 rows in the track files, 24 in the profile files, 24 in `trip_statistics.csv` and 45,000 in the KDE grid. No differences to explain.

Phase 3 classification against `outputs_v3/eez/fix_classification.csv`: 0 zone mismatches and 0 south-of-60S mismatches across 93,474 fixes. Foraging fixes: 38,379; New Zealand EEZ 1,043 (2.72%); outside all EEZs 37,336 (97.28%); south of 60S 362 (0.94%).

**Second run, after the foraging-centre fix:** five CSVs remain byte-identical to `data/processed_v3/`. `bird_profiles.csv` and `bird_risk_profiles.csv` differ only in `forage_centre_lon`. `risk_cluster`, `risk_label` and `risk_score` are unchanged.

## Foraging-centre longitude

Method: circular mean, normalised around longitude 169 (range -11 to 349), in `python/colony.py`, called from Phase 2a. Popups now label north, south, east and west.

Columns changed: `forage_centre_lon` in `bird_profiles.csv` and `bird_risk_profiles.csv`. No other column or file in `data/processed/` changed. It shifts by more than 5 degrees for 18 of 24 birds.

Every use of `forage_centre_lon` in this repository's real scripts:

- `python/phase2a_behaviour_classification.py`: computes it and writes `bird_profiles.csv`.
- `python/phase3_conservation_risk.py`: passes it through to `bird_risk_profiles.csv`; not a clustering feature (`forage_centre_lat` is).
- `python/phase4_interactive_map.py`: the risk lookup, the popup text and the marker position.

The frozen copies in `rerun_v2/` and the `data/processed_v3/` files keep the old values.

**Correction to the checkpoint.** The checkpoint said the regenerated map would still show misplaced markers. That was wrong: `centres_group` was built but never added to the map, so the markers and popups have never appeared, on `main` or on this branch. To make the requested popup fix visible, one line (`centres_group.add_to(m)`) was added, so the "Foraging centres" layer is visible for the first time. Remove that line to undo it.

| Bird | Old `forage_centre_lon` | New `forage_centre_lon` |
|---|---|---|
| 1 | 95.135 | 177.8676 |
| 2 | -76.0486 | 183.8815 |
| 23058 | -126.5115 | 180.3408 |
| 23059 | 176.9093 | 176.9099 |
| 23096 | -140.5625 | 183.0656 |
| 23782 | -99.138 | 180.2405 |
| 29155 | 171.5941 | 171.5942 |
| 41269 | -142.8211 | 182.0552 |
| 49364 | 168.3026 | 168.3025 |
| 58565 | -85.3865 | 182.1573 |
| 61696 | 117.7689 | 177.7698 |
| 62093 | 169.3493 | 169.3471 |
| 82589 | -121.7462 | 181.5204 |
| 89518 | -130.3592 | 186.1564 |
| 89570 | 170.8231 | 170.8225 |
| 90282 | -80.1786 | 179.8849 |
| 90287 | -159.1786 | 184.0001 |
| 90407 | -153.0603 | 181.4828 |
| 90420 | -112.1247 | 182.6365 |
| 90434 | 177.4016 | 177.4018 |
| 90468 | 39.0209 | 179.0117 |
| 90493 | -144.2534 | 203.9879 |
| 90494 | -102.6697 | 181.3113 |
| 90590 | -143.7268 | 183.547 |

## Figures and map

Before and after sizes and what changed: `outputs_v3/portfolio_assets/MANIFEST.md`. Map: 1,886,849 bytes before, 1,935,916 bytes after.

- **EEZ layer:** "EEZ outlines (World EEZ v12, Marine Regions)", toggleable, 4 features (New Zealand; Australia; Australia, Macquarie Island; Australia, Norfolk Island). Drawn as outer rings plus non-land pockets, without coastlines and without the edge at 180 degrees.
- **Simplification:** tolerance 0.01 degrees, about 1.1 km north-south. Vertices 21,876 reduced to 848, about 17 KB of coordinates. New Zealand outer ring 6,708 vertices reduced to 278, Hausdorff distance from the original 0.0103 degrees.
- **Credit:** in the map attribution line, as specified.
- **CCAMLR boundary drawn:** a dashed polyline at latitude -60 from normalised longitude -11 to 349 in 5 degree steps, named "CCAMLR boundary (60°S, approximate)", left as it was. It runs all the way round the map, beyond the 150E eastward to 50W sector.
- **CCAMLR effort circles:** not drawn; legend entry removed; code kept with a comment.
- **CARTO key:** handled as before, as a hard-coded query string in the tile URL at `python/phase4_interactive_map.py`, so it also appears in the generated HTML files, including the `portfolio_assets` copy. The value is not shown here.
- **Checks:** the map's JavaScript passes `node --check`; layer names, legend counts (13 / 8 / 3), 24 popups and the attribution order were checked in the HTML. The map was **not opened in a browser**, because the network was not to be used and its libraries load from CDNs.

## README edits

**Old:**

```
**A four-phase GIS and conservation data science project analysing GPS tracking data from 24 grey-headed albatrosses (*Thalassarche chrysostoma*) breeding at Campbell Island, New Zealand.**
```

**New:**

```
**A four-phase GIS and conservation data science project analysing GPS tracking data from 24 grey-headed albatrosses (*Thalassarche chrysostoma*) at Campbell Island, New Zealand. The 24 birds are adults recorded as incubating in the Movebank reference data, tracked with igotU GT-600 loggers (one fix every 5 minutes) between 14 October and 12 December 2013, with away trips of 7.6 to 21.8 days (mean 14.8 days).**
```

**Old:**

```
Using movement ecology methods, satellite-derived oceanographic data, and Southern Ocean fisheries records, this project identifies where and when these birds forage, what drives their habitat selection, and which individuals face the highest risk of overlap with longline fishing operations.
```

**New:**

```
Using movement ecology methods and satellite-derived oceanographic data, this project classifies behaviour from movement, relates it to environmental variables, and reports where foraging fixes fall relative to exclusive economic zone boundaries and the 60°S line.
```

**Old:**

```
- **Individual foraging strategies vary dramatically** — maximum foraging range spans from 745 km to 2,715 km across 24 birds from the same colony. Some birds spend 59% of their tracked time actively foraging; others just 33%.
```

**New:**

```
- **Maximum distance from the colony** ranges from 746 km to 2,713 km across the 24 birds (3.6x). The foraging share of fixes ranges from 33% to 59%, and total distance from 3,465 km to 12,285 km.
```

**Old:**

```
- **Behaviour is classifiable from movement alone** — a Hidden Markov Model fitted to step length and turning angle cleanly separates three states: resting (26.9%), foraging area-restricted search (41.1%), and transiting (32.0%). The foraging signal is particularly strong: mean turning angle of 62.2° vs 9.9° for transit.
```

**New:**

```
- **Behaviour was classified from movement** using a Hidden Markov Model fitted to step length and turning angle, with three states: resting (26.9% of fixes), foraging area-restricted search (41.1%), and transiting (32.1%). Mean turning angle is 62.2° in the foraging state and 9.9° in the transiting state.
```

**Old:**

```
- **Spatial fidelity outweighs environmental tracking** — a Random Forest model predicts foraging behaviour from five variables. Distance from colony (0.31) and latitude/longitude (0.43 combined) are more predictive than SST (0.15) and chlorophyll-a (0.11), suggesting birds use learned spatial knowledge of productive zones rather than real-time environmental tracking.
```

**New:**

```
(removed)
```

**Old:**

```
- **99.1% of foraging occurs outside CCAMLR waters** — the birds forage almost entirely in New Zealand's Exclusive Economic Zone and adjacent subantarctic waters (north of 60°S). Bycatch risk from longline fisheries is primarily a matter for New Zealand's Ministry for Primary Industries and SPRFMO, not CCAMLR.
```

**New:**

```
- Of 38,379 foraging fixes from 24 incubating adults tracked in 2013, 97.3% fell outside every country's exclusive economic zone and 2.7% fell inside New Zealand's. 99.1% fell north of 60°S, outside the CCAMLR Convention Area.
```

**Old:**

```
- **Temporal synchrony with CCAMLR longline effort is moderate (0.31)** — peak bird foraging activity (October–November) does not strongly coincide with peak CCAMLR longline effort (January), though December presents a risk window where both are active.
```

**New:**

```
- **Temporal synchrony index: 0.295.** It is computed against all CCAMLR longline effort worldwide with no area filter and is not a measure of overlap.
```

**Old:**

```
- **Three birds carry disproportionate risk** — birds 2, 89518, and 90493 form a distinct high-risk cluster, ranging 2,300–2,715 km from Campbell Island, covering 10,500–12,285 km total. Individual specialisation in foraging strategy appears persistent, suggesting these individuals are chronically rather than incidentally exposed.
```

**New:**

```
- **K-means clustering** of four foraging-strategy metrics gives cluster sizes of 13 low, 8 medium and 3 high risk. The high-risk cluster is birds 2, 89518 and 90493, with maximum distances of 2,319 to 2,713 km and total distances of 9,713 to 12,285 km. The clustering uses no fishing data.
```

**Old:**

```
| GPS tracking data | Torres et al. (2017), Movebank Data Repository. DOI: [10.5441/001/1.694p666h](https://doi.org/10.5441/001/1.694p666h) | 93,474 GPS fixes, 24 birds, 2013 |
```

**New:**

```
| GPS tracking data | Thompson et al. (2017), Movebank Data Repository (see Data citations) | 93,474 GPS fixes, 24 birds, 14 October to 12 December 2013 |
```

**Old:**

```
| Fishing effort | CCAMLR Statistical Bulletin Vol. 37, [ccamlr.org](https://www.ccamlr.org) | Longline (LLS) gear, 2013 |
```

**New:**

```
| Fishing effort | CCAMLR Statistical Bulletin Vol. 37, [ccamlr.org](https://www.ccamlr.org) | Longline (LLS) gear, 2013 |
| EEZ boundaries | World EEZ v12, Flanders Marine Institute (see Data citations) | Point-in-polygon test and map outlines |
```

**Old:**

```
(new section before "## Data Sources")
```

**New:**

```
## Data Correction (8 November 2026)
Bird 90494's timestamps in the source file, as downloaded from the Movebank Data Repository, had day and month swapped on 3,056 fixes (3.3% of the data). The same swap appears in that bird's deployment date in the Movebank reference data. The swap was repaired using event-id order, the source file is unchanged, the repair script (`python/phase0_repair_dates.py`) and rule are in this repository, and the pipeline was rerun. An earlier version of this README reported a 274-day trip and a complete breeding year, both of which were artefacts of the swap.

---

```

**Old:**

```
GPS data cleaned and enriched with step length, speed, bearing, and turning angle at each fix. Tracks segmented into foraging trips using a 50 km colony threshold. Key finding: most birds made a single extended post-breeding foraging trip (mean 25 days, max 274 days), consistent with grey-headed albatross non-breeding year behaviour.
```

**New:**

```
GPS data enriched with step length, speed, bearing, and turning angle at each fix. Bird 90494's timestamps are repaired first (Phase 0). Tracks segmented into away trips using a 50 km threshold around the colony reference point. Away trips lasted 7.6 to 21.8 days (mean 14.8 days).
```

**Old:**

```
**Scripts:** `python/phase1_movement_metrics.py`  
```

**New:**

```
**Scripts:** `python/phase0_repair_dates.py`, `python/colony.py`, `python/phase1_movement_metrics.py`  
```

**Old:**

```
**Outputs:** `data/processed/tracks_with_metrics.csv`, `data/processed/trip_statistics.csv`
```

**New:**

```
**Outputs:** `data/raw/albatross_tracks_corrected.csv`, `data/processed/tracks_with_metrics.csv`, `data/processed/trip_statistics.csv`
```

**Old:**

```
Gaussian Hidden Markov Model (3 states) fitted to log-transformed step length and absolute turning angle across all 24 birds simultaneously using `hmmlearn`. States labelled by mean step length: resting (0.14 km, 6.9°), foraging (1.44 km, 62.2°), transiting (4.04 km, 9.9°). Per-bird profiles extracted including foraging centre of mass, time budget, and movement statistics — these feed directly into Phase 5 artwork generation.
```

**New:**

```
Gaussian Hidden Markov Model (3 states) fitted to log-transformed step length and absolute turning angle across all 24 birds simultaneously using `hmmlearn`. States labelled by mean step length: resting (0.14 km, 6.9°), foraging (1.38 km, 62.2°), transiting (4.04 km, 9.9°). Per-bird profiles extracted including foraging centre of mass, time budget, and movement statistics — these feed directly into Phase 5 artwork generation.
```

**Old:**

```
Monthly SST and chlorophyll-a downloaded from NOAA CoastWatch ERDDAP via direct HTTP and matched to each GPS fix using nearest-neighbour temporal and spatial lookup. Random Forest classifier (200 trees, max depth 10) trained on environmental and spatial features to predict foraging behaviour. Feature importance analysis reveals spatial features dominate environmental ones.
```

**New:**

```
Monthly SST and chlorophyll-a downloaded from NOAA CoastWatch ERDDAP via direct HTTP and matched to each GPS fix using nearest-neighbour temporal and spatial lookup. Random Forest classifier (200 trees, max depth 10) trained on environmental and spatial features to predict foraging behaviour.
```

**Old:**

```
Foraging hotspots mapped using 2D kernel density estimation on foraging-state GPS points (0–360° longitude normalisation to handle dateline crossing). Foraging points classified by management jurisdiction. CCAMLR longline fishing effort (2013) analysed temporally and overlaid using approximate area centroids. Individual birds clustered into risk groups using k-means on four foraging strategy metrics.
```

**New:**

```
Foraging hotspots mapped using 2D kernel density estimation on foraging-state GPS points (0–360° longitude normalisation to handle dateline crossing). Fixes classified by point-in-polygon against World EEZ v12 and by the 60°S line. CCAMLR longline fishing effort (2013) analysed temporally. Individual birds clustered into risk groups using k-means on four foraging strategy metrics.
```

**Old:**

```
**Scripts:** `python/phase3_conservation_risk.py`  
```

**New:**

```
**Scripts:** `python/phase3_conservation_risk.py`, `python/eez_classification.py`  
```

**Old:**

```
**Outputs:** `data/processed/bird_risk_profiles.csv`, `data/processed/foraging_kde_grid.csv`
```

**New:**

```
**Outputs:** `data/processed/bird_risk_profiles.csv`, `data/processed/foraging_kde_grid.csv`, `data/processed/eez_zone_summary.csv`
```

**Old:**

```
Folium web map with Campbell Island-centred coordinate normalisation to maintain continuous flight path rendering across the dateline. Layers: individual bird tracks (risk-coloured, togglable), foraging heatmap, CCAMLR fishing effort circles (scaled by hook count), approximate CCAMLR Convention Area boundary. Per-bird popup statistics drawn from Phase 3 risk profiles.
```

**New:**

```
Folium web map with Campbell Island-centred coordinate normalisation to maintain continuous flight path rendering across the dateline. Layers: individual bird tracks (risk-coloured, togglable), foraging centres with per-bird popup statistics from Phase 3 risk profiles, foraging heatmap, EEZ outlines (World EEZ v12), approximate CCAMLR Convention Area boundary. CCAMLR fishing effort circles are not drawn.
```

**Old:**

```
(new section before "## Reproducing This Analysis")
```

**New:**

```
## Method Notes
- The colony reference point is the deployment site from the Movebank reference data.
- Jurisdiction was tested by point-in-polygon against World EEZ v12.
- The CCAMLR boundary is the 60°S line in this sector.
- Behaviour states come from this project's own Hidden Markov Model, not from the RST method in Torres et al. 2017.
- No fishing data was used in the jurisdiction test.

---

```

**Old:**

```
pip install pandas numpy matplotlib scipy scikit-learn hmmlearn xarray netCDF4 folium rasterio
```

**New:**

```
pip install pandas numpy matplotlib scipy scikit-learn hmmlearn xarray netCDF4 folium rasterio geopandas
```

**Old:**

```
Download `Grey-headed albatross, New Zealand (data from Torres et al. 2017).csv` from the [Movebank Data Repository](https://datarepository.movebank.org/handle/10255/move.637) and save to `data/raw/albatross_tracks.csv`.
```

**New:**

```
Download `Grey-headed albatross, New Zealand (data from Torres et al. 2017).csv` from the [Movebank Data Repository](https://datarepository.movebank.org/handle/10255/move.637) and save to `data/raw/albatross_tracks.csv`. Save the study's reference data to `data/raw/movebank_reference_data.csv`.

World EEZ v12 GeoPackages from [marineregions.org](https://www.marineregions.org/), extracted to `data/external/eez/World_EEZ_v12_20231025_gpkg/`.
```

**Old:**

```
python3 python/phase1_movement_metrics.py
```

**New:**

```
python3 python/phase0_repair_dates.py
python3 python/phase1_movement_metrics.py
```

**Old:**

```
│   │   ├── albatross_tracks.csv          # GPS tracking data (Torres et al. 2017)
```

**New:**

```
│   │   ├── albatross_tracks.csv          # GPS tracking data (Thompson et al. 2017)
│   │   ├── movebank_reference_data.csv   # Deployment reference data
│   │   ├── albatross_tracks_corrected.csv # Written by Phase 0
```

**Old:**

```
│   └── environmental/                    # SST, chlorophyll, bathymetry rasters
```

**New:**

```
│   ├── environmental/                    # SST, chlorophyll, bathymetry rasters
│   └── external/eez/                     # World EEZ v12
```

**Old:**

```
├── python/                               # Analysis scripts (Phases 1–4)
```

**New:**

```
├── python/                               # Analysis scripts (Phases 0–4)
```

**Old:**

```
**Environmental resolution:** SST and chlorophyll matched at monthly/~0.1° resolution. Fine-scale oceanographic features (fronts, eddies) that may drive local foraging decisions are not captured. Chlorophyll coverage is 94.8% due to cloud masking in ocean colour imagery.
```

**New:**

```
**Environmental resolution:** SST and chlorophyll matched at monthly/~0.1° resolution. Fine-scale oceanographic features (fronts, eddies) that may drive local foraging decisions are not captured. Chlorophyll coverage is incomplete due to cloud masking in ocean colour imagery.
```

**Old:**

```
**CCAMLR spatial matching:** Fishing effort mapped to approximate CCAMLR statistical area centroids (Area.csv contains no coordinate data). Precise spatial overlap with fishing grounds requires CCAMLR GIS boundary files not included in the public Statistical Bulletin.
```

**New:**

```
**CCAMLR effort:** Area.csv contains no coordinate data, so fishing effort is not spatially matched to the tracks and effort circles are not drawn on the map.
```

**Old:**

```
**NZ EEZ fishing data gap:** 97.5% of foraging occurs in New Zealand's EEZ and adjacent subantarctic waters outside CCAMLR's jurisdiction. A complete bycatch risk assessment requires New Zealand Ministry for Primary Industries fisheries data (FAO Area 81 / SPRFMO Convention Area), which was not available for this analysis.
```

**New:**

```
**Fishing data:** No fishing effort data for New Zealand's EEZ or the high seas (FAO Area 81 / SPRFMO Convention Area) was available for this analysis.
```

**Old:**

```
**Single breeding year:** Data covers 2013 only. Individual foraging strategies are assumed consistent across years based on published literature on seabird niche conservatism, but multi-year data would be needed to confirm.
```

**New:**

```
**Single tracking period:** Data covers 14 October to 12 December 2013 only.

**Random Forest:** Accuracy is 65.19% on a random split and 56.36% when whole birds are held out. The largest-class share is 58.96%.
```

**Old:**

```
(new section before "## Citation")
```

**New:**

```
## Data Citations
Thompson, D.R., Torres, L.G., Sagar, P.M., Kroeger, C.E. and Orben, R.A. (2017). Grey-headed albatross, New Zealand (data from Torres et al. 2017). Movebank Data Repository. doi:10.5441/001/1.694p666h/1.

Torres, L.G., Orben, R.A., Tolkova, I. and Thompson, D.R. (2017). Classification of Animal Movement Behavior through Residence in Space and Time. PLOS ONE 12(1): e0168513. doi:10.1371/journal.pone.0168513.

Flanders Marine Institute (2023). Maritime Boundaries Geodatabase: Maritime Boundaries and Exclusive Economic Zones (200NM), version 12. Available online at https://www.marineregions.org/. https://doi.org/10.14284/632 (licence CC BY 4.0).

---

```

**Old:**

```
- Movebank tracking data: Torres et al. (2017) - see original study for terms
```

**New:**

```
- Movebank tracking data: Thompson et al. (2017) - see original study for terms
- World EEZ v12: CC BY 4.0
```

## Unresolved

1. **CCAMLR effort circles:** areas 5851 and 5852 are positioned at guessed coordinates near 165E; 58.5.1 and 58.5.2 are Kerguelen and Heard Island in the Indian Ocean. Not drawn until positions are sourced.
2. **Root map file:** `albatross_interactive_map.html` is written by no script and still shows the old data (stale).
3. **Published pages:** the portfolio pages and art pages live elsewhere, were not touched, and still carry the old figures and wording.
4. **Artwork inputs:** the artwork scripts read `data/processed/` from this repository (seen in the earlier audit, not rechecked), so those inputs have now changed. That repository was not touched.
5. **`linkedin_tracks_map.png`:** still splits the tracks at the dateline into two blocks, as before.
6. **Map legend colours:** do not match the track colours, as before. The legend now shows computed counts.
7. **Phase 3 figure:** the KDE colour bar shows repeated 0.000 labels, as before.
8. **README licence text:** the `LICENSE` link points to a file that does not exist, left as instructed. The data licence list still names NOAA OISST and NASA Ocean Color, while the data table names MUR SST and ESA CCI; left unchanged.
9. **Chlorophyll coverage:** computed coverage is now 95.8%, where the README said 94.8%. The figure is in neither source report, so the README no longer gives a number.
10. **README text not in the list:** the README never contained "complete breeding year", "full year", "3.5x", "high-risk overlap areas" or "compliance targeting" as such; those claims are on the portfolio pages. "Inter-breeding" was also not present.
11. **`rerun_v2/make_copies.py`:** it expects the old constants in `python/`, so it no longer runs against these scripts. The committed copies and earlier commits keep the record.
12. **Boundary line 1289:** does not lie on either polygon it names (see `outputs_v3/eez/eez_report.md`). It is not used by the map's outlines except through the ring filter, and is not near any fix.
13. **Licence file request:** it asks users not to make its products available for download elsewhere. The map embeds simplified outlines with the credit; the source files are not committed.
14. **Later fixes in the second commit:** `centres_group.add_to(m)` and the filter that keeps baselines out of the EEZ ring test are in the foraging-centre commit, not the first script commit.

## Later changes

These supersede the matching text above.

1. **Foraging-centre markers hidden again.** The line `centres_group.add_to(m)` was removed, so the map again shows no foraging-centre markers or popups, as before this work. The circular-mean values stay in `bird_profiles.csv` and `bird_risk_profiles.csv`. The README map-layers sentence no longer lists foraging centres. The map was regenerated, and the copies in `outputs/maps/` and `outputs_v3/portfolio_assets/`, plus `MANIFEST.md`, were refreshed.
2. **README data correction wording.** "The same swap appears in that bird's deployment date in the Movebank reference data." was replaced with "The deployment date recorded for that bird in the Movebank reference data (2013-01-11) is also inconsistent with its tracking period."
