# World EEZ v12 test of the v3 tracks

Numbers and evidence only. Published wording was not changed.

## Sources

**Boundary data:** Flanders Marine Institute (2023). Maritime Boundaries Geodatabase: Maritime Boundaries and Exclusive Economic Zones (200NM), version 12. Available online at https://www.marineregions.org/. https://doi.org/10.14284/632. Licence: CC BY 4.0.

**Track data:** Thompson, D.R., Torres, L.G., Sagar, P.M., Kroeger, C.E. and Orben, R.A. (2017). Grey-headed albatross, New Zealand (data from Torres et al. 2017). Movebank Data Repository. doi:10.5441/001/1.694p666h/1.

**Tracks used:** `data/processed_v3/tracks_with_behaviour.csv` (bird 90494 dates repaired, colony point 169.224E, 52.474S).

### Which file was used for which step

| File | Used for |
|---|---|
| `eez_v12.gpkg` | Point-in-polygon classification (Part 3), known-point tests (Part 2), map outlines (Part 6) |
| `eez_boundaries_v12.gpkg` | Distance to nearest boundary (Part 4). It holds the legal limits as lines, without the coastline and without the artificial edge at 180 degrees that the polygon outlines contain. |
| `LICENSE_EEZ_v12.txt` | Licence wording below |

### Licence wording, quoted from `LICENSE_EEZ_v12.txt`

