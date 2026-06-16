# Grey-headed Albatross Foraging Ecology

**A four-phase GIS and conservation data science project analysing GPS tracking data from 24 grey-headed albatrosses (*Thalassarche chrysostoma*) breeding at Campbell Island, New Zealand.**

Using movement ecology methods, satellite-derived oceanographic data, and Southern Ocean fisheries records, this project identifies where and when these birds forage, what drives their habitat selection, and which individuals face the highest risk of overlap with longline fishing operations.

---

## Key Findings

- **Individual foraging strategies vary dramatically** — maximum foraging range spans from 745 km to 2,715 km across 24 birds from the same colony. Some birds spend 59% of their tracked time actively foraging; others just 33%.

- **Behaviour is classifiable from movement alone** — a Hidden Markov Model fitted to step length and turning angle cleanly separates three states: resting (26.9%), foraging area-restricted search (41.1%), and transiting (32.0%). The foraging signal is particularly strong: mean turning angle of 62.2° vs 9.9° for transit.

- **Spatial fidelity outweighs environmental tracking** — a Random Forest model predicts foraging behaviour from five variables. Distance from colony (0.31) and latitude/longitude (0.43 combined) are more predictive than SST (0.15) and chlorophyll-a (0.11), suggesting birds use learned spatial knowledge of productive zones rather than real-time environmental tracking.

- **99.1% of foraging occurs outside CCAMLR waters** — the birds forage almost entirely in New Zealand's Exclusive Economic Zone and adjacent subantarctic waters (north of 60°S). Bycatch risk from longline fisheries is primarily a matter for New Zealand's Ministry for Primary Industries and SPRFMO, not CCAMLR.

- **Temporal synchrony with CCAMLR longline effort is moderate (0.31)** — peak bird foraging activity (October–November) does not strongly coincide with peak CCAMLR longline effort (January), though December presents a risk window where both are active.

- **Three birds carry disproportionate risk** — birds 2, 89518, and 90493 form a distinct high-risk cluster, ranging 2,300–2,715 km from Campbell Island, covering 10,500–12,285 km total. Individual specialisation in foraging strategy appears persistent, suggesting these individuals are chronically rather than incidentally exposed.

---

## Data Sources

