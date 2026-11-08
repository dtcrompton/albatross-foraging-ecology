"""Remove timestamp_original and timestamp_repaired from finished track CSVs so they
have the same columns as data/processed/.  Usage: strip_audit_columns.py <processed dir>"""
import sys
from pathlib import Path
import pandas as pd

d = Path(sys.argv[1])
for name in ['tracks_with_metrics.csv', 'tracks_with_behaviour.csv', 'tracks_with_env.csv']:
    df = pd.read_csv(d / name, dtype=str, keep_default_na=False)
    df = df.drop(columns=['timestamp_original', 'timestamp_repaired'])
    original = pd.read_csv(Path('data/processed') / name, nrows=0).columns.tolist()
    assert df.columns.tolist() == original, name
    df.to_csv(d / name, index=False)
    print('stripped', d / name)
