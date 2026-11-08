"""Generate the per-run script copies by exact-string replacement of paths
(and, for v3 only, the colony coordinates), and record each diff.

Usage, from the repository root:  python3 rerun_v2/make_copies.py control|v2|v3
"""
import difflib
import sys
from pathlib import Path

RUN = sys.argv[1]
SCRIPTS = ['explore_data.py', 'phase1_movement_metrics.py',
           'phase2a_behaviour_classification.py', 'phase2a_figures.py',
           'phase2b_environmental_drivers.py', 'phase3_conservation_risk.py',
           'phase4_interactive_map.py']
PROC = {'control': 'data/processed_v2/control/', 'v2': 'data/processed_v2/',
        'v3': 'data/processed_v3/'}[RUN]
OUT = {'control': 'outputs_v2/control/', 'v2': 'outputs_v2/', 'v3': 'outputs_v2/v3/'}[RUN]
RAW = 'data/raw/albatross_tracks.csv' if RUN == 'control' else 'data/raw/albatross_tracks_corrected.csv'

COORDS = {
    'explore_data.py': [('campbell_lat = -52.55', 'campbell_lat = -52.474'),
                        ('campbell_lon = 169.15', 'campbell_lon = 169.224')],
    'phase1_movement_metrics.py': [('CAMPBELL_LON = 169.15', 'CAMPBELL_LON = 169.224'),
                                   ('CAMPBELL_LAT = -52.55', 'CAMPBELL_LAT = -52.474')],
    'phase2a_behaviour_classification.py': [('ax1.scatter(169.15, -52.55,', 'ax1.scatter(169.224, -52.474,')],
    'phase2a_figures.py': [('CAMPBELL_LON = 169.15', 'CAMPBELL_LON = 169.224'),
                           ('CAMPBELL_LAT = -52.55', 'CAMPBELL_LAT = -52.474')],
    'phase3_conservation_risk.py': [('ax1.scatter(169.15, -52.55,', 'ax1.scatter(169.224, -52.474,')],
    'phase4_interactive_map.py': [('CAMPBELL_LAT =  -52.55', 'CAMPBELL_LAT =  -52.474'),
                                  ('CAMPBELL_LON =  169.15', 'CAMPBELL_LON =  169.224')],
}

dst = Path('rerun_v2') / RUN
dst.mkdir(parents=True, exist_ok=True)
Path('rerun_v2/diffs').mkdir(exist_ok=True)
diff_all = []
for name in SCRIPTS:
    src = Path('python') / name
    text = src.read_text(encoding='utf-8')
    new = (text.replace('data/raw/Grey-headed albatross, New Zealand (data from Torres et al. 2017).csv', RAW)
               .replace('data/raw/albatross_tracks.csv', RAW)
               .replace('data/processed/', PROC)
               .replace('outputs/figures/', OUT + 'figures/')
               .replace('outputs/maps', OUT + 'maps'))
    if RUN == 'v3':
        for old, rep in COORDS.get(name, []):
            assert new.count(old) == 1, (name, old)
            new = new.replace(old, rep)
    (dst / name).write_text(new, encoding='utf-8')
    diff_all += difflib.unified_diff(text.splitlines(), new.splitlines(),
                                     f'python/{name}', f'rerun_v2/{RUN}/{name}', lineterm='', n=0)
Path(f'rerun_v2/diffs/{RUN}.diff').write_text('\n'.join(diff_all) + '\n', encoding='utf-8')
print(RUN, 'changed lines:', sum(1 for l in diff_all if l[:1] in '+-' and l[:3] not in ('+++', '---')))
