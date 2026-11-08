# Grey-headed Albatross Foraging Ecology

**A four-phase GIS and conservation data science project analysing GPS tracking data from 24 grey-headed albatrosses (*Thalassarche chrysostoma*) at Campbell Island, New Zealand. The 24 birds are adults recorded as incubating in the Movebank reference data, tracked with igotU GT-600 loggers (one fix every 5 minutes) between 14 October and 12 December 2013, with away trips of 7.6 to 21.8 days (mean 14.8 days).**

Using movement ecology methods and satellite-derived oceanographic data, this project classifies behaviour from movement, relates it to environmental variables, and reports where foraging fixes fall relative to exclusive economic zone boundaries and the 60°S line.

---

## Key Findings

- **Maximum distance from the colony** ranges from 746 km to 2,713 km across the 24 birds (3.6x). The foraging share of fixes ranges from 33% to 59%, and total distance from 3,465 km to 12,285 km.

- **Behaviour was classified from movement** using a Hidden Markov Model fitted to step length and turning angle, with three states: resting (26.9% of fixes), foraging area-restricted search (41.1%), and transiting (32.1%). Mean turning angle is 62.2° in the foraging state and 9.9° in the transiting state.

- Of 38,379 foraging fixes from 24 incubating adults tracked in 2013, 97.3% fell outside every country's exclusive economic zone and 2.7% fell inside New Zealand's. 99.1% fell north of 60°S, outside the CCAMLR Convention Area.

- **Temporal synchrony index: 0.295.** It is computed against all CCAMLR longline effort worldwide with no area filter and is not a measure of overlap.

- **K-means clustering** of four foraging-strategy metrics gives cluster sizes of 13 low, 8 medium and 3 high risk. The high-risk cluster is birds 2, 89518 and 90493, with maximum distances of 2,319 to 2,713 km and total distances of 9,713 to 12,285 km. The clustering uses no fishing data.

---

## Data Correction (8 November 2026)
Bird 90494's timestamps in the source file, as downloaded from the Movebank Data Repository, had day and month swapped on 3,056 fixes (3.3% of the data). The same swap appears in that bird's deployment date in the Movebank reference data. The swap was repaired using event-id order, the source file is unchanged, the repair script (`python/phase0_repair_dates.py`) and rule are in this repository, and the pipeline was rerun. An earlier version of this README reported a 274-day trip and a complete breeding year, both of which were artefacts of the swap.

---

## Data Sources

