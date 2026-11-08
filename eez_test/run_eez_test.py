"""Point-in-polygon test of the v3 tracks against World EEZ v12.
Writes outputs_v3/eez/eez_report.md, two check maps and fix_classification.csv.
Run from the repository root: python3 eez_test/run_eez_test.py
No network use; reads only data/processed_v3 and data/external/eez."""
import hashlib
import platform
import sqlite3
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
import pyogrio
import pyproj
import scipy
import shapely
from pyproj import Geod, Transformer
from scipy.spatial import cKDTree
from shapely.geometry import Point, box
from shapely.ops import transform as shp_transform

OUT = Path('outputs_v3/eez')
OUT.mkdir(parents=True, exist_ok=True)
DIR = Path('data/external/eez/World_EEZ_v12_20231025_gpkg')
POLY, LINES, LIC = DIR / 'eez_v12.gpkg', DIR / 'eez_boundaries_v12.gpkg', DIR / 'LICENSE_EEZ_v12.txt'
TRACKS = Path('data/processed_v3/tracks_with_behaviour.csv')
DEP_LAT, DEP_LON = -52.474, 169.224
NZ, AU_MAC = 8455, 8311
Z_NZ, Z_AU, Z_OTHER, Z_OVER, Z_OUT, Z_GAP = ('New Zealand EEZ', 'Australian EEZ', 'Other named EEZ',
                                             'Overlapping claim or joint regime', 'Outside all EEZs',
                                             'Land gap inside New Zealand EEZ outline')
ZONES = [Z_NZ, Z_AU, Z_OTHER, Z_OVER, Z_OUT, Z_GAP]
STATES = [(1, 'Foraging'), (2, 'Transiting'), (0, 'Resting')]
GEOD = Geod(ellps='WGS84')
ECEF = Transformer.from_crs('EPSG:4326', 'EPSG:4978', always_xy=True)
BOUNDARY_EXCLUDED_TYPES = {'Straight baseline', 'Normal baseline (official)', 'Archipelagic baseline', 'Connection line'}
INK, MUTED = '#0b0b0b', '#52514e'
COLOURS = {Z_NZ: '#2a78d6', Z_OUT: '#eb6834', Z_GAP: '#1baf7a'}


def md(head, rows):
    return ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)] + \
           ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]


def cp(n, tot):
    return f'{n:,} ({n / tot * 100:.2f}%)' if tot else '0'


def densify(coords, step_km=0.5):
    """Geodesically densify one line (lon, lat array); safe across the dateline."""
    out = []
    for (x0, y0), (x1, y1) in zip(coords[:-1], coords[1:]):
        out.append((x0, y0))
        d = GEOD.inv(x0, y0, x1, y1)[2] / 1000
        if d > step_km:
            out.extend(GEOD.npts(x0, y0, x1, y1, int(np.ceil(d / step_km)) - 1))
    out.append(tuple(coords[-1]))
    return np.array(out)


def line_parts(g):
    return [np.asarray(p.coords)[:, :2] for p in (g.geoms if hasattr(g, 'geoms') else [g])]


def xyz(lon, lat):
    return np.column_stack(ECEF.transform(lon, lat, np.zeros(len(lon))))


def nearest(tree, vx, vy, lon, lat, k=8):
    """Smallest WGS84 geodesic distance (km) among the k nearest vertices in 3-D."""
    _, idx = tree.query(xyz(lon, lat), k=k)
    best = np.full(len(lon), np.inf)
    who = np.zeros(len(lon), dtype=int)
    for c in range(k):
        i = idx[:, c]
        d = GEOD.inv(lon, lat, vx[i], vy[i])[2] / 1000
        better = d < best
        best[better], who[better] = d[better], i[better]
    return best, who


# ---------------------------------------------------------------- Part 1
t = pd.read_csv(TRACKS, low_memory=False, parse_dates=['timestamp'])
t = t.sort_values(['individual-local-identifier', 'timestamp']).reset_index(drop=True)
t['bird'] = t['individual-local-identifier'].astype(str)
LON, LAT = t['location-long'].values, t['location-lat'].values
assert LON.min() >= -180 and LON.max() <= 180
l360 = LON % 360
box_w, box_e, box_s, box_n = l360.min() - 10, l360.max() + 10, LAT.min() - 10, LAT.max() + 10
boxes = [box(box_w, box_s, 180, box_n), box(-180, box_s, box_e - 360, box_n)]

e = gpd.read_file(POLY)
L = gpd.read_file(LINES)
near = e[e.intersects(boxes[0]) | e.intersects(boxes[1])].copy()
Ln = L[L.intersects(boxes[0]) | L.intersects(boxes[1])].copy()
info = pyogrio.read_info(POLY)
linfo = pyogrio.read_info(LINES)
meta = {}
for f in (POLY, LINES):
    c = sqlite3.connect(f'file:{f}?mode=ro', uri=True)
    meta[f.name] = c.execute('select last_change from gpkg_contents').fetchone()[0]
    c.close()

