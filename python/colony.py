"""Colony reference point, defined in one place and imported by every script.

The point is the deployment site in the Movebank reference data. All 24 rows must
agree. If the reference file is missing, the documented fallback below (the same
values, as read on 8 November 2026) is used and a warning is printed.
"""
from pathlib import Path

import numpy as np
import pandas as pd

REFERENCE_FILE = Path('data/raw/movebank_reference_data.csv')
FALLBACK_LAT, FALLBACK_LON = -52.474, 169.224


def _load():
    if not REFERENCE_FILE.exists():
        print(f'WARNING: {REFERENCE_FILE} not found; using fallback colony point '
              f'{FALLBACK_LAT}, {FALLBACK_LON}')
        return FALLBACK_LAT, FALLBACK_LON
    ref = pd.read_csv(REFERENCE_FILE, usecols=['deploy-on-latitude', 'deploy-on-longitude'])
    if ref.nunique().max() != 1:
        raise ValueError(f'{REFERENCE_FILE} holds more than one deployment site')
    return float(ref['deploy-on-latitude'].iloc[0]), float(ref['deploy-on-longitude'].iloc[0])


COLONY_LAT, COLONY_LON = _load()

# Longitudes are normalised around Campbell Island so that tracks crossing 180 stay continuous
CENTER_LON = 169


def normalize_lon(lon):
    """Shift a longitude into the range [CENTER_LON - 180, CENTER_LON + 180)."""
    return ((lon - CENTER_LON + 180) % 360) + CENTER_LON - 180


def circular_mean_lon(lons):
    """Circular mean of longitudes in degrees, normalised around Campbell Island."""
    radians = np.radians(np.asarray(lons, dtype=float))
    return float(normalize_lon(np.degrees(np.arctan2(np.sin(radians).mean(), np.cos(radians).mean()))))
