"""
Point-in-polygon classification of fixes against World EEZ v12, using the same method
as eez_test/run_eez_test.py: raw longitudes (-180 to 180) against unmodified polygons.

Boundary data: Flanders Marine Institute (2023). Maritime Boundaries Geodatabase:
Maritime Boundaries and Exclusive Economic Zones (200NM), version 12. Available online
at https://www.marineregions.org/. https://doi.org/10.14284/632 (licence CC BY 4.0).
Download it to data/external/eez/World_EEZ_v12_20231025_gpkg/.

The CCAMLR test is latitude below -60: the boundary in this sector is the 60S line.
"""
from pathlib import Path

import geopandas as gpd
import numpy as np
import shapely
from shapely.geometry import box

EEZ_POLYGONS = Path('data/external/eez/World_EEZ_v12_20231025_gpkg/eez_v12.gpkg')
EEZ_LINES = Path('data/external/eez/World_EEZ_v12_20231025_gpkg/eez_boundaries_v12.gpkg')
NZ_MRGID = 8455
CCAMLR_LAT = -60.0
Z_NZ = 'New Zealand EEZ'
Z_AU = 'Australian EEZ'
Z_OTHER = 'Other named EEZ'
Z_OVERLAP = 'Overlapping claim or joint regime'
Z_OUT = 'Outside all EEZs'
Z_GAP = 'Land gap inside New Zealand EEZ outline'
ZONES = [Z_NZ, Z_AU, Z_OTHER, Z_OVERLAP, Z_OUT, Z_GAP]


def features_near_tracks(lon, lat, margin=10):
    """EEZ features intersecting the tracks' bounding box plus a margin."""
    l360 = np.asarray(lon) % 360
    west, east = l360.min() - margin, l360.max() + margin
    south, north = np.min(lat) - margin, np.max(lat) + margin
    eez = gpd.read_file(EEZ_POLYGONS)
    near = eez.intersects(box(west, south, 180, north)) | eez.intersects(box(-180, south, east - 360, north))
    return eez[near].reset_index(drop=True)


def classify_fixes(lon, lat):
    """Return (zone array, south-of-60S boolean array) for raw longitudes and latitudes."""
    lon, lat = np.asarray(lon), np.asarray(lat)
    near = features_near_tracks(lon, lat)
    pts = gpd.GeoSeries(gpd.points_from_xy(lon, lat), crs=4326)
    zone = np.full(len(lon), Z_OUT, dtype=object)
    for i, j in zip(*near.sindex.query(pts, predicate='intersects')):
        f = near.iloc[j]
        if f.POL_TYPE != '200NM':
            zone[i] = Z_OVERLAP
        elif f.MRGID == NZ_MRGID:
            zone[i] = Z_NZ
        elif f.SOVEREIGN1 == 'Australia':
            zone[i] = Z_AU
        else:
            zone[i] = Z_OTHER
    # The polygons exclude land, so a fix on an island inside the outline is its own category
    nz = near.loc[near.MRGID == NZ_MRGID, 'geometry'].iloc[0]
    filled = shapely.union_all([shapely.Polygon(p.exterior) for p in nz.geoms])
    zone[pts.within(filled).values & (zone == Z_OUT)] = Z_GAP
    return zone, lat < CCAMLR_LAT
