"""
Phase 4: Interactive Folium Map
Grey-headed Albatross Foraging Ecology Project

Produces a single self-contained HTML file combining:
    - Individual bird GPS tracks (togglable, coloured by behaviour state)
    - Foraging hotspot heatmap
    - CCAMLR longline fishing effort (scaled circle markers)
    - Campbell Island breeding colony marker
    - Per-bird popup statistics
    - Risk cluster labelling

Output:
    outputs/maps/albatross_interactive_map.html
"""

import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, MiniMap, MeasureControl
from pathlib import Path

Path('outputs/maps').mkdir(parents=True, exist_ok=True)

CCAMLR_DIR = Path('data/raw/ccamlr/CCAMLR_statistical bulletin_V37')

# Behaviour colours — matching portfolio palette
BEHAVIOUR_COLOURS = {
    0: '#AAAAAA',  # Resting — mid grey
    1: '#7FAD87',  # Foraging — green
    2: '#B794D9',  # Transiting — mauve
}
BEHAVIOUR_LABELS = {0: 'Resting', 1: 'Foraging', 2: 'Transiting'}

RISK_COLOURS = {
    'Low risk':    '#1a6b35',   # dark forest green
    'Medium risk': '#1a3a6b',   # dark navy
    'High risk':   '#8b1a1a',   # dark crimson
}

CAMPBELL_LAT =  -52.55
CAMPBELL_LON =  169.15

print("\n" + "=" * 70)
print("PHASE 4: INTERACTIVE FOLIUM MAP")
print("=" * 70)


# ============================================================================
# PART 1: LOAD DATA
# ============================================================================

print("\nLoading data...")

df       = pd.read_csv('data/processed/tracks_with_behaviour.csv',
                        parse_dates=['timestamp'])
profiles = pd.read_csv('data/processed/bird_risk_profiles.csv')
effort   = pd.read_csv(CCAMLR_DIR / 'Effort.csv')

for col in ['hook_count', 'fishing_days', 'month', 'year']:
    effort[col] = pd.to_numeric(effort[col], errors='coerce').fillna(0)

# Filter CCAMLR to 2013 longline
effort_2013 = effort[
    (effort['year'] == 2013) &
    (effort['gear_type_code'] == 'LLS')
].copy()

# Build lookup of risk labels per bird
risk_lookup = profiles.set_index('bird_id')[
    ['risk_label', 'max_dist_km', 'total_dist_km',
     'prop_foraging', 'prop_transiting', 'prop_resting',
     'forage_centre_lat', 'forage_centre_lon']
].to_dict('index')

bird_ids = df['individual-local-identifier'].unique()
print(f"  Birds: {len(bird_ids)}")
print(f"  GPS points (full): {len(df):,}")

# Subsample tracks for performance — every 4th point
# (still preserves track shape, reduces render load significantly)
df_sub = df.iloc[::4].copy().reset_index(drop=True)
print(f"  GPS points (subsampled 4x): {len(df_sub):,}")


# ============================================================================
# PART 2: DATELINE SPLIT FUNCTION
# ============================================================================

CENTER_LON = 169  # Campbell Island — all coordinates normalised around this

def normalize_lon(lon):
    """
    Shift any longitude into the range [CENTER_LON-180, CENTER_LON+180].
    This places Campbell Island at the centre of the coordinate system and
    moves the 'break point' to -11°W (western Atlantic), where no albatross
    data exists. A bird crossing from 179°E to -179°W becomes 179° to 181°
    — a continuous 2° step with no dateline jump.
    """
    return ((lon - CENTER_LON + 180) % 360) + CENTER_LON - 180

# ============================================================================
# PART 3: BUILD BASE MAP
# ============================================================================

print("\nBuilding base map...")

# Centre on Campbell Island; zoom 4 shows the full Southern Ocean
m = folium.Map(
    location=[CAMPBELL_LAT, CAMPBELL_LON + 11],
    zoom_start=4,
    tiles='CartoDB positron',
    prefer_canvas=True,
)