> LICENSE, TERMS OF USE & CITATION
> LICENSE
> Marine Regions’ data is licensed under CC-By (https://creativecommons.org/licenses/by/4.0/).
> Please contact us for other uses of the Licensed Material beyond license terms.
> We kindly request our users not to make our products available for download elsewhere and to always refer to marineregions.org for the most up-to-date products and services.
>
>
> TERMS OF USE
> Marine Regions is not meant to be used for legal, economical (in the sense of exploration of natural resources) or navigational purposes.
> It is developed solely for scientific, educational and research purposes.
>
> VLIZ can in no case be held accountable or liable for faults, of any nature, that might occur in the usage of Marine Regions.
> All those who wish to use Marine Regions do so completely at own risk/under own responsibility and according to the License conditions and the Terms of Use.
> VLIZ expresses no opinion about the legal state neither of any country, territory or area nor concerning its delimitation, frontier or borders.
> The data has no legal value whatsoever.
>
> Marine Regions can be used according to the terms and conditions mentioned in the CC-BY license (CC-BY, https://creativecommons.org/licenses/by/4.0/).
> The provisions above in no way replace the provisions of the CC-license.
> If any of the abovementioned provisions divert from or contradict the provisions of the CC-license in any way, the CC-license provisions prevail.
>
>
> FEEDBACK
> If Marine Regions' data is used for a publication or product, we kindly request to inform us (info@marineregions.org) and we'll add the publication to our users page (http://marineregions.org/stats_pubs.php).
>
> Feedback of the users of Marine Regions is more than welcome.
> In case you notice mistakes, incompleteness or are willing to join us in this endeavor, please feel free to open an issue or start a discussion on our public GitHub forum (https://github.com/lifewatch/marineregions-issues), or contact us on info@marineregions.org if it concerns sensitive information that should not be shared publicly.
>
>
> CITATION
> Flanders Marine Institute (2023). Maritime Boundaries Geodatabase: Maritime Boundaries and Exclusive Economic Zones (200NM), version 12. Available online at https://www.marineregions.org/. https://doi.org/10.14284/632

The boundary files are not committed to this repository (`data/external/` is listed in `.git/info/exclude`).

### Software

Python 3.13.10; geopandas 1.1.3, shapely 2.1.2 (GEOS 3.13.1), pyogrio 0.12.1, pyproj 3.7.2 (PROJ 9.5.1), scipy 1.17.1, numpy 2.4.3, pandas 3.0.1.

## Part 1: boundary file

| File | Size (bytes) | SHA-256 | Layer | CRS | Geometry | Features | Last change stored in file |
|---|---|---|---|---|---|---|---|
| eez_v12.gpkg | 164,458,496 | `90f14b06bac693f8d7469255f56542a2260ef032a3a52f4afc3113e38c363a46` | eez_v12 | EPSG:4326 | MultiPolygon | 285 | 2023-10-11T07:39:09.526Z |
| eez_boundaries_v12.gpkg | 15,794,176 | `ee073df6d1777c8aae69b41b90105536a4356871dd28eac7e9d552b4d56d8ca1` | eez_boundaries_v12 | EPSG:4326 | MultiLineString | 2349 | 2023-10-11T07:42:30.131Z |

Version evidence: the folder is named `World_EEZ_v12_20231025_gpkg`, the layer is `eez_v12`, and the licence file citation says version 12. The metadata stored inside the GeoPackage holds an empty QGIS template with no version, date, licence or citation text.

Polygon columns: MRGID, GEONAME, MRGID_TER1, POL_TYPE, MRGID_SOV1, TERRITORY1, ISO_TER1, SOVEREIGN1, MRGID_TER2, MRGID_SOV2, TERRITORY2, ISO_TER2, SOVEREIGN2, MRGID_TER3, MRGID_SOV3, TERRITORY3, ISO_TER3, SOVEREIGN3, X_1, Y_1, MRGID_EEZ, AREA_KM2, ISO_SOV1, ISO_SOV2, ISO_SOV3, UN_SOV1, UN_SOV2, UN_SOV3, UN_TER1, UN_TER2, UN_TER3.

Line columns: LINE_ID, LINE_NAME, LINE_TYPE, MRGID_SOV1, MRGID_TER1, TERRITORY1, SOVEREIGN1, MRGID_TER2, TERRITORY2, MRGID_SOV2, SOVEREIGN2, MRGID_EEZ1, EEZ1, MRGID_EEZ2, EEZ2, SOURCE1, URL1, SOURCE2, URL2, SOURCE3, URL3, ORIGIN, DOC_DATE, MRGID_JREG, JOINT_REG, LENGTH_KM, MRGID_EEZ3, EEZ3, TERRITORY3, MRGID_TER3, SOVEREIGN3, MRGID_SOV3.

### Features intersecting the track bounding box plus 10 degrees

Box: longitude 155.515 to 220.130 in 0-360 form (split at 180 for the test), latitude -70.626 to -31.563. Polygon type counts in the whole file: 200NM 229, Overlapping claim 35, Joint regime 21. None of the overlapping-claim or joint-regime features intersects the box.

| MRGID | GEONAME | Territory | Sovereign | POL_TYPE | AREA_KM2 |
|---|---|---|---|---|---|
| 8310 | Australian Exclusive Economic Zone (Norfolk Island) | Norfolk Island | Australia | 200NM | 430,600 |
| 8323 | Australian Exclusive Economic Zone | Australia | Australia | 200NM | 6,873,830 |
| 8311 | Australian Exclusive Economic Zone (Macquarie Island) | Macquarie Island | Australia | 200NM | 476,278 |
| 8455 | New Zealand Exclusive Economic Zone | New Zealand | New Zealand | 200NM | 4,104,551 |

- New Zealand EEZ: MRGID 8455.
- Australian EEZ around Macquarie Island: MRGID 8311.
- Others in the box: Australian EEZ (MRGID 8323) and Australian EEZ, Norfolk Island (MRGID 8310).

### Splitting at the 180 degree meridian

| GEONAME | Parts | Parts touching +180 | Parts touching -180 | Interior rings | Bounds (W, S, E, N) |
|---|---|---|---|---|---|
| Australian Exclusive Economic Zone (Norfolk Island) | 1 | 0 | 0 | 4 | 164.111, -32.478, 171.801, -25.845 |
| Australian Exclusive Economic Zone | 8 | 0 | 0 | 4304 | 109.233, -47.194, 163.192, -8.883 |
| Australian Exclusive Economic Zone (Macquarie Island) | 1 | 0 | 0 | 2 | 152.863, -58.449, 164.691, -51.027 |
| New Zealand Exclusive Economic Zone | 2 | 1 | 1 | 770 | -180.000, -55.949, 180.000, -25.888 |

The New Zealand EEZ is one MultiPolygon split at the meridian into two parts. East part vertices on +180: latitude -52.956989 to -26.421365. West part vertices on -180: latitude -52.956987 to -26.421359.

Handling: raw longitudes (-180 to 180) were tested against the unmodified polygons, which use the same range, so each side of the meridian is matched by its own part. No fix has a longitude of exactly +180 or -180. Across all birds, 120 consecutive fix pairs cross the meridian and 0 of those pairs change zone.

## Part 2: validation

| Point | Lat, lon | Expected | Result |
|---|---|---|---|
| Deployment site | -52.474, 169.224 | New Zealand EEZ (per the task) | None |
| 60S, 169E | -60, 169 | None: south of the NZ limit (55.949S) and the Macquarie limit (58.449S) | None |
| 52.5S, 175W | -52.5, -175 | None | None |
| 40S, 150W | -40, -150 | None: east of the NZ limit (171.201W) | None |
| 50S, 100E | -50, 100 | None: west of the Australian limit (109.233E) | None |
| Added control: 52.0S, 169.2E (sea north of Campbell) | -52.0, 169.2 | New Zealand EEZ | New Zealand Exclusive Economic Zone |
| Added control: 55S, 160E | -55, 160 | Australian EEZ (Macquarie Island) | Australian Exclusive Economic Zone (Macquarie Island) |
| Added control: 48S, 179.999E (seam) | -48, 179.999 | New Zealand EEZ | New Zealand Exclusive Economic Zone |
| Added control: 48S, 179.999W (seam) | -48, -179.999 | New Zealand EEZ | New Zealand Exclusive Economic Zone |
| Added control: 55S, 179.999E (seam) | -55, 179.999 | None | None |
| Added control: 55S, 179.999W (seam) | -55, -179.999 | None | None |

**Unexpected result:** the deployment site is not inside any polygon. It falls in an interior ring of the New Zealand EEZ feature with bounds 169.016, -52.609, 169.269, -52.465 (W, S, E, N), which is a land gap covering Campbell Island: the EEZ polygons exclude land. The other four requested points returned no feature, as expected from the file bounds. The added controls behaved as expected.

Because of this, a fix on land inside a polygon outline is reported as its own row, "Land gap inside New Zealand EEZ outline", rather than as outside. Fixes per feature in such a gap: Australian Exclusive Economic Zone (Norfolk Island): 0; Australian Exclusive Economic Zone: 0; Australian Exclusive Economic Zone (Macquarie Island): 0; New Zealand Exclusive Economic Zone: 1. The New Zealand fix: bird 23059, 2013-10-27 19:55:29, -52.479733, 169.146851, behaviour 2.

### Boundary lines against polygons, New Zealand EEZ

Lines tested: 5 features where New Zealand is named, excluding baselines. Both sets were densified to 0.5 km along geodesics.

| Check | Result |
|---|---|
| Outline points away from the 180 seam to nearest line point: median, maximum | 0.000 km, 0.227 km |
| Outline points away from the seam more than 1 km from a line | 0 of 26,047 |
| Outline points on the 180 seam (no line expected) | 11,789 |

Each boundary line against all rings (outer and interior) of the polygons named in its EEZ1 and EEZ2 fields. Treaty lines are tested against both parties because they extend beyond the New Zealand polygon.

| LINE_ID | LINE_NAME | LINE_TYPE | EEZ1 | EEZ2 | Points | Median km | Maximum km | Points over 1 km |
|---|---|---|---|---|---|---|---|---|
| 1289 | Norfolk Island (Australia) - New Zealand | Treaty | Australian Exclusive Economic Zone (Norfolk Island) | New Zealand Exclusive Economic Zone | 394 | 295.064 | 375.940 | 100.00% |
| 4020 | Norfolk Island (Australia) - New Zealand | Treaty | Australian Exclusive Economic Zone (Norfolk Island) | New Zealand Exclusive Economic Zone | 1,365 | 0.000 | 0.246 | 0.00% |
| 2062 | New Zealand 200 NM | 200 NM | New Zealand Exclusive Economic Zone |  | 24,306 | 0.000 | 0.465 | 0.00% |
| 4096 | New Zealand 200 NM | 200 NM | New Zealand Exclusive Economic Zone |  | 2,294 | 0.101 | 0.235 | 0.00% |
| 4615 | New Zealand - Macquarie Island (Australia) | Treaty | New Zealand Exclusive Economic Zone | Australian Exclusive Economic Zone (Macquarie Island) | 2,234 | 0.000 | 0.000 | 0.00% |

Line 1289 does not lie on either polygon it names. It runs near 33S, 162 to 163E. Fixes for which it is the nearest boundary line: 0. The boundary line closest to any fix within 20 km of a boundary: LINE_ID 2062 (1,033 fixes).

Interior rings of the New Zealand EEZ south of 38S with area over 0.003 square degrees. A ring is called a land gap or a non-land pocket according to whether a boundary line runs along it:

| Bounds (W, S, E, N) | Median distance to a boundary line | Fixes inside | Type |
|---|---|---|---|
| 166.425, -46.676, 174.318, -40.498 | 393.176 km | 0 | No boundary line (land gap) |
| 177.636, -44.555, 178.496, -44.071 | 0.101 km | 0 | Boundary line (non-land pocket) |
| 166.443, -45.756, 166.724, -45.598 | 376.204 km | 0 | No boundary line (land gap) |
| 166.867, -45.303, 167.004, -45.145 | 373.417 km | 0 | No boundary line (land gap) |
| 173.768, -40.943, 173.968, -40.692 | 468.710 km | 0 | No boundary line (land gap) |
| 174.160, -41.244, 174.393, -41.088 | 458.805 km | 0 | No boundary line (land gap) |
| 167.447, -47.291, 168.229, -46.683 | 404.987 km | 0 | No boundary line (land gap) |
| 171.805, -50.731, 174.104, -48.296 | 0.101 km | 0 | Boundary line (non-land pocket) |
| 165.868, -50.863, 166.290, -50.509 | 326.342 km | 0 | No boundary line (land gap) |
| 165.897, -50.930, 166.208, -50.836 | 308.123 km | 0 | No boundary line (land gap) |
| 169.016, -52.609, 169.269, -52.465 | 357.881 km | 1 | No boundary line (land gap) |
| -176.895, -44.133, -176.191, -43.692 | 388.524 km | 0 | No boundary line (land gap) |
| -176.277, -44.355, -176.153, -44.224 | 384.860 km | 0 | No boundary line (land gap) |

The one fix in the "Land gap" row lies in the ring containing the deployment site.

## Part 3: classification

Method: `sindex.query(points, predicate="intersects")` against the 4 features in the box, on raw longitudes. Fixes hitting more than one feature: 0. CCAMLR test: latitude below -60, using the 60S line as the boundary for this longitude sector as specified for this task; no CCAMLR boundary file was used.

### Zone shares by behaviour state

| Zone | Foraging | Transiting | Resting | All fixes |
|---|---|---|---|---|
| New Zealand EEZ | 1,043 (2.72%) | 4,515 (15.07%) | 1,280 (5.09%) | 6,838 (7.32%) |
| Australian EEZ | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) |
| Other named EEZ | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) |
| Overlapping claim or joint regime | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) |
| Outside all EEZs | 37,336 (97.28%) | 25,444 (84.93%) | 23,855 (94.91%) | 86,635 (92.68%) |
| Land gap inside New Zealand EEZ outline | 0 (0.00%) | 1 (0.00%) | 0 (0.00%) | 1 (0.00%) |
| Total | 38,379 | 29,960 | 25,135 | 93,474 |

### Foraging fixes: zone by south of 60S

| Zone | North of or on 60S | South of 60S | Total |
|---|---|---|---|
| New Zealand EEZ | 1,043 (2.72%) | 0 (0.00%) | 1,043 (2.72%) |
| Australian EEZ | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) |
| Other named EEZ | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) |
| Overlapping claim or joint regime | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) |
| Outside all EEZs | 36,974 (96.34%) | 362 (0.94%) | 37,336 (97.28%) |
| Land gap inside New Zealand EEZ outline | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) |
| Total | 38,017 (99.06%) | 362 (0.94%) | 38,379 |