seam = []
for _, r in near.iterrows():
    parts = list(r.geometry.geoms) if hasattr(r.geometry, 'geoms') else [r.geometry]
    seam.append([r.GEONAME, len(parts), sum(p.bounds[2] >= 179.9999999 for p in parts),
                 sum(p.bounds[0] <= -179.9999999 for p in parts), sum(len(p.interiors) for p in parts),
                 ', '.join(f'{v:.3f}' for v in r.geometry.bounds)])
nzg = e.loc[e.MRGID == NZ, 'geometry'].iloc[0]
east = [p for p in nzg.geoms if p.bounds[2] >= 179.9999999][0]
west = [p for p in nzg.geoms if p.bounds[0] <= -179.9999999][0]
ve = shapely.get_coordinates(east.exterior)
vw = shapely.get_coordinates(west.exterior)
ye = ve[np.abs(ve[:, 0] - 180) < 1e-7, 1]
yw = vw[np.abs(vw[:, 0] + 180) < 1e-7, 1]
seam_text = (f'East part vertices on +180: latitude {ye.min():.6f} to {ye.max():.6f}. '
             f'West part vertices on -180: latitude {yw.min():.6f} to {yw.max():.6f}.')

# ---------------------------------------------------------------- Part 2
TESTS = [('Deployment site', -52.474, 169.224, 'New Zealand EEZ (per the task)'),
         ('60S, 169E', -60, 169, 'None: south of the NZ limit (55.949S) and the Macquarie limit (58.449S)'),
         ('52.5S, 175W', -52.5, -175, 'None'),
         ('40S, 150W', -40, -150, 'None: east of the NZ limit (171.201W)'),
         ('50S, 100E', -50, 100, 'None: west of the Australian limit (109.233E)'),
         ('Added control: 52.0S, 169.2E (sea north of Campbell)', -52.0, 169.2, 'New Zealand EEZ'),
         ('Added control: 55S, 160E', -55, 160, 'Australian EEZ (Macquarie Island)'),
         ('Added control: 48S, 179.999E (seam)', -48, 179.999, 'New Zealand EEZ'),
         ('Added control: 48S, 179.999W (seam)', -48, -179.999, 'New Zealand EEZ'),
         ('Added control: 55S, 179.999E (seam)', -55, 179.999, 'None'),
         ('Added control: 55S, 179.999W (seam)', -55, -179.999, 'None')]
test_rows = []
for name, y, x, exp in TESTS:
    hit = e[e.intersects(Point(x, y))].GEONAME.tolist()
    test_rows.append([name, f'{y}, {x}', exp, '; '.join(hit) or 'None'])
gap_hole = None
for p in nzg.geoms:
    for r in p.interiors:
        h = shapely.Polygon(r)
        if h.contains(Point(DEP_LON, DEP_LAT)):
            gap_hole = h.bounds
assert gap_hole is not None

# ---------------------------------------------------------------- Part 3
pts = gpd.GeoSeries(gpd.points_from_xy(LON, LAT), crs=4326)
ii, jj = near.sindex.query(pts, predicate='intersects')
hits = pd.Series(ii).value_counts()
n_multi = int((hits > 1).sum())
t['zone'] = Z_OUT
t['feature'] = ''
for i, j in zip(ii, jj):
    f = near.iloc[j]
    if f.POL_TYPE != '200NM':
        z = Z_OVER
    elif f.MRGID == NZ:
        z = Z_NZ
    elif f.SOVEREIGN1 == 'Australia':
        z = Z_AU
    else:
        z = Z_OTHER
    t.iat[i, t.columns.get_loc('zone')] = z
    t.iat[i, t.columns.get_loc('feature')] = f.GEONAME
gap_rows = []
for _, f in near.iterrows():
    parts = f.geometry.geoms if hasattr(f.geometry, 'geoms') else [f.geometry]
    filled = shapely.union_all([shapely.Polygon(p.exterior) for p in parts])
    g = pts.within(filled).values & (t.zone == Z_OUT).values
    gap_rows.append([f.GEONAME, int(g.sum())])
    if f.MRGID == NZ:
        t.loc[g, 'zone'] = Z_GAP
    else:
        assert not g.any(), 'land-gap fix in a feature other than NZ'
t['south_of_60S'] = t['location-lat'] < -60

# Consecutive fixes crossing the 180 meridian must not change zone just by crossing
same = t.bird == t.bird.shift()
crossed = same & (np.abs(t['location-long'] - t['location-long'].shift()) > 180)
n_cross = int(crossed.sum())
cross_change = int((crossed & (t.zone != t.zone.shift())).sum())
crossing_detail = t.loc[crossed & (t.zone != t.zone.shift()), ['bird', 'timestamp', 'location-long', 'location-lat']]

