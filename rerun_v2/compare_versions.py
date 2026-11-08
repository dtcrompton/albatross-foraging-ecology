"""Three-way comparison: old (data/processed), v2 (dates fixed, old colony point),
v3 (dates fixed, deployment-site colony point). Writes outputs_v2/comparison_report.md
and outputs_v2/per_bird_comparison.csv. Run from the repository root."""
import re
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

V = {'old': Path('data/processed'), 'v2': Path('data/processed_v2'), 'v3': Path('data/processed_v3')}
LOG = {'old': 'control', 'v2': 'v2', 'v3': 'v3'}
ID = 'individual-local-identifier'
FEATS = ['sst', 'chla', 'location-lat', 'location-long', 'dist_from_campbell']
STATE = {0: 'Resting', 1: 'Foraging', 2: 'Transiting'}
CCAMLR = Path('data/raw/ccamlr/CCAMLR_statistical bulletin_V37')


def rf():
    return RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42,
                                  n_jobs=-1, class_weight='balanced')


def load(v):
    t = pd.read_csv(V[v] / 'tracks_with_env.csv', parse_dates=['timestamp'],
                    dtype={ID: str}, low_memory=False)
    t = t.sort_values([ID, 'timestamp']).reset_index(drop=True)
    p = pd.read_csv(V[v] / 'bird_risk_profiles.csv', dtype={'bird_id': str}).set_index('bird_id')
    tr = pd.read_csv(V[v] / 'trip_statistics.csv', dtype={'bird_id': str})
    return t, p, tr