### Foraging fixes per bird

| Bird | Foraging fixes | New Zealand EEZ | Australian EEZ | Other named EEZ | Overlapping claim or joint regime | Outside all EEZs | Land gap inside New Zealand EEZ outline |
|---|---|---|---|---|---|---|---|
| 1 | 1,906 | 1.4% | 0.0% | 0.0% | 0.0% | 98.6% | 0.0% |
| 2 | 1,518 | 1.6% | 0.0% | 0.0% | 0.0% | 98.4% | 0.0% |
| 23058 | 1,402 | 1.1% | 0.0% | 0.0% | 0.0% | 98.9% | 0.0% |
| 23059 | 1,549 | 1.8% | 0.0% | 0.0% | 0.0% | 98.2% | 0.0% |
| 23096 | 2,118 | 2.0% | 0.0% | 0.0% | 0.0% | 98.0% | 0.0% |
| 23782 | 1,344 | 6.2% | 0.0% | 0.0% | 0.0% | 93.8% | 0.0% |
| 29155 | 1,409 | 2.9% | 0.0% | 0.0% | 0.0% | 97.1% | 0.0% |
| 41269 | 1,609 | 7.6% | 0.0% | 0.0% | 0.0% | 92.4% | 0.0% |
| 49364 | 1,523 | 0.6% | 0.0% | 0.0% | 0.0% | 99.4% | 0.0% |
| 58565 | 2,414 | 2.7% | 0.0% | 0.0% | 0.0% | 97.3% | 0.0% |
| 61696 | 726 | 3.2% | 0.0% | 0.0% | 0.0% | 96.8% | 0.0% |
| 62093 | 1,493 | 3.3% | 0.0% | 0.0% | 0.0% | 96.7% | 0.0% |
| 82589 | 1,250 | 0.8% | 0.0% | 0.0% | 0.0% | 99.2% | 0.0% |
| 89518 | 2,005 | 1.5% | 0.0% | 0.0% | 0.0% | 98.5% | 0.0% |
| 89570 | 1,364 | 0.9% | 0.0% | 0.0% | 0.0% | 99.1% | 0.0% |
| 90282 | 1,621 | 2.6% | 0.0% | 0.0% | 0.0% | 97.4% | 0.0% |
| 90287 | 1,562 | 1.9% | 0.0% | 0.0% | 0.0% | 98.1% | 0.0% |
| 90407 | 1,004 | 0.3% | 0.0% | 0.0% | 0.0% | 99.7% | 0.0% |
| 90420 | 2,356 | 5.3% | 0.0% | 0.0% | 0.0% | 94.7% | 0.0% |
| 90434 | 1,745 | 2.0% | 0.0% | 0.0% | 0.0% | 98.0% | 0.0% |
| 90468 | 1,939 | 4.7% | 0.0% | 0.0% | 0.0% | 95.3% | 0.0% |
| 90493 | 1,491 | 2.8% | 0.0% | 0.0% | 0.0% | 97.2% | 0.0% |
| 90494 | 2,041 | 3.1% | 0.0% | 0.0% | 0.0% | 96.9% | 0.0% |
| 90590 | 990 | 2.7% | 0.0% | 0.0% | 0.0% | 97.3% | 0.0% |