| Dataset | Source | Notes |
|---|---|---|
| GPS tracking data | Torres et al. (2017), Movebank Data Repository. DOI: [10.5441/001/1.694p666h](https://doi.org/10.5441/001/1.694p666h) | 93,474 GPS fixes, 24 birds, 2013 |
| Sea surface temperature | NASA JPL MUR SST monthly (jplMURSST41mday), NOAA CoastWatch ERDDAP | 0.01°, monthly composites |
| Chlorophyll-a | ESA CCI Ocean Colour monthly (pmlEsaCCI60OceanColorMonthly), NOAA CoastWatch ERDDAP | Monthly composites |
| Bathymetry | GEBCO 2026 Grid, [gebco.net](https://www.gebco.net) | GeoTiff tile, 100°E–180°E, 65°S–40°S |
| Fishing effort | CCAMLR Statistical Bulletin Vol. 37, [ccamlr.org](https://www.ccamlr.org) | Longline (LLS) gear, 2013 |

---

## Methodology

### Phase 1 — Movement Metrics and Trip Segmentation
GPS data cleaned and enriched with step length, speed, bearing, and turning angle at each fix. Tracks segmented into foraging trips using a 50 km colony threshold. Key finding: most birds made a single extended post-breeding foraging trip (mean 25 days, max 274 days), consistent with grey-headed albatross non-breeding year behaviour.

**Scripts:** `python/phase1_movement_metrics.py`  
**Outputs:** `data/processed/tracks_with_metrics.csv`, `data/processed/trip_statistics.csv`

### Phase 2a — Behavioural State Classification
Gaussian Hidden Markov Model (3 states) fitted to log-transformed step length and absolute turning angle across all 24 birds simultaneously using `hmmlearn`. States labelled by mean step length: resting (0.14 km, 6.9°), foraging (1.44 km, 62.2°), transiting (4.04 km, 9.9°). Per-bird profiles extracted including foraging centre of mass, time budget, and movement statistics — these feed directly into Phase 5 artwork generation.

**Scripts:** `python/phase2a_behaviour_classification.py`, `python/phase2a_figures.py`  
**Outputs:** `data/processed/tracks_with_behaviour.csv`, `data/processed/bird_profiles.csv`

### Phase 2b — Environmental Driver Analysis
Monthly SST and chlorophyll-a downloaded from NOAA CoastWatch ERDDAP via direct HTTP and matched to each GPS fix using nearest-neighbour temporal and spatial lookup. Random Forest classifier (200 trees, max depth 10) trained on environmental and spatial features to predict foraging behaviour. Feature importance analysis reveals spatial features dominate environmental ones.

**Scripts:** `python/phase2b_environmental_drivers.py`  
**Outputs:** `data/processed/tracks_with_env.csv`, `data/environmental/sst_2013.nc`, `data/environmental/chla_2013.nc`

### Phase 3 — Conservation Risk Analysis
Foraging hotspots mapped using 2D kernel density estimation on foraging-state GPS points (0–360° longitude normalisation to handle dateline crossing). Foraging points classified by management jurisdiction. CCAMLR longline fishing effort (2013) analysed temporally and overlaid using approximate area centroids. Individual birds clustered into risk groups using k-means on four foraging strategy metrics.

**Scripts:** `python/phase3_conservation_risk.py`  
**Outputs:** `data/processed/bird_risk_profiles.csv`, `data/processed/foraging_kde_grid.csv`

### Phase 4 — Interactive Map
Folium web map with Campbell Island-centred coordinate normalisation to maintain continuous flight path rendering across the dateline. Layers: individual bird tracks (risk-coloured, togglable), foraging heatmap, CCAMLR fishing effort circles (scaled by hook count), approximate CCAMLR Convention Area boundary. Per-bird popup statistics drawn from Phase 3 risk profiles.

**Scripts:** `python/phase4_interactive_map.py`  
**Outputs:** `outputs/maps/albatross_interactive_map.html`

---

## Reproducing This Analysis

### Prerequisites
```bash
Python 3.11+
pip install pandas numpy matplotlib scipy scikit-learn hmmlearn xarray netCDF4 folium rasterio
```

### Data
Download `Grey-headed albatross, New Zealand (data from Torres et al. 2017).csv` from the [Movebank Data Repository](https://datarepository.movebank.org/handle/10255/move.637) and save to `data/raw/albatross_tracks.csv`.

CCAMLR Statistical Bulletin Vol. 37 zip from [ccamlr.org](https://www.ccamlr.org/en/document/data/ccamlr-statistical-bulletin-vol-37), extracted to `data/raw/ccamlr/`.

GEBCO bathymetry tile (100°E–180°E, 65°S–40°S) from [gebco.net](https://www.gebco.net/data-products/gridded-bathymetry-data/), saved to `data/environmental/bathymetry/`.

SST and chlorophyll downloaded automatically by `phase2b_environmental_drivers.py` via curl commands documented in the script header.

### Run
```bash
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
│   │   ├── albatross_tracks.csv          # GPS tracking data (Torres et al. 2017)
│   │   └── ccamlr/                       # CCAMLR Statistical Bulletin Vol. 37
│   ├── processed/                        # Enriched CSVs from each phase
│   └── environmental/                    # SST, chlorophyll, bathymetry rasters
├── python/                               # Analysis scripts (Phases 1–4)
├── outputs/
│   ├── figures/                          # PNG figures from each phase
│   └── maps/                             # Interactive Folium map
└── README.md
```
---

## Limitations

**Environmental resolution:** SST and chlorophyll matched at monthly/~0.1° resolution. Fine-scale oceanographic features (fronts, eddies) that may drive local foraging decisions are not captured. Chlorophyll coverage is 94.8% due to cloud masking in ocean colour imagery.

**CCAMLR spatial matching:** Fishing effort mapped to approximate CCAMLR statistical area centroids (Area.csv contains no coordinate data). Precise spatial overlap with fishing grounds requires CCAMLR GIS boundary files not included in the public Statistical Bulletin.

**NZ EEZ fishing data gap:** 97.5% of foraging occurs in New Zealand's EEZ and adjacent subantarctic waters outside CCAMLR's jurisdiction. A complete bycatch risk assessment requires New Zealand Ministry for Primary Industries fisheries data (FAO Area 81 / SPRFMO Convention Area), which was not available for this analysis.

**Single breeding year:** Data covers 2013 only. Individual foraging strategies are assumed consistent across years based on published literature on seabird niche conservatism, but multi-year data would be needed to confirm.

**CCAMLR Convention Area boundary:** Approximated at 60°S across the Pacific sector. The actual boundary follows the Antarctic Convergence in some areas and fixed latitude lines in others.

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
- Movebank tracking data: Torres et al. (2017) - see original study for terms
- NOAA OISST: Public domain
- GEBCO bathymetry: Open access under GEBCO license
- NASA Ocean Color: Open access

---

## Contact

**Daniel Crompton**  
Portfolio: [dtcrompton.github.io](https://dtcrompton.github.io)  
LinkedIn: [linkedin.com/in/dtcrompton](https://linkedin.com/in/dtcrompton/)  
GitHub: [@dtcrompton](https://github.com/dtcrompton)