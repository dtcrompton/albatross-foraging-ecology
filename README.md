# Grey-headed Albatross Foraging Ecology

GPS tracking analysis of grey-headed albatross (*Thalassarche chrysostoma*) from Campbell Island, New Zealand.

**Data source:** Torres et al. (2017), Movebank Data Repository  
**DOI:** 10.5441/001/1.694p666h

## Project Structure
```
albatross-foraging-ecology/
├── data/
│   ├── raw/                    # Original Movebank CSV
│   ├── processed/              # Cleaned tracking data
│   └── environmental/          # SST, chlorophyll, bathymetry
├── python/                     # Analysis scripts
├── notebooks/                  # Jupyter notebooks
├── outputs/
│   ├── figures/               # Charts and graphs
│   ├── maps/                  # Interactive Folium maps
│   └── artwork/               # Generative art outputs
└── README.md
```
## Data Acquisition

Download Grey-headed albatross tracking data from:  
https://www.datarepository.movebank.org/handle/10255/move.637

Save as: `data/raw/albatross_tracks.csv`

## Installation

```bash
pip install pandas numpy matplotlib seaborn geopandas folium scipy scikit-learn pillow --break-system-packages
```

## Usage

**Phase 1: Data Exploration**
```bash
python3 python/explore_data.py
```
## Data Sources

**Albatross tracking data:**  
Thompson DR, Torres LG, Sagar PM, Kroeger CE, Orben RA (2017) Data from: Classification of animal movement behavior through residence in space and time. Movebank Data Repository. https://doi.org/10.5441/001/1.694p666h

**Environmental data:**  
- Sea Surface Temperature: NOAA OISST
- Bathymetry: GEBCO 2023
- Chlorophyll-a: NASA Ocean Color

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