# ---------------------------------------------------------------- Part 4
blines = Ln[~Ln.LINE_TYPE.isin(BOUNDARY_EXCLUDED_TYPES)]
vs, ids = [], []
for idx, r in blines.iterrows():
    for part in line_parts(r.geometry):
        d = densify(part)
        vs.append(d)
        ids.append(np.full(len(d), r.LINE_ID))
V = np.vstack(vs)
V_ID = np.concatenate(ids)
tree = cKDTree(xyz(V[:, 0], V[:, 1]))
t['dist_boundary_km'], who = nearest(tree, V[:, 0], V[:, 1], LON, LAT)
t['nearest_line'] = V_ID[who]

# Boundary lines versus polygon outline for the New Zealand EEZ
nz_lines = L[(L.MRGID_EEZ1 == NZ) | (L.MRGID_EEZ2 == NZ)]
nz_outer = nz_lines[~nz_lines.LINE_TYPE.isin(BOUNDARY_EXCLUDED_TYPES)]
ln = np.vstack([densify(p) for g in nz_outer.geometry for p in line_parts(g)])
ring_pts = [densify(shapely.get_coordinates(p.exterior)) for p in nzg.geoms]
ring = np.vstack(ring_pts)
on_seam = np.abs(np.abs(ring[:, 0]) - 180) < 1e-7
# Interior rings: land gaps, plus non-land pockets enclosed by the 200 NM arcs. Boundary lines run
# along the pockets, so the line-to-polygon check has to include interior rings.
inner = [densify(shapely.get_coordinates(r)) for p in nzg.geoms for r in p.interiors]
all_rings = np.vstack([ring] + inner)
ring_tree, line_tree = cKDTree(xyz(all_rings[:, 0], all_rings[:, 1])), cKDTree(xyz(ln[:, 0], ln[:, 1]))
# Each line against every ring of the polygons it names (treaty lines also border the partner EEZ)
per_line = []
for _, r in nz_outer.iterrows():
    named = [m for m in (r.MRGID_EEZ1, r.MRGID_EEZ2) if pd.notna(m)]
    rr = []
    for g in e[e.MRGID.isin(named)].geometry:
        for p in (g.geoms if hasattr(g, 'geoms') else [g]):
            rr.append(densify(shapely.get_coordinates(p.exterior)))
            rr += [densify(shapely.get_coordinates(q)) for q in p.interiors]
    rr = np.vstack(rr)
    pts_l = np.vstack([densify(q) for q in line_parts(r.geometry)])
    d, _ = nearest(cKDTree(xyz(rr[:, 0], rr[:, 1])), rr[:, 0], rr[:, 1], pts_l[:, 0], pts_l[:, 1])
    per_line.append([r.LINE_ID, r.LINE_NAME, r.LINE_TYPE, r.EEZ1, r.EEZ2 if pd.notna(r.EEZ2) else '', f'{len(pts_l):,}',
                     f'{np.median(d):.3f}', f'{d.max():.3f}', f'{(d > 1).mean() * 100:.2f}%'])
# Interior rings large enough to show on the maps, with the fixes inside each
large = []
for p in nzg.geoms:
    for r in p.interiors:
        h = shapely.Polygon(r)
        if h.area > 0.003 and -56 < h.bounds[1] and h.bounds[3] < -38:
            on_line = np.median(nearest(line_tree, ln[:, 0], ln[:, 1], *shapely.get_coordinates(r).T)[0])
            large.append([', '.join(f'{v:.3f}' for v in h.bounds), f'{on_line:.3f} km', int(pts.within(h).sum()),
                          'Boundary line (non-land pocket)' if on_line < 1 else 'No boundary line (land gap)'])
camp = shapely.Polygon([r for p in nzg.geoms for r in p.interiors if shapely.Polygon(r).contains(Point(DEP_LON, DEP_LAT))][0])
assert all(camp.contains(Point(x, y)) for x, y in zip(t.loc[t.zone == Z_GAP, 'location-long'], t.loc[t.zone == Z_GAP, 'location-lat']))
d_r2l, _ = nearest(line_tree, ln[:, 0], ln[:, 1], ring[:, 0], ring[:, 1])
d_ns = d_r2l[~on_seam]
far = ring[~on_seam][d_ns > 1]

# ---------------------------------------------------------------- Output CSV
out = pd.DataFrame({'event-id': t['event-id'], 'bird': t.bird, 'timestamp': t.timestamp, 'behaviour': t.behaviour,
                    'longitude': t['location-long'], 'latitude': t['location-lat'], 'zone': t.zone,
                    'south_of_60S': t.south_of_60S, 'distance_to_nearest_boundary_km': t.dist_boundary_km.round(3)})