def per_bird(t, p):
    rows = {}
    for b, x in t.groupby(ID):
        f = (x.behaviour == 1).values
        starts = f & ~np.r_[False, f[:-1]]
        rid = np.cumsum(starts)[f]
        ts = x.timestamp.values[f]
        hrs = pd.Series(ts).groupby(rid).agg(lambda s: (s.iloc[-1] - s.iloc[0]).total_seconds() / 3600).clip(lower=.1)
        n = int(starts.sum())
        away = (x.dist_from_campbell > 50).values
        runs = np.flatnonzero(away & ~np.r_[False, away[:-1]])
        ends = np.flatnonzero(away & ~np.r_[away[1:], False])
        days = (x.timestamp.values[ends] - x.timestamp.values[runs]) / np.timedelta64(1, 'D')
        rows[b] = dict(
            fixes=len(x), duration_days=(x.timestamp.iloc[-1] - x.timestamp.iloc[0]).total_seconds() / 86400,
            bouts=n, bout_hours_total=hrs.sum(), prop_foraging=(x.behaviour == 1).mean(),
            max_dist_km=x.dist_from_campbell.max(), total_dist_km=x.step_length_km.sum(),
            forage_centre_lat=p.loc[b, 'forage_centre_lat'], risk_label=p.loc[b, 'risk_label'],
            rings=min(40, max(3, n // 10)), away_trips=len(runs), away_trips_1d=int((days >= 1).sum()),
            closest_km=x.dist_from_campbell.min(), first_km=x.dist_from_campbell.iloc[0],
            last_km=x.dist_from_campbell.iloc[-1])
    return pd.DataFrame(rows).T


def synchrony(t):
    e = pd.read_csv(CCAMLR / 'Effort.csv', low_memory=False)
    for c in ['hook_count', 'month', 'year']:
        e[c] = pd.to_numeric(e[c], errors='coerce').fillna(0)
    codes = [c for c in ['LLS', 'LL', 'LP', 'DLL', 'SSL', 'LHP', 'LHM'] if c in e.gear_type_code.values]
    h = e[(e.year == 2013) & e.gear_type_code.isin(codes)].groupby('month').hook_count.sum().reindex(range(1, 13), fill_value=0)
    f = t[t.behaviour == 1]
    m = f.groupby(f.timestamp.dt.month).size().reindex(range(1, 13), fill_value=0)
    fn, en = m / m.max(), h / max(h.max(), 1)
    return (fn * en).sum() / fn.sum(), m


def forest(t):
    d = t.dropna(subset=['sst', 'chla']).copy()
    d['y'] = (d.behaviour == 1).astype(int)
    a, b, c, e = train_test_split(d[FEATS], d.y, test_size=.3, random_state=42, stratify=d.y)
    r = rf().fit(a, c)
    res = dict(test_acc=r.score(b, e), imp=dict(zip(FEATS, r.feature_importances_)), n=len(d),
               majority=max(d.y.mean(), 1 - d.y.mean()))
    correct = per = 0
    accs = {}
    for bird, g in d.groupby(ID):
        tr = d[d[ID] != bird]
        p = rf().fit(tr[FEATS], tr.y).predict(g[FEATS])
        accs[bird] = (p == g.y.values).mean()
        correct += (p == g.y.values).sum()
    res['lobo_pooled'] = correct / len(d)
    res['lobo_mean'] = np.mean(list(accs.values()))
    res['lobo_min'], res['lobo_max'] = min(accs.values()), max(accs.values())
    return res


def stats(t, p, tr):
    f = t[t.behaviour == 1]
    lat = f['location-lat']
    s = {'fixes': len(t), 'birds': t[ID].nunique()}
    for k, st in STATE.items():
        q = t[t.behaviour == k]
        s[f'share_{st}'] = len(q) / len(t) * 100
        s[f'turn_{st}'] = np.degrees(q.abs_turning_angle.mean())
        s[f'step_{st}'] = q.step_length_km.mean()
    s.update(maxd_min=p.max_dist_km.min(), maxd_max=p.max_dist_km.max(), multiple=p.max_dist_km.max() / p.max_dist_km.min(),
             pf_min=p.prop_foraging.min() * 100, pf_max=p.prop_foraging.max() * 100,
             tot_min=p.total_dist_km.min(), tot_max=p.total_dist_km.max(),
             trip_n=len(tr), trip_mean=tr.duration_days.mean(), trip_max=tr.duration_days.max(),
             z_s60=(lat < -60).mean() * 100, z_mid=((lat >= -60) & (lat < -48.8)).mean() * 100,
             z_n488=(lat >= -48.8).mean() * 100, z_n60=(lat >= -60).mean() * 100,
             closest_min=t.groupby(ID).dist_from_campbell.min().min(), closest_max=t.groupby(ID).dist_from_campbell.min().max(),
             sst_f=f.sst.mean(), sst_nf=t[t.behaviour != 1].sst.mean(), chla_cov=t.chla.notna().mean() * 100)
    s['sync'], s['_months'] = synchrony(t)
    s['high'] = ', '.join(sorted(p.index[p.risk_label == 'High risk'], key=int))
    vc = p.risk_label.value_counts()
    s['sizes'] = f"{vc.get('Low risk', 0)} / {vc.get('Medium risk', 0)} / {vc.get('High risk', 0)}"
    r = forest(t)
    s['rf'] = r['test_acc'] * 100
    s['rf_lobo'] = r['lobo_pooled'] * 100
    s['rf_lobo_mean'] = r['lobo_mean'] * 100
    s['rf_lobo_rng'] = f"{r['lobo_min'] * 100:.1f} to {r['lobo_max'] * 100:.1f}"
    s['rf_major'] = r['majority'] * 100
    s['rf_n'] = r['n']
    for k, v in r['imp'].items():
        s['imp_' + k] = v
    return s


def table(head, rows):
    return ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)] + ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]


data = {v: load(v) for v in V}
pb = {v: per_bird(data[v][0], data[v][1]) for v in V}
print('forests take a few minutes')
st = {v: stats(*data[v]) for v in V}

# Cross-check against what the pipeline itself logged
for v in V:
    log2b = Path(f'rerun_v2/logs/{LOG[v]}_phase2b_environmental_drivers.log').read_text()
    log3 = Path(f'rerun_v2/logs/{LOG[v]}_phase3_conservation_risk.log').read_text()
    assert abs(float(re.search(r'Test accuracy:\s+([\d.]+)', log2b).group(1)) - st[v]['rf'] / 100) < .0006, v
    assert abs(float(re.search(r'synchrony index: ([\d.]+)', log3).group(1)) - st[v]['sync']) < .0006, v
    for b, row in pb[v].iterrows():
        assert abs(row.total_dist_km - data[v][1].loc[b, 'total_dist_km']) < .06 and abs(row.max_dist_km - data[v][1].loc[b, 'max_dist_km']) < .06, (v, b)