### Across birds

| Zone | Minimum | Median | Maximum |
|---|---|---|---|
| New Zealand EEZ | 0.3% | 2.3% | 7.6% |
| Australian EEZ | 0.0% | 0.0% | 0.0% |
| Other named EEZ | 0.0% | 0.0% | 0.0% |
| Overlapping claim or joint regime | 0.0% | 0.0% | 0.0% |
| Outside all EEZs | 92.4% | 97.7% | 99.7% |
| Land gap inside New Zealand EEZ outline | 0.0% | 0.0% | 0.0% |

Birds with no foraging fix in the New Zealand EEZ: 0. Highest share: bird 41269, 7.6%.

### Foraging fixes inside the New Zealand EEZ and near the colony point

| Foraging fixes | Count | Share of foraging fixes | Share of NZ EEZ foraging fixes |
|---|---|---|---|
| Inside New Zealand EEZ | 1,043 | 2.72% | 100.00% |
| Inside NZ EEZ and within 50 km of colony point | 125 | 0.33% | 11.98% |
| Inside NZ EEZ and over 50 km from colony point | 918 | 2.39% | 88.02% |

## Part 4: sensitivity to boundary position

Distance method: each boundary line in the box was densified along WGS84 geodesics to 0.5 km spacing, excluding types Archipelagic baseline, Connection line, Normal baseline (official), Straight baseline. For each fix, the 8 nearest vertices in earth-centred 3-D coordinates were found, then the WGS84 geodesic distance to each was computed and the smallest kept. No map projection is involved, so the 180 meridian has no effect. The vertex spacing can overstate a distance by up to about 0.25 km for a fix on a line, and less further away.