out.to_csv(OUT / 'fix_classification.csv', index=False)

# ---------------------------------------------------------------- Tables
fo = t[t.behaviour == 1]
N = len(fo)
rows = []
groups = [(n, t[t.behaviour == s]) for s, n in STATES] + [('All fixes', t)]
for z in ZONES:
    rows.append([z] + [cp(int((g.zone == z).sum()), len(g)) for _, g in groups])
rows.append(['Total'] + [f'{len(g):,}' for _, g in groups])
T_state = md(['Zone'] + [n for n, _ in groups], rows)

T_cross = md(['Zone', 'North of or on 60S', 'South of 60S', 'Total'],
             [[z, cp(int(((fo.zone == z) & ~fo.south_of_60S).sum()), N), cp(int(((fo.zone == z) & fo.south_of_60S).sum()), N),
               cp(int((fo.zone == z).sum()), N)] for z in ZONES] +
             [['Total', cp(int((~fo.south_of_60S).sum()), N), cp(int(fo.south_of_60S.sum()), N), f'{N:,}']])

pb = pd.crosstab(fo.bird, fo.zone).reindex(columns=ZONES, fill_value=0)
ps = pb.div(pb.sum(axis=1), axis=0) * 100
ps = ps.loc[sorted(ps.index, key=int)]
T_bird = md(['Bird', 'Foraging fixes'] + ZONES, [[b, f'{int(pb.loc[b].sum()):,}'] + [f'{ps.loc[b, z]:.1f}%' for z in ZONES] for b in ps.index])
T_sum = md(['Zone', 'Minimum', 'Median', 'Maximum'], [[z, f'{ps[z].min():.1f}%', f'{ps[z].median():.1f}%', f'{ps[z].max():.1f}%'] for z in ZONES])
zero_nz = [b for b in ps.index if ps.loc[b, Z_NZ] == 0]
most_nz = ps[Z_NZ].idxmax()

fnz = fo[fo.zone == Z_NZ]
c50 = fnz.dist_from_campbell <= 50
T_50 = md(['Foraging fixes', 'Count', 'Share of foraging fixes', 'Share of NZ EEZ foraging fixes'],
          [['Inside New Zealand EEZ', f'{len(fnz):,}', f'{len(fnz) / N * 100:.2f}%', '100.00%'],
           ['Inside NZ EEZ and within 50 km of colony point', f'{int(c50.sum()):,}', f'{c50.sum() / N * 100:.2f}%', f'{c50.mean() * 100:.2f}%'],
           ['Inside NZ EEZ and over 50 km from colony point', f'{int((~c50).sum()):,}', f'{(~c50).sum() / N * 100:.2f}%', f'{(~c50).mean() * 100:.2f}%']])

T_near = md(['Within', 'Foraging fixes', 'Share of foraging fixes', 'All fixes', 'Share of all fixes'],
            [[f'{k} km', f'{int((fo.dist_boundary_km <= k).sum()):,}', f'{(fo.dist_boundary_km <= k).mean() * 100:.2f}%',
              f'{int((t.dist_boundary_km <= k).sum()):,}', f'{(t.dist_boundary_km <= k).mean() * 100:.2f}%'] for k in (5, 10, 20)])
nr = fo[fo.dist_boundary_km <= 10]
line_names = Ln.set_index('LINE_ID').LINE_NAME
T_nearby = md(['Nearest boundary line', 'Foraging fixes within 10 km'],
              [[f'{line_names[k]} (LINE_ID {k})', f'{v:,}'] for k, v in nr.nearest_line.value_counts().items()])
base_nz = int((fo.zone == Z_NZ).sum())
near_out = int(((fo.dist_boundary_km <= 10) & (fo.zone == Z_OUT)).sum())
near_nz = int(((fo.dist_boundary_km <= 10) & (fo.zone == Z_NZ)).sum())
near_other = int(((fo.dist_boundary_km <= 10) & ~fo.zone.isin([Z_NZ, Z_OUT])).sum())
base_out = int((fo.zone == Z_OUT).sum())
gap_f = int((fo.zone == Z_GAP).sum())
T_case = md(['Case', 'New Zealand EEZ', 'Outside all EEZs', 'Land gap'],
            [['As classified', cp(base_nz, N), cp(base_out, N), cp(gap_f, N)],
             ['All fixes within 10 km of a boundary assigned to NZ EEZ', cp(base_nz + near_out, N), cp(base_out - near_out, N), cp(gap_f, N)],
             ['All fixes within 10 km of a boundary assigned to outside', cp(base_nz - near_nz, N), cp(base_out + near_nz, N), cp(gap_f, N)]])