birds = sorted(pb['old'].index, key=int)
METRICS = [('fixes', 'Fixes', 0), ('duration_days', 'Duration (days)', 2), ('bouts', 'Foraging bouts', 0),
           ('prop_foraging', 'Proportion foraging', 3), ('max_dist_km', 'Max distance (km)', 1),
           ('total_dist_km', 'Total distance (km)', 1), ('forage_centre_lat', 'Forage centre latitude', 4),
           ('risk_label', 'Risk cluster', None), ('rings', 'Ring count', 0)]
wide = pd.DataFrame(index=birds)
for k in pb['old'].columns:
    for v in V:
        wide[f'{k}_{v}'] = pb[v][k]
wide.index.name = 'bird'
wide.to_csv('outputs_v2/per_bird_comparison.csv')


def fm(x, dp):
    return x if dp is None else f'{float(x):,.{dp}f}'


L = ['# Old versus v2 versus v3', '',
     '- **old:** existing `data/processed/` (original data, colony point 169.15E, 52.55S).',
     '- **v2:** bird 90494 dates repaired, colony point 169.15E, 52.55S (`data/processed_v2/`).',
     '- **v3:** bird 90494 dates repaired, colony point 169.224E, 52.474S (`data/processed_v3/`).', '',
     'Control: the copied pipeline on the original raw file reproduced all seven `data/processed/` files byte for byte (`outputs_v2/control_comparison.md`), so no comparison below carries a reproducibility flag.', '',
     'Sources for every number: `outputs_v2/per_bird_comparison.csv` and the run logs in `rerun_v2/logs/`.', '',
     'Definitions: a foraging bout is a contiguous run of behaviour 1 (duration is last minus first timestamp, minimum 0.1 h). Ring count is `min(40, max(3, n_bouts // 10))`. An away trip is a run of fixes over 50 km from the colony point.', '',
     '## 1. Per bird: values', '']
for key, name, dp in METRICS:
    L += [f'### {name}', ''] + table(['Bird', 'old', 'v2', 'v3'], [[b] + [fm(pb[v].loc[b, key], dp) for v in V] for b in birds]) + ['']

for sec, a, c, title in [('1b', 'old', 'v2', 'old to v2 (date repair)'), ('1c', 'v2', 'v3', 'v2 to v3 (colony point)')]:
    L += [f'## {sec}. Per bird differences: {title}', '']
    rows = []
    for b in birds:
        r = [b]
        for key, name, dp in METRICS:
            if dp is None:
                r.append('same' if pb[a].loc[b, key] == pb[c].loc[b, key] else f'{pb[a].loc[b, key]} to {pb[c].loc[b, key]}')
            elif key == 'prop_foraging':
                r.append(f'{(pb[c].loc[b, key] - pb[a].loc[b, key]) * 100:+.2f} pp')
            else:
                r.append(f'{float(pb[c].loc[b, key]) - float(pb[a].loc[b, key]):+,.{dp}f}')
        rows.append(r)
    L += table(['Bird'] + [m[1] for m in METRICS], rows) + ['']

L += ['## 2. State stability', '', 'Percentage of each bird\'s fixes whose HMM state changed, joined on event-id.', '']
rows, tot = [], {}
for b in birds:
    r = [b]
    for a, c in [('old', 'v2'), ('v2', 'v3')]:
        m = data[a][0].loc[data[a][0][ID] == b, ['event-id', 'behaviour']].merge(data[c][0].loc[data[c][0][ID] == b, ['event-id', 'behaviour']], on='event-id')
        n = int((m.behaviour_x != m.behaviour_y).sum())
        tot[(a, c)] = tot.get((a, c), 0) + n
        r += [n, f'{n / len(m) * 100:.3f}%']
    rows.append(r)
L += table(['Bird', 'old to v2 fixes', 'old to v2 %', 'v2 to v3 fixes', 'v2 to v3 %'], rows)
L += ['', f"All birds: old to v2 {tot[('old', 'v2')]:,} fixes; v2 to v3 {tot[('v2', 'v3')]:,} fixes.", '', '### HMM state parameters', '']
rows = [[STATE[k]] + [f"{st[v][f'step_{STATE[k]}']:.4f}" for v in V] + [f"{st[v][f'turn_{STATE[k]}']:.3f}" for v in V] for k in STATE]
L += table(['State', 'Step km old', 'Step km v2', 'Step km v3', 'Turn deg old', 'Turn deg v2', 'Turn deg v3'], rows) + ['']