# Add minimap and measure control for usability
MiniMap(toggle_display=True).add_to(m)
MeasureControl(position='topleft', primary_length_unit='kilometers').add_to(m)


# ============================================================================
# PART 4: CAMPBELL ISLAND MARKER
# ============================================================================

folium.Marker(
    location=[CAMPBELL_LAT, CAMPBELL_LON],
    popup=folium.Popup(
        "<b>Campbell Island</b><br>"
        "Grey-headed albatross breeding colony<br>"
        "52.5°S, 169.2°E<br>"
        "24 birds tracked, 2013",
        max_width=200
    ),
    tooltip="Campbell Island (breeding colony)",
    icon=folium.Icon(color='red', icon='star', prefix='fa')
).add_to(m)


# ============================================================================
# PART 5: INDIVIDUAL BIRD TRACKS
# ============================================================================

print("\nAdding individual bird tracks...")

# Single FeatureGroup for all foraging centres — gives them one clean toggle
centres_group = folium.FeatureGroup(
    name='Foraging centres (click for statistics)', show=True
)

# Each bird gets its own FeatureGroup so it can be toggled independently
# in the layer control panel

for bird_id in bird_ids:

    bird_data = df_sub[df_sub['individual-local-identifier'] == bird_id]
    if len(bird_data) < 2:
        continue

    risk_info = risk_lookup.get(bird_id, {})
    risk_label = risk_info.get('risk_label', 'Unknown')
    track_colour = RISK_COLOURS.get(risk_label, '#888888')

    # Build popup HTML — shown when user clicks on the bird ID label
    popup_html = f"""
    <div style="font-family:sans-serif; font-size:13px; width:220px">
        <b>Bird {bird_id}</b>
        <hr style="margin:4px 0">
        <b>Risk profile:</b> {risk_label}<br>
        <b>Max distance:</b> {risk_info.get('max_dist_km', 'N/A'):.0f} km<br>
        <b>Total distance:</b> {risk_info.get('total_dist_km', 'N/A'):.0f} km<br>
        <hr style="margin:4px 0">
        <b>Time budget:</b><br>
        &nbsp; Foraging: {risk_info.get('prop_foraging', 0)*100:.1f}%<br>
        &nbsp; Transiting: {risk_info.get('prop_transiting', 0)*100:.1f}%<br>
        &nbsp; Resting: {risk_info.get('prop_resting', 0)*100:.1f}%<br>
        <hr style="margin:4px 0">
        <b>Foraging centre:</b><br>
        &nbsp; {risk_info.get('forage_centre_lat', 0):.1f}°S,
               {risk_info.get('forage_centre_lon', 0):.1f}°E
    </div>
    """

    # Create the FeatureGroup for this bird
    # show=True means visible by default; set to False for cleaner initial view
    bird_group = folium.FeatureGroup(
        name=f"Bird {bird_id} ({risk_label})",
        show=False
    )

    # Add an invisible marker at the foraging centre to carry the popup
    # (clicking a PolyLine in Folium doesn't always trigger popups reliably)
    forage_lat = risk_info.get('forage_centre_lat', CAMPBELL_LAT)
    forage_lon = risk_info.get('forage_centre_lon', CAMPBELL_LON)

    folium.CircleMarker(
        location=[forage_lat, forage_lon],
        radius=6,
        color=track_colour,
        fill=True,
        fill_color=track_colour,
        fill_opacity=0.9,
        popup=folium.Popup(popup_html, max_width=240),
        tooltip=f"Bird {bird_id} — {risk_label} — click for details"
    ).add_to(centres_group)

    lons = bird_data['location-long'].values
    lats = bird_data['location-lat'].values
    lons_norm = [normalize_lon(lon) for lon in lons]

    coords = list(zip(lats.tolist(), lons_norm))
    folium.PolyLine(
        locations=coords,
        color=track_colour,
        weight=2.5,
        opacity=0.9
    ).add_to(bird_group)

    bird_group.add_to(m)