def old_band(lat):
    return 'South of 60S (CCAMLR label)' if lat < -60 else ('60S to 48.8S (NZ EEZ / Subantarctic label)' if lat < -48.8 else 'North of 48.8S (High Seas / FAO 81 label)')


fo = fo.assign(old=fo['location-lat'].map(old_band))
BANDS = ['South of 60S (CCAMLR label)', '60S to 48.8S (NZ EEZ / Subantarctic label)', 'North of 48.8S (High Seas / FAO 81 label)']
T_old = md(['Old latitude label'] + ZONES + ['Total'],
           [[b] + [cp(int(((fo.old == b) & (fo.zone == z)).sum()), int((fo.old == b).sum())) for z in ZONES] + [f'{int((fo.old == b).sum()):,}'] for b in BANDS])
mid = fo[fo.old == BANDS[1]]

# Duration facts used in the caveats
trips = pd.read_csv('data/processed_v3/trip_statistics.csv')
rec = t.groupby('bird').timestamp.agg(lambda s: (s.max() - s.min()).total_seconds() / 86400)
assert round(trips.duration_days.min(), 1) == 7.6 and round(trips.duration_days.max(), 1) == 21.8
assert round(rec.min(), 1) == 7.7 and round(rec.max(), 1) == 21.9
ref = pd.read_csv('data/raw/movebank_reference_data.csv', dtype=str, keep_default_na=False)
assert len(ref) == 24 and set(ref['animal-life-stage']) == {'adult'} and set(ref['animal-reproductive-condition']) == {'incubating'}
assert t.timestamp.min().strftime('%Y-%m') == '2013-10' and t.timestamp.max().strftime('%Y-%m') == '2013-12'


# ---------------------------------------------------------------- Part 6: maps
def shift(g):
    """Display only: move negative longitudes to 180-360."""
    return shp_transform(lambda x, y, z=None: (np.where(np.asarray(x) < 0, np.asarray(x) + 360, x), y), g)


display = {}
for _, r in near.iterrows():
    parts = list(r.geometry.geoms) if hasattr(r.geometry, 'geoms') else [r.geometry]
    display[r.GEONAME] = shapely.union_all([shift(p) for p in parts])


def draw(path, data, title):
    fig, ax = plt.subplots(figsize=(13, 8.5), facecolor='#fcfcfb')
    ax.set_facecolor('#fcfcfb')
    x0, x1, y0, y1 = 155, 220, -64.5, -38
    for name, g in display.items():
        for p in (g.geoms if hasattr(g, 'geoms') else [g]):
            ax.plot(*p.exterior.xy, color=MUTED, lw=1.1, zorder=3)
            for r in p.interiors:
                if shapely.Polygon(r).area > 0.003:
                    ax.plot(*r.xy, color=MUTED, lw=.7, zorder=3)
    for z, size in [(Z_OUT, 1.2), (Z_NZ, 1.2)]:
        d = data[data.zone == z]
        ax.scatter(d['location-long'] % 360, d['location-lat'], s=size, color=COLOURS[z], linewidths=0, zorder=2, rasterized=True)
    d = data[data.zone == Z_GAP]
    if len(d):
        ax.scatter(d['location-long'] % 360, d['location-lat'], s=45, color=COLOURS[Z_GAP], edgecolors='#fcfcfb', linewidths=1.2, zorder=5)
    ax.axhline(-60, color=INK, lw=1.1, ls=(0, (6, 4)), zorder=3)
    ax.text(218.7, -59.75, '60°S', color=INK, fontsize=13, ha='right', va='bottom')
    ax.scatter(DEP_LON, DEP_LAT, marker='*', s=260, color=INK, edgecolors='#fcfcfb', linewidths=1.1, zorder=6)
    ax.annotate('Deployment site', (DEP_LON, DEP_LAT), xytext=(162.0, -49.4), fontsize=12.5, color=INK,
                arrowprops=dict(arrowstyle='-', color=INK, lw=.8), zorder=6, ha='center')
    ax.text(178, -47.2, 'New Zealand EEZ', fontsize=13, color=INK, ha='center', zorder=6, bbox=dict(fc='#fcfcfb', ec='none', alpha=.85, pad=2))
    ax.text(158.6, -56.9, 'Australian EEZ\n(Macquarie I.)', fontsize=12, color=INK, ha='center', zorder=6, bbox=dict(fc='#fcfcfb', ec='none', alpha=.85, pad=2))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect(1 / np.cos(np.radians(51)))
    xt = range(160, 221, 10)
    ax.set_xticks(list(xt)); ax.set_xticklabels([f'{v}°E' if v <= 180 else f'{360 - v}°W' for v in xt], fontsize=12, color=MUTED)
    yt = range(-60, -37, 5)
    ax.set_yticks(list(yt)); ax.set_yticklabels([f'{-v}°S' for v in yt], fontsize=12, color=MUTED)
    ax.grid(color='#e6e5e0', lw=.6, zorder=0)
    for s in ax.spines.values():
        s.set_color('#d5d4cf')
    ax.set_title(title, fontsize=15, color=INK, loc='left', pad=12, fontweight='bold')
    n = len(data)
    handles = [Line2D([], [], marker='o', ls='', ms=8, color=COLOURS[z], label=f'{z}: {int((data.zone == z).sum()):,} ({(data.zone == z).mean() * 100:.1f}%)') for z in (Z_NZ, Z_OUT)]
    if len(d):
        handles.append(Line2D([], [], marker='o', ls='', ms=8, color=COLOURS[Z_GAP], label=f'{Z_GAP}: {len(d):,}'))
    handles += [Line2D([], [], color=MUTED, lw=1.1, label='EEZ outline (World EEZ v12)'),
                Line2D([], [], color=INK, lw=1.1, ls=(0, (6, 4)), label='60°S line'),
                Line2D([], [], marker='*', ls='', ms=14, color=INK, label='Deployment site')]
    ax.legend(handles=handles, loc='lower center', ncol=3, fontsize=11, frameon=True, facecolor='#fcfcfb', edgecolor='#d5d4cf', labelcolor=INK, bbox_to_anchor=(.5, .012))
    fig.text(.012, .012, 'Longitudes shifted to 0–360 for display only. Classification used raw longitudes. Boundaries: Flanders Marine Institute (2023), CC BY 4.0.',
             fontsize=10.5, color=MUTED)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='#fcfcfb')
    plt.close(fig)


