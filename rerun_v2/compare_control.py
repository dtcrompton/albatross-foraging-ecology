"""Compare data/processed_v2/control/ with data/processed/ and write
outputs_v2/control_comparison.md. Run from the repository root."""
import importlib.metadata as md
import sys
from pathlib import Path
import numpy as np
import pandas as pd

OLD, NEW = Path('data/processed'), Path('data/processed_v2/control')
TOL = 1e-6
lines = ['# Control run versus existing data/processed/', '',
         'Control: copied pipeline, original unrepaired raw file, old colony point.', '',
         'Environment: Python ' + sys.version.split()[0] + ', ' +
         ', '.join(f'{p} {md.version(p)}' for p in ['pandas', 'numpy', 'scipy', 'scikit-learn', 'hmmlearn', 'xarray']),
         '', f'Numeric tolerance: absolute difference up to {TOL}.', '',
         '| File | Rows old / control | Same columns | Exact text match | Numeric columns over tolerance | Other columns differing |',
         '|---|---|---|---|---|---|']
all_ok = True
detail = []
for name in ['tracks_with_metrics.csv', 'tracks_with_behaviour.csv', 'tracks_with_env.csv',
             'bird_profiles.csv', 'bird_risk_profiles.csv', 'trip_statistics.csv', 'foraging_kde_grid.csv']:
    a, b = pd.read_csv(OLD / name, low_memory=False), pd.read_csv(NEW / name, low_memory=False)
    exact = (OLD / name).read_bytes() == (NEW / name).read_bytes()
    same_cols = a.columns.tolist() == b.columns.tolist()
    over, other = [], []
    if same_cols and len(a) == len(b):
        for c in a.columns:
            if (pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c])
                    and not pd.api.types.is_bool_dtype(a[c]) and not pd.api.types.is_bool_dtype(b[c])):
                d = (a[c] - b[c]).abs()
                bad = (d > TOL) | (a[c].isna() != b[c].isna())
                if bad.any():
                    over.append(c)
                    detail.append(f'- {name} `{c}`: {int(bad.sum())} rows differ, largest difference {d.max():.6g}')
            elif not (a[c].astype(str) == b[c].astype(str)).all():
                other.append(c)
                detail.append(f'- {name} `{c}`: {int((a[c].astype(str) != b[c].astype(str)).sum())} rows differ')
    ok = same_cols and len(a) == len(b) and not over and not other
    all_ok &= ok
    lines.append(f"| {name} | {len(a):,} / {len(b):,} | {same_cols} | {exact} | {', '.join(over) or 'none'} | {', '.join(other) or 'none'} |")

a, b = (pd.read_csv(p / 'tracks_with_behaviour.csv', low_memory=False) for p in (OLD, NEW))
m = a[['event-id', 'behaviour', 'hmm_state_raw']].merge(b[['event-id', 'behaviour', 'hmm_state_raw']], on='event-id', suffixes=('_old', '_ctl'))
lines += ['', '## State labels', '',
          f"Fixes joined on event-id: {len(m):,}. Behaviour label differs on {int((m.behaviour_old != m.behaviour_ctl).sum()):,}. "
          f"Raw HMM state number differs on {int((m.hmm_state_raw_old != m.hmm_state_raw_ctl).sum()):,}.", '',
          '## Differences', ''] + (detail or ['None over tolerance.']) + ['', f'## Result: {"REPRODUCED within tolerance" if all_ok else "NOT REPRODUCED within tolerance"}']
Path('outputs_v2/control_comparison.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('\n'.join(lines))