| LINE_ID | LINE_NAME | LINE_TYPE | Used for distance | LENGTH_KM |
|---|---|---|---|---|
| 2064 | Macquarie Island (Australia) 200 NM | 200 NM | Yes | 1,509.5 |
| 2059 | Australia 200 NM | 200 NM | Yes | 10,790.7 |
| 1289 | Norfolk Island (Australia) - New Zealand | Treaty | Yes | 169.5 |
| 4020 | Norfolk Island (Australia) - New Zealand | Treaty | Yes | 650.2 |
| 2062 | New Zealand 200 NM | 200 NM | Yes | 10,379.9 |
| 4096 | New Zealand 200 NM | 200 NM | Yes | 890.0 |
| 4631 | Macquarie Island (Australia) Straight Baseline | Straight baseline | No (baseline) | 43.2 |
| 4632 | Macquarie Island (Australia) Normal Baseline | Normal baseline (official) | No (baseline) | 58.0 |
| 4615 | New Zealand - Macquarie Island (Australia) | Treaty | Yes | 959.0 |

| Within | Foraging fixes | Share of foraging fixes | All fixes | Share of all fixes |
|---|---|---|---|---|
| 5 km | 19 | 0.05% | 174 | 0.19% |
| 10 km | 72 | 0.19% | 422 | 0.45% |
| 20 km | 189 | 0.49% | 1,033 | 1.11% |