| Dataset | Source | Notes |
|---|---|---|
| GPS tracking data | Thompson et al. (2017), Movebank Data Repository (see Data citations) | 93,474 GPS fixes, 24 birds, 14 October to 12 December 2013 |
| Sea surface temperature | NASA JPL MUR SST monthly (jplMURSST41mday), NOAA CoastWatch ERDDAP | 0.01°, monthly composites |
| Chlorophyll-a | ESA CCI Ocean Colour monthly (pmlEsaCCI60OceanColorMonthly), NOAA CoastWatch ERDDAP | Monthly composites |
| Bathymetry | GEBCO 2026 Grid, [gebco.net](https://www.gebco.net) | GeoTiff tile, 100°E–180°E, 65°S–40°S |
| Fishing effort | CCAMLR Statistical Bulletin Vol. 37, [ccamlr.org](https://www.ccamlr.org) | Longline (LLS) gear, 2013 |
| EEZ boundaries | World EEZ v12, Flanders Marine Institute (see Data citations) | Point-in-polygon test and map outlines |

---

## Methodology

### Phase 1 — Movement Metrics and Trip Segmentation
GPS data enriched with step length, speed, bearing, and turning angle at each fix. Bird 90494's timestamps are repaired first (Phase 0). Tracks segmented into away trips using a 50 km threshold around the colony reference point. Away trips lasted 7.6 to 21.8 days (mean 14.8 days).

**Scripts:** `python/phase0_repair_dates.py`, `python/colony.py`, `python/phase1_movement_metrics.py`  
**Outputs:** `data/raw/albatross_tracks_corrected.csv`, `data/processed/tracks_with_metrics.csv`, `data/processed/trip_statistics.csv`

### Phase 2a — Behavioural State Classification
Gaussian Hidden Markov Model (3 states) fitted to log-transformed step length and absolute turning angle across all 24 birds simultaneously using `hmmlearn`. States labelled by mean step length: resting (0.14 km, 6.9°), foraging (1.38 km, 62.2°), transiting (4.04 km, 9.9°). Per-bird profiles extracted including foraging centre of mass, time budget, and movement statistics — these feed directly into Phase 5 artwork generation.

**Scripts:** `python/phase2a_behaviour_classification.py`, `python/phase2a_figures.py`  
**Outputs:** `data/processed/tracks_with_behaviour.csv`, `data/processed/bird_profiles.csv`

### Phase 2b — Environmental Driver Analysis
Monthly SST and chlorophyll-a downloaded from NOAA CoastWatch ERDDAP via direct HTTP and matched to each GPS fix using nearest-neighbour temporal and spatial lookup. Random Forest classifier (200 trees, max depth 10) trained on environmental and spatial features to predict foraging behaviour.

**Scripts:** `python/phase2b_environmental_drivers.py`  
**Outputs:** `data/processed/tracks_with_env.csv`, `data/environmental/sst_2013.nc`, `data/environmental/chla_2013.nc`

### Phase 3 — Conservation Risk Analysis
Foraging hotspots mapped using 2D kernel density estimation on foraging-state GPS points (0–360° longitude normalisation to handle dateline crossing). Fixes classified by point-in-polygon against World EEZ v12 and by the 60°S line. CCAMLR longline fishing effort (2013) analysed temporally. Individual birds clustered into risk groups using k-means on four foraging strategy metrics.

**Scripts:** `python/phase3_conservation_risk.py`, `python/eez_classification.py`  
**Outputs:** `data/processed/bird_risk_profiles.csv`, `data/processed/foraging_kde_grid.csv`, `data/processed/eez_zone_summary.csv`

### Phase 4 — Interactive Map
Folium web map with Campbell Island-centred coordinate normalisation to maintain continuous flight path rendering across the dateline. Layers: individual bird tracks (risk-coloured, togglable), foraging heatmap, EEZ outlines (World EEZ v12), approximate CCAMLR Convention Area boundary. CCAMLR fishing effort circles are not drawn.

**Scripts:** `python/phase4_interactive_map.py`  
**Outputs:** `outputs/maps/albatross_interactive_map.html`

---

## Method Notes
- The colony reference point is the deployment site from the Movebank reference data.
- Jurisdiction was tested by point-in-polygon against World EEZ v12.
- The CCAMLR boundary is the 60°S line in this sector.
- Behaviour states come from this project's own Hidden Markov Model, not from the RST method in Torres et al. 2017.
- No fishing data was used in the jurisdiction test.

---

## Reproducing This Analysis

### Prerequisites
```bash
Python 3.11+
pip install pandas numpy matplotlib scipy scikit-learn hmmlearn xarray netCDF4 folium rasterio geopandas
```

### Data
Download `Grey-headed albatross, New Zealand (data from Torres et al. 2017).csv` from the [Movebank Data Repository](https://datarepository.movebank.org/handle/10255/move.637) and save to `data/raw/albatross_tracks.csv`. Save the study's reference data to `data/raw/movebank_reference_data.csv`.

World EEZ v12 GeoPackages from [marineregions.org](https://www.marineregions.org/), extracted to `data/external/eez/World_EEZ_v12_20231025_gpkg/`.

CCAMLR Statistical Bulletin Vol. 37 zip from [ccamlr.org](https://www.ccamlr.org/en/document/data/ccamlr-statistical-bulletin-vol-37), extracted to `data/raw/ccamlr/`.

GEBCO bathymetry tile (100°E–180°E, 65°S–40°S) from [gebco.net](https://www.gebco.net/data-products/gridded-bathymetry-data/), saved to `data/environmental/bathymetry/`.

SST and chlorophyll downloaded automatically by `phase2b_environmental_drivers.py` via curl commands documented in the script header.

### Run
```bash
python3 python/phase0_repair_dates.py
python3 python/phase1_movement_metrics.py
python3 python/phase2a_behaviour_classification.py
python3 python/phase2a_figures.py
python3 python/phase2b_environmental_drivers.py
python3 python/phase3_conservation_risk.py
python3 python/phase4_interactive_map.py
open outputs/maps/albatross_interactive_map.html
```

---

## Project Structure
```
albatross-foraging-ecology/

├── data/
│   ├── raw/
│   │   ├── albatross_tracks.csv          # GPS tracking data (Thompson et al. 2017)
│   │   ├── movebank_reference_data.csv   # Deployment reference data
│   │   ├── albatross_tracks_corrected.csv # Written by Phase 0
│   │   └── ccamlr/                       # CCAMLR Statistical Bulletin Vol. 37
│   ├── processed/                        # Enriched CSVs from each phase
│   ├── environmental/                    # SST, chlorophyll, bathymetry rasters
│   └── external/eez/                     # World EEZ v12
├── python/                               # Analysis scripts (Phases 0–4)
├── outputs/
│   ├── figures/                          # PNG figures from each phase
│   └── maps/                             # Interactive Folium map
└── README.md
```
---

## Limitations

**Environmental resolution:** SST and chlorophyll matched at monthly/~0.1° resolution. Fine-scale oceanographic features (fronts, eddies) that may drive local foraging decisions are not captured. Chlorophyll coverage is incomplete due to cloud masking in ocean colour imagery.

**CCAMLR effort:** Area.csv contains no coordinate data, so fishing effort is not spatially matched to the tracks and effort circles are not drawn on the map.

**Fishing data:** No fishing effort data for New Zealand's EEZ or the high seas (FAO Area 81 / SPRFMO Convention Area) was available for this analysis.

**Single tracking period:** Data covers 14 October to 12 December 2013 only.

**Random Forest:** Accuracy is 65.19% on a random split and 56.36% when whole birds are held out. The largest-class share is 58.96%.

**CCAMLR Convention Area boundary:** Approximated at 60°S across the Pacific sector. The actual boundary follows the Antarctic Convergence in some areas and fixed latitude lines in others.

---

## Data Citations
Thompson, D.R., Torres, L.G., Sagar, P.M., Kroeger, C.E. and Orben, R.A. (2017). Grey-headed albatross, New Zealand (data from Torres et al. 2017). Movebank Data Repository. doi:10.5441/001/1.694p666h/1.

Torres, L.G., Orben, R.A., Tolkova, I. and Thompson, D.R. (2017). Classification of Animal Movement Behavior through Residence in Space and Time. PLOS ONE 12(1): e0168513. doi:10.1371/journal.pone.0168513.

Flanders Marine Institute (2023). Maritime Boundaries Geodatabase: Maritime Boundaries and Exclusive Economic Zones (200NM), version 12. Available online at https://www.marineregions.org/. https://doi.org/10.14284/632 (licence CC BY 4.0).

---

## Citation

If using this work, please cite:
```
Crompton, D. (2026). Grey-headed Albatross Foraging Ecology: GPS tracking
analysis and oceanographic correlates. GitHub repository.
https://github.com/dtcrompton/albatross-foraging-ecology

```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

Data sources retain their original licenses:
- Movebank tracking data: Thompson et al. (2017) - see original study for terms
- World EEZ v12: CC BY 4.0
- NOAA OISST: Public domain
- GEBCO bathymetry: Open access under GEBCO license
- NASA Ocean Color: Open access

---

## Contact

**Daniel Crompton**  
Portfolio: [dtcrompton.github.io](https://dtcrompton.github.io)  
LinkedIn: [linkedin.com/in/dtcrompton](https://linkedin.com/in/dtcrompton/)  
GitHub: [@dtcrompton](https://github.com/dtcrompton)