SPEC = [('Total fixes', '93,474', 'fixes', 0, 0), ('Birds', '24', 'birds', 0, 0),
        ('Foraging share of fixes (%)', '41.1', 'share_Foraging', 1, 2), ('Resting share of fixes (%)', '26.9', 'share_Resting', 1, 2),
        ('Transiting share of fixes (%)', '32.0', 'share_Transiting', 1, 2),
        ('Mean turning, foraging (deg)', '62.2', 'turn_Foraging', 1, 2), ('Mean turning, transiting (deg)', '9.9', 'turn_Transiting', 1, 2),
        ('Mean turning, resting (deg)', '6.9', 'turn_Resting', 1, 2),
        ('Mean step, resting (km)', '0.14', 'step_Resting', 2, 3), ('Mean step, foraging (km)', '1.44', 'step_Foraging', 2, 3),
        ('Mean step, transiting (km)', '4.04', 'step_Transiting', 2, 3),
        ('Max foraging distance, lowest bird (km)', '745', 'maxd_min', 0, 1), ('Max foraging distance, highest bird (km)', '2,715', 'maxd_max', 0, 1),
        ('Range multiple', '3.5', 'multiple', 1, 3),
        ('Proportion foraging, lowest bird (%)', '33', 'pf_min', 0, 1), ('Proportion foraging, highest bird (%)', '59', 'pf_max', 0, 1),
        ('Total distance, lowest bird (km)', '3,465', 'tot_min', 0, 1), ('Total distance, highest bird (km)', '12,285', 'tot_max', 0, 1),
        ('Trips of 1 day or more, trip_statistics rows', 'not published', 'trip_n', 0, 0),
        ('Mean trip duration (days)', '25', 'trip_mean', 0, 2), ('Longest trip duration (days)', '274', 'trip_max', 0, 2),
        ('Zone: south of 60S (%)', '0.9', 'z_s60', 1, 3), ('Zone: 60S to 48.8S (%)', '97.5', 'z_mid', 1, 3),
        ('Zone: north of 48.8S (%)', 'not published', 'z_n488', 1, 3), ('Zone: north of 60S (%)', '99.1', 'z_n60', 1, 3),
        ('Temporal synchrony index', '0.31', 'sync', 2, 3), ('High-risk birds', '2, 89518, 90493', 'high', None, None),
        ('Cluster sizes, low / medium / high', '3 high', 'sizes', None, None),
        ('Random Forest test accuracy (%)', '64.9', 'rf', 1, 2), ('Importance: distance from colony', '0.31', 'imp_dist_from_campbell', 2, 3),
        ('Importance: latitude', '0.24', 'imp_location-lat', 2, 3), ('Importance: longitude', '0.19', 'imp_location-long', 2, 3),
        ('Importance: SST', '0.15', 'imp_sst', 2, 3), ('Importance: chlorophyll-a', '0.11', 'imp_chla', 2, 3),
        ('RF accuracy, whole bird held out, pooled (%)', 'not published', 'rf_lobo', 1, 2),
        ('RF accuracy, whole bird held out, mean of birds (%)', 'not published', 'rf_lobo_mean', 1, 2),
        ('RF accuracy, whole bird held out, range across birds (%)', 'not published', 'rf_lobo_rng', None, None),
        ('Largest-class share of modelled fixes (%)', 'not published', 'rf_major', 1, 2),
        ('Closest approach, lowest bird (km)', '7', 'closest_min', 0, 2), ('Closest approach, highest bird (km)', '14', 'closest_max', 0, 2),
        ('Mean SST, foraging (C)', '6.31', 'sst_f', 2, 3), ('Mean SST, not foraging (C)', '6.44', 'sst_nf', 2, 3)]


def pub(v, key, dp):
    return st[v][key] if dp is None else round(float(st[v][key]) + 0.0, dp)