draw(OUT / 'check_map_all_tracks_by_zone.png', t, f'CHECK MAP, NOT FOR PUBLICATION: all {len(t):,} fixes by zone')
draw(OUT / 'check_map_foraging_fixes_by_zone.png', fo, f'CHECK MAP, NOT FOR PUBLICATION: {N:,} foraging fixes by zone')

# ---------------------------------------------------------------- Report
lic = LIC.read_text(encoding='utf-8-sig').strip()
sha = hashlib.sha256(POLY.read_bytes()).hexdigest()
sha2 = hashlib.sha256(LINES.read_bytes()).hexdigest()
feature_rows = [[r.MRGID, r.GEONAME, r.TERRITORY1, r.SOVEREIGN1, r.POL_TYPE, f'{int(r.AREA_KM2):,}'] for _, r in near.iterrows()]
line_rows = [[r.LINE_ID, r.LINE_NAME, r.LINE_TYPE, 'No (baseline)' if r.LINE_TYPE in BOUNDARY_EXCLUDED_TYPES else 'Yes', f'{r.LENGTH_KM:,.1f}'] for _, r in Ln.iterrows()]
gap_fix = t[t.zone == Z_GAP]
gap_desc = '; '.join(f"bird {r.bird}, {r.timestamp}, {r['location-lat']:.6f}, {r['location-long']:.6f}, behaviour {r.behaviour}" for _, r in gap_fix.iterrows())
R = ['# World EEZ v12 test of the v3 tracks', '',
     'Numbers and evidence only. Published wording was not changed.', '',
     '## Sources', '',
     '**Boundary data:** Flanders Marine Institute (2023). Maritime Boundaries Geodatabase: Maritime Boundaries and Exclusive Economic Zones (200NM), version 12. Available online at https://www.marineregions.org/. https://doi.org/10.14284/632. Licence: CC BY 4.0.', '',
     '**Track data:** Thompson, D.R., Torres, L.G., Sagar, P.M., Kroeger, C.E. and Orben, R.A. (2017). Grey-headed albatross, New Zealand (data from Torres et al. 2017). Movebank Data Repository. doi:10.5441/001/1.694p666h/1.', '',
     '**Tracks used:** `data/processed_v3/tracks_with_behaviour.csv` (bird 90494 dates repaired, colony point 169.224E, 52.474S).', '',
     '### Which file was used for which step', '',
     *md(['File', 'Used for'],
         [[f'`{POLY.name}`', 'Point-in-polygon classification (Part 3), known-point tests (Part 2), map outlines (Part 6)'],
          [f'`{LINES.name}`', 'Distance to nearest boundary (Part 4). It holds the legal limits as lines, without the coastline and without the artificial edge at 180 degrees that the polygon outlines contain.'],
          [f'`{LIC.name}`', 'Licence wording below']]), '',
     '### Licence wording, quoted from `LICENSE_EEZ_v12.txt`', '',
     *['> ' + x if x.strip() else '>' for x in lic.splitlines()], '',
     'The boundary files are not committed to this repository (`data/external/` is listed in `.git/info/exclude`).', '',
     '### Software', '',
     f'Python {platform.python_version()}; geopandas {gpd.__version__}, shapely {shapely.__version__} (GEOS {shapely.geos_version_string}), pyogrio {pyogrio.__version__}, pyproj {pyproj.__version__} (PROJ {pyproj.proj_version_str}), scipy {scipy.__version__}, numpy {np.__version__}, pandas {pd.__version__}.', '',
     '## Part 1: boundary file', '',
     *md(['File', 'Size (bytes)', 'SHA-256', 'Layer', 'CRS', 'Geometry', 'Features', 'Last change stored in file'],
         [[POLY.name, f'{POLY.stat().st_size:,}', f'`{sha}`', 'eez_v12', info['crs'], info['geometry_type'], info['features'], meta[POLY.name]],
          [LINES.name, f'{LINES.stat().st_size:,}', f'`{sha2}`', 'eez_boundaries_v12', linfo['crs'], linfo['geometry_type'], linfo['features'], meta[LINES.name]]]), '',
     'Version evidence: the folder is named `World_EEZ_v12_20231025_gpkg`, the layer is `eez_v12`, and the licence file citation says version 12. The metadata stored inside the GeoPackage holds an empty QGIS template with no version, date, licence or citation text.', '',
     f"Polygon columns: {', '.join(info['fields'])}.", '',
     f"Line columns: {', '.join(linfo['fields'])}.", '',
     f'### Features intersecting the track bounding box plus 10 degrees', '',
     f'Box: longitude {box_w:.3f} to {box_e:.3f} in 0-360 form (split at 180 for the test), latitude {box_s:.3f} to {box_n:.3f}. Polygon type counts in the whole file: 200NM 229, Overlapping claim 35, Joint regime 21. None of the overlapping-claim or joint-regime features intersects the box.', '',
     *md(['MRGID', 'GEONAME', 'Territory', 'Sovereign', 'POL_TYPE', 'AREA_KM2'], feature_rows), '',
     f'- New Zealand EEZ: MRGID {NZ}.',
     f'- Australian EEZ around Macquarie Island: MRGID {AU_MAC}.',
     '- Others in the box: Australian EEZ (MRGID 8323) and Australian EEZ, Norfolk Island (MRGID 8310).', '',
     '### Splitting at the 180 degree meridian', '',
     *md(['GEONAME', 'Parts', 'Parts touching +180', 'Parts touching -180', 'Interior rings', 'Bounds (W, S, E, N)'], seam), '',
     f'The New Zealand EEZ is one MultiPolygon split at the meridian into two parts. {seam_text}', '',
     f'Handling: raw longitudes (-180 to 180) were tested against the unmodified polygons, which use the same range, so each side of the meridian is matched by its own part. No fix has a longitude of exactly +180 or -180. Across all birds, {n_cross:,} consecutive fix pairs cross the meridian and {cross_change:,} of those pairs change zone.', '',
     '## Part 2: validation', '',
     *md(['Point', 'Lat, lon', 'Expected', 'Result'], test_rows), '',
     f'**Unexpected result:** the deployment site is not inside any polygon. It falls in an interior ring of the New Zealand EEZ feature with bounds {gap_hole[0]:.3f}, {gap_hole[1]:.3f}, {gap_hole[2]:.3f}, {gap_hole[3]:.3f} (W, S, E, N), which is a land gap covering Campbell Island: the EEZ polygons exclude land. The other four requested points returned no feature, as expected from the file bounds. The added controls behaved as expected.', '',
     f'Because of this, a fix on land inside a polygon outline is reported as its own row, "{Z_GAP}", rather than as outside. Fixes per feature in such a gap: ' + '; '.join(f'{a}: {b}' for a, b in gap_rows) + f'. The New Zealand fix: {gap_desc or "none"}.', '',
     '### Boundary lines against polygons, New Zealand EEZ', '',
     f'Lines tested: {len(nz_outer)} features where New Zealand is named, excluding baselines. Both sets were densified to 0.5 km along geodesics.', '',
     *md(['Check', 'Result'],
         [ ['Outline points away from the 180 seam to nearest line point: median, maximum', f'{np.median(d_ns):.3f} km, {d_ns.max():.3f} km'],
          ['Outline points away from the seam more than 1 km from a line', f'{len(far):,} of {len(d_ns):,}'],
          ['Outline points on the 180 seam (no line expected)', f'{int(on_seam.sum()):,}']]), '',
     'Each boundary line against all rings (outer and interior) of the polygons named in its EEZ1 and EEZ2 fields. Treaty lines are tested against both parties because they extend beyond the New Zealand polygon.', '',
     *md(['LINE_ID', 'LINE_NAME', 'LINE_TYPE', 'EEZ1', 'EEZ2', 'Points', 'Median km', 'Maximum km', 'Points over 1 km'], per_line), '',
     f'Line 1289 does not lie on either polygon it names. It runs near 33S, 162 to 163E. Fixes for which it is the nearest boundary line: {int((t.nearest_line == 1289).sum()):,}. The boundary line closest to any fix within 20 km of a boundary: ' + ', '.join(f'LINE_ID {k} ({v:,} fixes)' for k, v in t.loc[t.dist_boundary_km <= 20, 'nearest_line'].value_counts().items()) + '.', '',
     'Interior rings of the New Zealand EEZ south of 38S with area over 0.003 square degrees. A ring is called a land gap or a non-land pocket according to whether a boundary line runs along it:', '',
     *md(['Bounds (W, S, E, N)', 'Median distance to a boundary line', 'Fixes inside', 'Type'], large), '',
     'The one fix in the "Land gap" row lies in the ring containing the deployment site.', '',
     '## Part 3: classification', '',
     f'Method: `sindex.query(points, predicate="intersects")` against the {len(near)} features in the box, on raw longitudes. Fixes hitting more than one feature: {n_multi}. CCAMLR test: latitude below -60, using the 60S line as the boundary for this longitude sector as specified for this task; no CCAMLR boundary file was used.', '',
     '### Zone shares by behaviour state', '', *T_state, '',
     '### Foraging fixes: zone by south of 60S', '', *T_cross, '',
     '### Foraging fixes per bird', '', *T_bird, '',
     '### Across birds', '', *T_sum, '',
     f'Birds with no foraging fix in the New Zealand EEZ: {len(zero_nz)}' + (f" ({', '.join(zero_nz)})." if zero_nz else '.') + f' Highest share: bird {most_nz}, {ps.loc[most_nz, Z_NZ]:.1f}%.', '',
     '### Foraging fixes inside the New Zealand EEZ and near the colony point', '', *T_50, '',
     '## Part 4: sensitivity to boundary position', '',
     f'Distance method: each boundary line in the box was densified along WGS84 geodesics to 0.5 km spacing, excluding types {", ".join(sorted(BOUNDARY_EXCLUDED_TYPES))}. For each fix, the 8 nearest vertices in earth-centred 3-D coordinates were found, then the WGS84 geodesic distance to each was computed and the smallest kept. No map projection is involved, so the 180 meridian has no effect. The vertex spacing can overstate a distance by up to about 0.25 km for a fix on a line, and less further away.', '',
     *md(['LINE_ID', 'LINE_NAME', 'LINE_TYPE', 'Used for distance', 'LENGTH_KM'], line_rows), '',
     *T_near, '', 'Nearest line for foraging fixes within 10 km:', '', *T_nearby, '',
     '### Worst cases for foraging fixes', '', *T_case, '',
     f'Within 10 km of a boundary: {near_nz:,} foraging fixes classified NZ EEZ, {near_out:,} classified outside, {near_other:,} other.', '',
     '## Part 5: old latitude bands against the real classification (foraging fixes)', '', *T_old, '',
     f'Of {len(mid):,} foraging fixes labelled NZ EEZ / Subantarctic by latitude, {int((mid.zone == Z_NZ).sum()):,} ({(mid.zone == Z_NZ).mean() * 100:.2f}%) are inside the New Zealand EEZ and {int((mid.zone == Z_OUT).sum()):,} ({(mid.zone == Z_OUT).mean() * 100:.2f}%) are outside all EEZs.', '',
     '## Part 6: check maps', '',
     '- `check_map_all_tracks_by_zone.png`', '- `check_map_foraging_fixes_by_zone.png`', '',
     'Check maps, not for publication. Longitudes are shifted to 0-360 for display only, with the New Zealand parts merged at 180 so no seam is drawn. The per-fix table is `fix_classification.csv` (not committed).', '',
     '## Caveats', '',
     '- These are 24 adult birds tracked while incubating, on away trips of 7.6 to 21.8 days each (full records 7.7 to 21.9 days), between mid October and mid December 2013.',
     '- The Movebank reference data records all 24 birds as adult and incubating (fields animal-life-stage and animal-reproductive-condition).',
     '- EEZ boundaries are legal limits, not ecological ones.',
     '- Overlapping or disputed claims are reported separately; none intersects the track box.',
     '- No fishing data was used in this analysis.',
     '- The licence file states that "The data has no legal value whatsoever" and that VLIZ "expresses no opinion about the legal state neither of any country, territory or area nor concerning its delimitation, frontier or borders".',
     '- Shares are shares of GPS fixes. Foraging, transiting and resting are inferred HMM states.',
     '- The CCAMLR test is the 60S latitude line, not a boundary file.', '']
(OUT / 'eez_report.md').write_text('\n'.join(R), encoding='utf-8')
print('\n'.join(R))
