# Control run versus existing data/processed/

Control: copied pipeline, original unrepaired raw file, old colony point.

Environment: Python 3.13.10, pandas 3.0.1, numpy 2.4.3, scipy 1.17.1, scikit-learn 1.8.0, hmmlearn 0.3.3, xarray 2026.4.0

Numeric tolerance: absolute difference up to 1e-06.

| File | Rows old / control | Same columns | Exact text match | Numeric columns over tolerance | Other columns differing |
|---|---|---|---|---|---|
| tracks_with_metrics.csv | 93,474 / 93,474 | True | True | none | none |
| tracks_with_behaviour.csv | 93,474 / 93,474 | True | True | none | none |
| tracks_with_env.csv | 93,474 / 93,474 | True | True | none | none |
| bird_profiles.csv | 24 / 24 | True | True | none | none |
| bird_risk_profiles.csv | 24 / 24 | True | True | none | none |
| trip_statistics.csv | 25 / 25 | True | True | none | none |
| foraging_kde_grid.csv | 45,000 / 45,000 | True | True | none | none |

## State labels

Fixes joined on event-id: 93,474. Behaviour label differs on 0. Raw HMM state number differs on 0.

## Differences

None over tolerance.

## Result: REPRODUCED within tolerance
