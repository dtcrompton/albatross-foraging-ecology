"""Write data/raw/albatross_tracks_corrected.csv from data/raw/albatross_tracks.csv.

Rule (bird 90494 only, event-id 2172899175..2172902497 inclusive): month becomes 11
and day becomes the stored month; time of day is unchanged. Every other byte of each
row is preserved. Two columns are appended: timestamp_original (stored value) and
timestamp_repaired (true only where the value changed). Refuses to overwrite.

Run from the repository root:  python3 rerun_v2/repair_90494_timestamps.py
"""
import csv
import hashlib
import sys
from pathlib import Path

SRC = Path('data/raw/albatross_tracks.csv')
DST = Path('data/raw/albatross_tracks_corrected.csv')
BIRD, EID_FIRST, EID_LAST = '90494', 2172899175, 2172902497

if DST.exists():
    sys.exit(f'{DST} already exists; refusing to overwrite')

raw = SRC.read_bytes().decode('utf-8')
lines = raw.split('\r\n')
assert lines[-1] == '', 'expected a trailing CRLF'
header, rows = lines[0], lines[1:-1]
out = [header + ',timestamp_original,timestamp_repaired']
in_range = changed = 0
for row in rows:
    # event-id,visible,timestamp are the first three, unquoted, fields
    eid, visible, ts, rest = row.split(',', 3)
    bird = next(csv.reader([row]))[8]  # individual-local-identifier (study-name holds a comma)
    new_ts, flag = ts, 'false'
    if bird == BIRD and EID_FIRST <= int(eid) <= EID_LAST:
        in_range += 1
        year, month, day = ts[:4], ts[5:7], ts[8:10]
        assert day == '11' and ts[17:19] == '00', row
        new_ts = f'{year}-11-{month}{ts[10:]}'
        if new_ts != ts:
            changed += 1
            flag = 'true'
    out.append(f'{eid},{visible},{new_ts},{rest},{ts},{flag}')
assert in_range == 3323 and changed == 3056, (in_range, changed)

data = ('\r\n'.join(out) + '\r\n').encode('utf-8')
DST.write_bytes(data)
print('rows', len(rows), 'in range', in_range, 'changed', changed)
print('sha256', hashlib.sha256(data).hexdigest())