rows, only_colony, only_date, both, same = [], [], [], [], []
for name, published, key, pdp, ddp in SPEC:
    a, b, c = (pub(v, key, pdp) for v in V)
    d1, d2 = a != b, b != c
    rows.append([name, published] + [fm(st[v][key], ddp) for v in V] + ['changes' if d1 else 'same', 'changes' if d2 else 'same'])
    (both if d1 and d2 else only_date if d1 else only_colony if d2 else same).append(name)
L += ['## 3. Published statistics', '',
      'Values show extra decimal places. "Changes" is judged at the precision the page publishes. Whole-bird hold-out uses the same forest settings, leaving out each of the 24 birds once. The "old" forest uses the existing `tracks_with_env.csv`.', '']
L += table(['Statistic', 'Published', 'old', 'v2', 'v3', 'old to v2', 'v2 to v3'], rows) + ['']

L += ['### Foraging fixes by month', ''] + table(['Month', 'old', 'v2', 'v3'], [[m] + [int(st[v]['_months'][m]) for v in V] for m in range(1, 13)]) + ['']

L += ['## 3b. Statistics that change only because of the colony point', '',
      'Same from old to v2, different from v2 to v3, at published precision:', ''] + ([f'- {n}' for n in only_colony] or ['- None.'])
L += ['', 'Change only because of the date repair:', ''] + ([f'- {n}' for n in only_date] or ['- None.'])
L += ['', 'Change at both steps:', ''] + ([f'- {n}' for n in both] or ['- None.'])
L += ['', 'Unchanged at both steps:', ''] + ([f'- {n}' for n in same] or ['- None.']) + ['']

L += ['## 4. Flags', '', 'Ring count change of 1 or more, proportion foraging change over 1 percentage point, or cluster change.', '']
rows = []
for a, c in [('old', 'v2'), ('v2', 'v3')]:
    for b in birds:
        x, y = pb[a].loc[b], pb[c].loc[b]
        if abs(y.rings - x.rings) >= 1:
            rows.append([f'{a} to {c}', b, 'ring count', x.rings, y.rings])
        if abs(y.prop_foraging - x.prop_foraging) * 100 > 1:
            rows.append([f'{a} to {c}', b, 'proportion foraging', f'{x.prop_foraging:.3f}', f'{y.prop_foraging:.3f}'])
        if x.risk_label != y.risk_label:
            rows.append([f'{a} to {c}', b, 'cluster', x.risk_label, y.risk_label])
L += (table(['Step', 'Bird', 'Flag', 'From', 'To'], rows) if rows else ['None.']) + ['']

s = st['v3']
L += ['## 5. Numbers for the web pages', '', 'All from v3 (dates repaired, colony point 169.224E, 52.474S).', '',
      f"- Total fixes: {s['fixes']:,}",
      f"- Birds: {s['birds']}",
      f"- Foraging share of fixes: {s['share_Foraging']:.1f}%",
      f"- Resting share of fixes: {s['share_Resting']:.1f}%",
      f"- Transiting share of fixes: {s['share_Transiting']:.1f}%",
      f"- Mean turning angle: foraging {s['turn_Foraging']:.1f} degrees, transiting {s['turn_Transiting']:.1f} degrees, resting {s['turn_Resting']:.1f} degrees",
      f"- Mean step length: resting {s['step_Resting']:.2f} km, foraging {s['step_Foraging']:.2f} km, transiting {s['step_Transiting']:.2f} km",
      f"- Maximum foraging distance range: {s['maxd_min']:,.0f} to {s['maxd_max']:,.0f} km",
      f"- Range multiple: {s['multiple']:.1f}",
      f"- Proportion foraging range: {s['pf_min']:.0f}% to {s['pf_max']:.0f}%",
      f"- Total distance range: {s['tot_min']:,.0f} to {s['tot_max']:,.0f} km",
      f"- Mean trip duration: {s['trip_mean']:.1f} days",
      f"- Longest trip duration: {s['trip_max']:.1f} days",
      f"- Date range: {data['v3'][0].timestamp.min():%d %b %Y} to {data['v3'][0].timestamp.max():%d %b %Y}",
      f"- Latitude zones: south of 60S {s['z_s60']:.1f}%, 60S to 48.8S {s['z_mid']:.1f}%, north of 48.8S {s['z_n488']:.1f}%, north of 60S {s['z_n60']:.1f}%",
      f"- Temporal synchrony index: {s['sync']:.2f}",
      f"- High-risk birds: {s['high']}",
      f"- Cluster sizes, low / medium / high: {s['sizes']}",
      f"- Random Forest test accuracy: {s['rf']:.1f}%",
      f"- Random Forest accuracy with whole birds held out: {s['rf_lobo']:.1f}% pooled",
      f"- Feature importances: distance from colony {s['imp_dist_from_campbell']:.2f}, latitude {s['imp_location-lat']:.2f}, longitude {s['imp_location-long']:.2f}, SST {s['imp_sst']:.2f}, chlorophyll-a {s['imp_chla']:.2f}",
      f"- Closest approach across birds: {s['closest_min']:.1f} to {s['closest_max']:.1f} km",
      f"- Mean SST: foraging {s['sst_f']:.2f} C, not foraging {s['sst_nf']:.2f} C", '']

