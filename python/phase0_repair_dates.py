"""
Phase 0: repair bird 90494's timestamps.

Rule, for bird 90494 and event-id 2172899175 to 2172902497 inclusive: month becomes 11
and day becomes the stored month; time of day is unchanged. 3,056 rows change value.
The 267 rows stored as 2013-11-11 swap to themselves and stay unchanged. No other row
changes. The source file is never modified.

Input:  data/raw/albatross_tracks.csv
Output: data/raw/albatross_tracks_corrected.csv, with timestamp_original and
        timestamp_repaired added. An existing output must match the expected checksum.
"""
import csv
import hashlib
import sys
from pathlib import Path

SRC = Path('data/raw/albatross_tracks.csv')
DST = Path('data/raw/albatross_tracks_corrected.csv')
BIRD, EID_FIRST, EID_LAST = '90494', 2172899175, 2172902497
EXPECTED_SHA256 = '0c0fe63b54d9aad176823f24c769c3fb4db2d286625cd0ef26f217ab9bbb56e4'

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
sha = hashlib.sha256(data).hexdigest()
if sha != EXPECTED_SHA256:
    sys.exit(f'repair output checksum {sha} does not match the expected {EXPECTED_SHA256}')
if DST.exists():
    if hashlib.sha256(DST.read_bytes()).hexdigest() != EXPECTED_SHA256:
        sys.exit(f'{DST} exists and does not match the expected checksum; not overwriting')
    print(f'{DST} already present and verified')
else:
    DST.write_bytes(data)
    print(f'Wrote {DST}')
print(f'rows {len(rows):,}; in range {in_range:,}; changed {changed:,}; sha256 {sha}')