Nearest line for foraging fixes within 10 km:

| Nearest boundary line | Foraging fixes within 10 km |
|---|---|
| New Zealand 200 NM (LINE_ID 2062) | 72 |

### Worst cases for foraging fixes

| Case | New Zealand EEZ | Outside all EEZs | Land gap |
|---|---|---|---|
| As classified | 1,043 (2.72%) | 37,336 (97.28%) | 0 (0.00%) |
| All fixes within 10 km of a boundary assigned to NZ EEZ | 1,076 (2.80%) | 37,303 (97.20%) | 0 (0.00%) |
| All fixes within 10 km of a boundary assigned to outside | 1,004 (2.62%) | 37,375 (97.38%) | 0 (0.00%) |

Within 10 km of a boundary: 39 foraging fixes classified NZ EEZ, 33 classified outside, 0 other.

## Part 5: old latitude bands against the real classification (foraging fixes)

| Old latitude label | New Zealand EEZ | Australian EEZ | Other named EEZ | Overlapping claim or joint regime | Outside all EEZs | Land gap inside New Zealand EEZ outline | Total |
|---|---|---|---|---|---|---|---|
| South of 60S (CCAMLR label) | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 362 (100.00%) | 0 (0.00%) | 362 |
| 60S to 48.8S (NZ EEZ / Subantarctic label) | 1,043 (2.79%) | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 36,381 (97.21%) | 0 (0.00%) | 37,424 |
| North of 48.8S (High Seas / FAO 81 label) | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 593 (100.00%) | 0 (0.00%) | 593 |

Of 37,424 foraging fixes labelled NZ EEZ / Subantarctic by latitude, 1,043 (2.79%) are inside the New Zealand EEZ and 36,381 (97.21%) are outside all EEZs.

## Part 6: check maps

- `check_map_all_tracks_by_zone.png`
- `check_map_foraging_fixes_by_zone.png`

Check maps, not for publication. Longitudes are shifted to 0-360 for display only, with the New Zealand parts merged at 180 so no seam is drawn. The per-fix table is `fix_classification.csv` (not committed).

## Caveats

- These are 24 adult birds tracked while incubating, on away trips of 7.6 to 21.8 days each (full records 7.7 to 21.9 days), between mid October and mid December 2013.
- The Movebank reference data records all 24 birds as adult and incubating (fields animal-life-stage and animal-reproductive-condition).
- EEZ boundaries are legal limits, not ecological ones.
- Overlapping or disputed claims are reported separately; none intersects the track box.
- No fishing data was used in this analysis.
- The licence file states that "The data has no legal value whatsoever" and that VLIZ "expresses no opinion about the legal state neither of any country, territory or area nor concerning its delimitation, frontier or borders".
- Shares are shares of GPS fixes. Foraging, transiting and resting are inferred HMM states.
- The CCAMLR test is the 60S latitude line, not a boundary file.