L += ['## 6. Bird 90494 in detail', '']
rows = []
x = {v: data[v][0][data[v][0][ID] == '90494'] for v in V}
for name, fn in [('First fix', lambda v, y: f'{y.timestamp.iloc[0]}'), ('Last fix', lambda v, y: f'{y.timestamp.iloc[-1]}'),
                 ('Duration (days)', lambda v, y: f"{pb[v].loc['90494', 'duration_days']:.2f}"),
                 ('Away trips, 50 km rule', lambda v, y: pb[v].loc['90494', 'away_trips']),
                 ('Away trips lasting 1 day or more', lambda v, y: pb[v].loc['90494', 'away_trips_1d']),
                 ('Foraging bouts', lambda v, y: pb[v].loc['90494', 'bouts']),
                 ('Ring count', lambda v, y: pb[v].loc['90494', 'rings']),
                 ('Resting fixes', lambda v, y: int((y.behaviour == 0).sum())),
                 ('Foraging fixes', lambda v, y: int((y.behaviour == 1).sum())),
                 ('Transiting fixes', lambda v, y: int((y.behaviour == 2).sum())),
                 ('Distinct trip_id values', lambda v, y: y.trip_id.nunique()),
                 ('Total distance (km)', lambda v, y: f"{pb[v].loc['90494', 'total_dist_km']:,.1f}"),
                 ('Distance at first fix (km)', lambda v, y: f"{pb[v].loc['90494', 'first_km']:.2f}"),
                 ('Distance at last fix (km)', lambda v, y: f"{pb[v].loc['90494', 'last_km']:.2f}")]:
    rows.append([name] + [fn(v, x[v]) for v in V])
L += table(['Measure', 'old', 'v2', 'v3'], rows) + ['']

L += ['## 7. Away trips and distance to the colony point, per bird', '']
L += table(['Bird', 'Trips old', 'Trips v2', 'Trips v3', 'Closest km v2', 'Closest km v3', 'First fix km v2', 'First fix km v3', 'Last fix km v2', 'Last fix km v3'],
           [[b] + [pb[v].loc[b, 'away_trips'] for v in V] + [f"{pb[v].loc[b, k]:.2f}" for k in ['closest_km', 'first_km', 'last_km'] for v in ('v2', 'v3')] for b in birds]) + ['']

ref = pd.read_csv('data/raw/movebank_reference_data.csv', dtype=str, keep_default_na=False).set_index('animal-id')
rows = []
for b in birds:
    dep = pd.Timestamp(ref.loc[b, 'deploy-on-date'])
    f0, f1 = data['old'][0][data['old'][0][ID] == b].timestamp.min(), data['v2'][0][data['v2'][0][ID] == b].timestamp.min()
    rows.append([b, ref.loc[b, 'deploy-on-date'], f0, f1, f'{(f0 - dep).total_seconds() / 3600:,.2f}', f'{(f1 - dep).total_seconds() / 3600:,.2f}'])
L += ['## 8. Movebank reference data: deployment date against first fix', '',
      'Values are as stored in `data/raw/movebank_reference_data.csv`. Differences are first fix minus deploy-on-date.', '']
L += table(['Bird', 'deploy-on-date', 'First fix, original file', 'First fix, after repair', 'Hours, original', 'Hours, after repair'], rows) + ['']

Path('outputs_v2/comparison_report.md').write_text('\n'.join(L), encoding='utf-8')
print('\n'.join(L))