print(f"  ✓ Added {len(bird_ids)} bird track layers")


# ============================================================================
# PART 6: FORAGING HOTSPOT HEATMAP
# ============================================================================

print("Adding foraging heatmap...")

# What we're achieving: a smooth density layer showing where birds concentrate
# when actually feeding — more visually informative than individual track lines.
#
# The challenge: HeatMap expects [lat, lon, weight] tuples. We use the
# full (not subsampled) dataset here because heatmaps aggregate by nature —
# more points = denser heat, which is exactly what we want for density.
#
# We weight each point by its KDE density value would require joining back
# to the KDE grid; instead we filter to foraging state only and let the
# heatmap show raw point density, which is equivalent for our purposes.

foraging_pts = [
    [row['location-lat'], normalize_lon(row['location-long'])]
    for _, row in df[df['behaviour'] == 1].iterrows()
]

heatmap_group = folium.FeatureGroup(name='Foraging hotspots (heatmap)', show=True)
HeatMap(
    foraging_pts,
    radius=12,
    blur=18,
    min_opacity=0.25,
    gradient={0.2: '#4575b4', 0.5: '#ffffbf', 1.0: '#d73027'}
).add_to(heatmap_group)
heatmap_group.add_to(m)

print(f"  ✓ Heatmap: {len(foraging_pts):,} foraging points")


# ============================================================================
# PART 7: CCAMLR FISHING EFFORT
# ============================================================================

print("Adding CCAMLR fishing effort...")

# What we're achieving: representing 58 million hooks across 14 CCAMLR areas
# on the map. The challenge: Area.csv has no coordinates — just area codes.
# We approximate each area's location using its asd_code as a lookup into
# known CCAMLR statistical area centroids. This is a simplification flagged
# in the map legend.
#
# Known centroids for CCAMLR subareas relevant to the Southern Ocean
# (lat, lon approximate centres):

CCAMLR_CENTROIDS = {
    '481':  (-57.0,  -27.0),   # 48.1 South Orkney
    '482':  (-54.0,  -38.0),   # 48.2 South Georgia general
    '483':  (-54.5,  -36.5),   # 48.3 South Georgia EEZ
    '484':  (-58.0,  -50.0),   # 48.4 South Sandwich
    '485':  (-60.0,  -65.0),   # 48.5 Western Antarctic Peninsula
    '486':  (-57.0,  -24.0),   # 48.6
    '581':  (-58.0,   20.0),   # 58.1 Crozet
    '5841': (-53.0,   72.0),   # 58.4.1 Kerguelen
    '5842': (-53.0,   73.5),   # 58.4.2 Heard
    '5851': (-60.0,  165.0),   # 58.5.1 Pacific sector south
    '5852': (-52.0,  165.0),   # 58.5.2 Pacific sector north
    '881':  (-72.0, -178.0),   # 88.1 West Ross Sea
    '882':  (-72.0, -140.0),   # 88.2 East Ross Sea
    '586':  (-55.0,   25.0),   # 58.6
}

effort_group = folium.FeatureGroup(
    name='CCAMLR longline effort 2013 (approx. centroids)', show=True
)

# Scale circle size by hook count — use square root to prevent
# the largest areas from completely dominating the visual
effort_by_area = effort_2013.groupby('asd_code')['hook_count'].sum()
max_hooks = effort_by_area.max()

areas_mapped = 0
for asd_code, total_hooks in effort_by_area.items():
    centroid = CCAMLR_CENTROIDS.get(str(asd_code))
    if centroid is None:
        continue  # skip areas without known centroids

    lat, lon = centroid
    lon_norm = normalize_lon(lon)
    radius = 5 + 30 * np.sqrt(total_hooks / max_hooks)  # 5–35px range

    popup_text = (
        f"<b>CCAMLR Area {asd_code}</b><br>"
        f"Longline hooks (2013): {total_hooks:,.0f}<br>"
        f"<i>Note: position is approximate area centroid</i>"
    )

    folium.CircleMarker(
        location=[lat, lon_norm],
        radius=radius,
        color='#D9947F',
        fill=True,
        fill_color='#D9947F',
        fill_opacity=0.4,
        weight=1.5,
        popup=folium.Popup(popup_text, max_width=220),
        tooltip=f"Area {asd_code}: {total_hooks:,.0f} hooks"
    ).add_to(effort_group)
    areas_mapped += 1

effort_group.add_to(m)
print(f"  ✓ Fishing effort: {areas_mapped} CCAMLR areas mapped")


# ============================================================================
# PART 8: CCAMLR BOUNDARY LINE
# ============================================================================

# Approximate CCAMLR Convention Area boundary at 60°S across the Pacific sector
ccamlr_group = folium.FeatureGroup(
    name='CCAMLR boundary (60°S, approximate)', show=True
)
folium.PolyLine(
    locations=[[-60, lon] for lon in range(-11, 350, 5)],
    color='#B794D9',
    weight=2,
    dash_array='8 4',
    opacity=0.7,
    tooltip='Approximate CCAMLR Convention Area boundary (60°S)'
).add_to(ccamlr_group)
ccamlr_group.add_to(m)


# ============================================================================
# PART 9: RISK CLUSTER LEGEND AND LAYER CONTROL
# ============================================================================

# Add a custom HTML legend explaining the colour coding
legend_html = """
<div style="
    position: fixed;
    bottom: 40px; left: 12px; z-index: 1000;
    background: white; border-radius: 8px;
    padding: 12px 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    font-family: sans-serif; font-size: 12px; line-height: 1.8;
    min-width: 190px;
">
    <b style="font-size:13px">Bird risk profile</b><br>
    <span style="color:#7FAD87">●</span> Low risk (11 birds)<br>
    <span style="color:#9BC4CB">●</span> Medium risk (10 birds)<br>
    <span style="color:#D9947F">●</span> High risk (3 birds)<br>
    <hr style="margin:6px 0">
    <b style="font-size:13px">Foraging heatmap</b><br>
    <span style="color:#4575b4">■</span> Low density<br>
    <span style="color:#ffffbf">■</span> Medium density<br>
    <span style="color:#d73027">■</span> High density<br>
    <hr style="margin:6px 0">
    <span style="color:#D9947F">●</span> CCAMLR longline effort<br>
    &nbsp;&nbsp;(size ∝ √hook count)<br>
    <span style="color:#B794D9">- -</span> CCAMLR boundary (~60°S)<br>
    <hr style="margin:6px 0">
    <i style="color:#888; font-size:10px">
    Bird tracks: toggle in layer control<br>
    Click foraging centre ● for stats
    </i>
</div>
"""

m.get_root().html.add_child(folium.Element(legend_html))

# Layer control — lets user toggle each bird track and data layer on/off
folium.LayerControl(collapsed=False).add_to(m)


# ============================================================================
# PART 10: SAVE
# ============================================================================

out_path = 'outputs/maps/albatross_interactive_map.html'
m.save(out_path)

import os
file_size_mb = os.path.getsize(out_path) / 1e6
print(f"\n  ✓ Saved: {out_path} ({file_size_mb:.1f} MB)")


# ============================================================================
# PART 11: SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("PHASE 4 SUMMARY")
print("=" * 70)
print(f"""
  Map layers:
    Individual bird tracks:    {len(bird_ids)} (togglable, off by default)
    Foraging heatmap:          {len(foraging_pts):,} points
    CCAMLR fishing effort:     {areas_mapped} areas
    CCAMLR boundary:           60°S approximate line

  Open in browser:
    open outputs/maps/albatross_interactive_map.html
""")
print("=" * 70)
print("PHASE 4 COMPLETE")
print("=" * 70 + "\n")