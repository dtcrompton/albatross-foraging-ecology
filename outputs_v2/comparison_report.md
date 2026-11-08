# Old versus v2 versus v3

- **old:** existing `data/processed/` (original data, colony point 169.15E, 52.55S).
- **v2:** bird 90494 dates repaired, colony point 169.15E, 52.55S (`data/processed_v2/`).
- **v3:** bird 90494 dates repaired, colony point 169.224E, 52.474S (`data/processed_v3/`).

Control: the copied pipeline on the original raw file reproduced all seven `data/processed/` files byte for byte (`outputs_v2/control_comparison.md`), so no comparison below carries a reproducibility flag.

Sources for every number: `outputs_v2/per_bird_comparison.csv` and the run logs in `rerun_v2/logs/`.

Definitions: a foraging bout is a contiguous run of behaviour 1 (duration is last minus first timestamp, minimum 0.1 h). Ring count is `min(40, max(3, n_bouts // 10))`. An away trip is a run of fixes over 50 km from the colony point.

## 1. Per bird: values

### Fixes

| Bird | old | v2 | v3 |
|---|---|---|---|
| 1 | 4,459 | 4,459 | 4,459 |
| 2 | 4,660 | 4,660 | 4,660 |
| 23058 | 3,008 | 3,008 | 3,008 |
| 23059 | 3,551 | 3,551 | 3,551 |
| 23096 | 4,448 | 4,448 | 4,448 |
| 23782 | 3,139 | 3,139 | 3,139 |
| 29155 | 3,618 | 3,618 | 3,618 |
| 41269 | 4,401 | 4,401 | 4,401 |
| 49364 | 2,582 | 2,582 | 2,582 |
| 58565 | 5,892 | 5,892 | 5,892 |
| 61696 | 1,785 | 1,785 | 1,785 |
| 62093 | 4,361 | 4,361 | 4,361 |
| 82589 | 2,553 | 2,553 | 2,553 |
| 89518 | 5,959 | 5,959 | 5,959 |
| 89570 | 3,963 | 3,963 | 3,963 |
| 90282 | 3,891 | 3,891 | 3,891 |
| 90287 | 3,561 | 3,561 | 3,561 |
| 90407 | 2,234 | 2,234 | 2,234 |
| 90420 | 5,278 | 5,278 | 5,278 |
| 90434 | 4,657 | 4,657 | 4,657 |
| 90468 | 4,329 | 4,329 | 4,329 |
| 90493 | 3,558 | 3,558 | 3,558 |
| 90494 | 4,668 | 4,668 | 4,668 |
| 90590 | 2,919 | 2,919 | 2,919 |

### Duration (days)

| Bird | old | v2 | v3 |
|---|---|---|---|
| 1 | 16.18 | 16.18 | 16.18 |
| 2 | 16.78 | 16.78 | 16.78 |
| 23058 | 13.42 | 13.42 | 13.42 |
| 23059 | 12.72 | 12.72 | 12.72 |
| 23096 | 18.52 | 18.52 | 18.52 |
| 23782 | 13.70 | 13.70 | 13.70 |
| 29155 | 13.02 | 13.02 | 13.02 |
| 41269 | 15.12 | 15.12 | 15.12 |
| 49364 | 11.00 | 11.00 | 11.00 |
| 58565 | 21.67 | 21.67 | 21.67 |
| 61696 | 7.67 | 7.67 | 7.67 |
| 62093 | 15.86 | 15.86 | 15.86 |
| 82589 | 11.86 | 11.86 | 11.86 |
| 89518 | 21.94 | 21.94 | 21.94 |
| 89570 | 14.10 | 14.10 | 14.10 |
| 90282 | 13.87 | 13.87 | 13.87 |
| 90287 | 12.92 | 12.92 | 12.92 |
| 90407 | 10.30 | 10.30 | 10.30 |
| 90420 | 19.23 | 19.23 | 19.23 |
| 90434 | 16.78 | 16.78 | 16.78 |
| 90468 | 15.65 | 15.65 | 15.65 |
| 90493 | 15.74 | 15.74 | 15.74 |
| 90494 | 335.00 | 16.95 | 16.95 |
| 90590 | 12.97 | 12.97 | 12.97 |

### Foraging bouts

| Bird | old | v2 | v3 |
|---|---|---|---|
| 1 | 296 | 296 | 296 |
| 2 | 317 | 317 | 317 |
| 23058 | 193 | 193 | 193 |
| 23059 | 206 | 206 | 206 |
| 23096 | 292 | 292 | 292 |
| 23782 | 211 | 211 | 211 |
| 29155 | 230 | 230 | 230 |
| 41269 | 254 | 254 | 254 |
| 49364 | 160 | 160 | 160 |
| 58565 | 458 | 457 | 457 |
| 61696 | 116 | 116 | 116 |
| 62093 | 323 | 323 | 323 |
| 82589 | 153 | 153 | 153 |
| 89518 | 383 | 382 | 382 |
| 89570 | 231 | 231 | 231 |
| 90282 | 249 | 249 | 249 |
| 90287 | 246 | 246 | 246 |
| 90407 | 129 | 129 | 129 |
| 90420 | 311 | 311 | 311 |
| 90434 | 394 | 394 | 394 |
| 90468 | 313 | 313 | 313 |
| 90493 | 217 | 217 | 217 |
| 90494 | 264 | 263 | 263 |
| 90590 | 207 | 207 | 207 |

### Proportion foraging

| Bird | old | v2 | v3 |
|---|---|---|---|
| 1 | 0.428 | 0.427 | 0.427 |
| 2 | 0.326 | 0.326 | 0.326 |
| 23058 | 0.466 | 0.466 | 0.466 |
| 23059 | 0.436 | 0.436 | 0.436 |
| 23096 | 0.476 | 0.476 | 0.476 |
| 23782 | 0.428 | 0.428 | 0.428 |
| 29155 | 0.389 | 0.389 | 0.389 |
| 41269 | 0.366 | 0.366 | 0.366 |
| 49364 | 0.590 | 0.590 | 0.590 |
| 58565 | 0.410 | 0.410 | 0.410 |
| 61696 | 0.407 | 0.407 | 0.407 |
| 62093 | 0.342 | 0.342 | 0.342 |
| 82589 | 0.490 | 0.490 | 0.490 |
| 89518 | 0.337 | 0.336 | 0.336 |
| 89570 | 0.344 | 0.344 | 0.344 |
| 90282 | 0.417 | 0.417 | 0.417 |
| 90287 | 0.439 | 0.439 | 0.439 |
| 90407 | 0.449 | 0.449 | 0.449 |
| 90420 | 0.446 | 0.446 | 0.446 |
| 90434 | 0.375 | 0.375 | 0.375 |
| 90468 | 0.448 | 0.448 | 0.448 |
| 90493 | 0.419 | 0.419 | 0.419 |
| 90494 | 0.438 | 0.437 | 0.437 |
| 90590 | 0.339 | 0.339 | 0.339 |

### Max distance (km)

| Bird | old | v2 | v3 |
|---|---|---|---|
| 1 | 929.7 | 929.7 | 929.3 |
| 2 | 2,326.6 | 2,326.6 | 2,318.9 |
| 23058 | 1,009.4 | 1,009.4 | 1,009.2 |
| 23059 | 744.7 | 744.7 | 745.7 |
| 23096 | 1,139.7 | 1,139.7 | 1,139.9 |
| 23782 | 1,001.0 | 1,001.0 | 1,000.6 |
| 29155 | 915.5 | 915.5 | 922.9 |
| 41269 | 1,352.1 | 1,352.1 | 1,347.4 |
| 49364 | 786.9 | 786.9 | 796.2 |
| 58565 | 1,271.8 | 1,271.8 | 1,270.6 |
| 61696 | 803.3 | 803.3 | 803.2 |
| 62093 | 1,009.1 | 1,009.1 | 1,013.5 |
| 82589 | 1,040.1 | 1,040.1 | 1,039.5 |
| 89518 | 2,642.7 | 2,642.7 | 2,640.3 |
| 89570 | 892.7 | 892.7 | 900.1 |
| 90282 | 901.4 | 901.4 | 901.4 |
| 90287 | 1,193.3 | 1,193.3 | 1,192.2 |
| 90407 | 967.7 | 967.7 | 967.8 |
| 90420 | 1,417.1 | 1,417.1 | 1,412.1 |
| 90434 | 769.9 | 769.9 | 771.0 |
| 90468 | 1,004.1 | 1,004.1 | 1,004.8 |
| 90493 | 2,715.2 | 2,715.2 | 2,713.1 |
| 90494 | 1,135.6 | 1,135.6 | 1,134.8 |
| 90590 | 1,719.1 | 1,719.1 | 1,713.3 |

### Total distance (km)

| Bird | old | v2 | v3 |
|---|---|---|---|
| 1 | 8,514.2 | 8,514.2 | 8,514.2 |
| 2 | 11,481.6 | 11,481.6 | 11,481.6 |
| 23058 | 5,630.9 | 5,630.9 | 5,630.9 |
| 23059 | 4,928.7 | 4,928.7 | 4,928.7 |
| 23096 | 7,284.8 | 7,284.8 | 7,284.8 |
| 23782 | 5,140.2 | 5,140.2 | 5,140.2 |
| 29155 | 5,740.8 | 5,740.8 | 5,740.8 |
| 41269 | 8,773.0 | 8,773.0 | 8,773.0 |
| 49364 | 4,295.7 | 4,295.7 | 4,295.7 |
| 58565 | 11,089.3 | 11,089.3 | 11,089.3 |
| 61696 | 3,464.8 | 3,464.8 | 3,464.8 |
| 62093 | 9,233.0 | 9,233.0 | 9,233.0 |
| 82589 | 5,293.1 | 5,293.1 | 5,293.1 |
| 89518 | 12,284.7 | 12,284.7 | 12,284.7 |
| 89570 | 7,084.5 | 7,084.5 | 7,084.5 |
| 90282 | 6,324.2 | 6,324.2 | 6,324.2 |
| 90287 | 6,852.1 | 6,852.1 | 6,852.1 |
| 90407 | 4,541.7 | 4,541.7 | 4,541.7 |
| 90420 | 8,501.6 | 8,501.6 | 8,501.6 |
| 90434 | 9,592.9 | 9,592.9 | 9,592.9 |
| 90468 | 7,913.8 | 7,913.8 | 7,913.8 |
| 90493 | 9,713.1 | 9,713.1 | 9,713.1 |
| 90494 | 9,013.3 | 6,978.2 | 6,978.2 |
| 90590 | 7,141.0 | 7,141.0 | 7,141.0 |

### Forage centre latitude

| Bird | old | v2 | v3 |
|---|---|---|---|
| 1 | -55.9950 | -55.9953 | -55.9953 |
| 2 | -53.0746 | -53.0746 | -53.0746 |
| 23058 | -56.3804 | -56.3804 | -56.3804 |
| 23059 | -55.6285 | -55.6288 | -55.6288 |
| 23096 | -56.1032 | -56.1032 | -56.1032 |
| 23782 | -56.1039 | -56.1039 | -56.1039 |
| 29155 | -59.2154 | -59.2154 | -59.2154 |
| 41269 | -54.8267 | -54.8267 | -54.8267 |
| 49364 | -58.6892 | -58.6892 | -58.6892 |
| 58565 | -56.1901 | -56.1902 | -56.1902 |
| 61696 | -55.6657 | -55.6657 | -55.6657 |
| 62093 | -57.6567 | -57.6567 | -57.6567 |
| 82589 | -56.3560 | -56.3560 | -56.3560 |
| 89518 | -55.6102 | -55.6101 | -55.6101 |
| 89570 | -58.5519 | -58.5519 | -58.5519 |
| 90282 | -55.9215 | -55.9215 | -55.9215 |
| 90287 | -56.0250 | -56.0250 | -56.0250 |
| 90407 | -56.3698 | -56.3698 | -56.3698 |
| 90420 | -55.4895 | -55.4895 | -55.4895 |
| 90434 | -55.5473 | -55.5474 | -55.5474 |
| 90468 | -55.7112 | -55.7112 | -55.7112 |
| 90493 | -53.0160 | -53.0160 | -53.0160 |
| 90494 | -56.0663 | -56.0680 | -56.0680 |
| 90590 | -54.9805 | -54.9805 | -54.9805 |

### Risk cluster

| Bird | old | v2 | v3 |
|---|---|---|---|
| 1 | Medium risk | Medium risk | Medium risk |
| 2 | High risk | High risk | High risk |
| 23058 | Low risk | Low risk | Low risk |
| 23059 | Low risk | Low risk | Low risk |
| 23096 | Low risk | Low risk | Low risk |
| 23782 | Low risk | Low risk | Low risk |
| 29155 | Low risk | Low risk | Low risk |
| 41269 | Medium risk | Medium risk | Medium risk |
| 49364 | Low risk | Low risk | Low risk |
| 58565 | Medium risk | Medium risk | Medium risk |
| 61696 | Low risk | Low risk | Low risk |
| 62093 | Medium risk | Medium risk | Medium risk |
| 82589 | Low risk | Low risk | Low risk |
| 89518 | High risk | High risk | High risk |
| 89570 | Medium risk | Medium risk | Medium risk |
| 90282 | Low risk | Low risk | Low risk |
| 90287 | Low risk | Low risk | Low risk |
| 90407 | Low risk | Low risk | Low risk |
| 90420 | Medium risk | Medium risk | Medium risk |
| 90434 | Medium risk | Medium risk | Medium risk |
| 90468 | Medium risk | Low risk | Low risk |
| 90493 | High risk | High risk | High risk |
| 90494 | Medium risk | Low risk | Low risk |
| 90590 | Medium risk | Medium risk | Medium risk |

### Ring count

| Bird | old | v2 | v3 |
|---|---|---|---|
| 1 | 29 | 29 | 29 |
| 2 | 31 | 31 | 31 |
| 23058 | 19 | 19 | 19 |
| 23059 | 20 | 20 | 20 |
| 23096 | 29 | 29 | 29 |
| 23782 | 21 | 21 | 21 |
| 29155 | 23 | 23 | 23 |
| 41269 | 25 | 25 | 25 |
| 49364 | 16 | 16 | 16 |
| 58565 | 40 | 40 | 40 |
| 61696 | 11 | 11 | 11 |
| 62093 | 32 | 32 | 32 |
| 82589 | 15 | 15 | 15 |
| 89518 | 38 | 38 | 38 |
| 89570 | 23 | 23 | 23 |
| 90282 | 24 | 24 | 24 |
| 90287 | 24 | 24 | 24 |
| 90407 | 12 | 12 | 12 |
| 90420 | 31 | 31 | 31 |
| 90434 | 39 | 39 | 39 |
| 90468 | 31 | 31 | 31 |
| 90493 | 21 | 21 | 21 |
| 90494 | 26 | 26 | 26 |
| 90590 | 20 | 20 | 20 |

## 1b. Per bird differences: old to v2 (date repair)

| Bird | Fixes | Duration (days) | Foraging bouts | Proportion foraging | Max distance (km) | Total distance (km) | Forage centre latitude | Risk cluster | Ring count |
|---|---|---|---|---|---|---|---|---|---|
| 1 | +0 | +0.00 | +0 | -0.02 pp | +0.0 | +0.0 | -0.0003 | same | +0 |
| 2 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 23058 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 23059 | +0 | +0.00 | +0 | -0.03 pp | +0.0 | +0.0 | -0.0003 | same | +0 |
| 23096 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 23782 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 29155 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 41269 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 49364 | +0 | +0.00 | +0 | -0.04 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 58565 | +0 | +0.00 | -1 | -0.02 pp | +0.0 | +0.0 | -0.0001 | same | +0 |
| 61696 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 62093 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 82589 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 89518 | +0 | +0.00 | -1 | -0.02 pp | +0.0 | +0.0 | +0.0001 | same | +0 |
| 89570 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 90282 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 90287 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 90407 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 90420 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 90434 | +0 | +0.00 | +0 | -0.02 pp | +0.0 | +0.0 | -0.0001 | same | +0 |
| 90468 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | Medium risk to Low risk | +0 |
| 90493 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 90494 | +0 | -318.05 | -1 | -0.04 pp | +0.0 | -2,035.1 | -0.0017 | Medium risk to Low risk | +0 |
| 90590 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |

## 1c. Per bird differences: v2 to v3 (colony point)

| Bird | Fixes | Duration (days) | Foraging bouts | Proportion foraging | Max distance (km) | Total distance (km) | Forage centre latitude | Risk cluster | Ring count |
|---|---|---|---|---|---|---|---|---|---|
| 1 | +0 | +0.00 | +0 | +0.00 pp | -0.4 | +0.0 | +0.0000 | same | +0 |
| 2 | +0 | +0.00 | +0 | +0.00 pp | -7.7 | +0.0 | +0.0000 | same | +0 |
| 23058 | +0 | +0.00 | +0 | +0.00 pp | -0.2 | +0.0 | +0.0000 | same | +0 |
| 23059 | +0 | +0.00 | +0 | +0.00 pp | +0.9 | +0.0 | +0.0000 | same | +0 |
| 23096 | +0 | +0.00 | +0 | +0.00 pp | +0.2 | +0.0 | +0.0000 | same | +0 |
| 23782 | +0 | +0.00 | +0 | +0.00 pp | -0.4 | +0.0 | +0.0000 | same | +0 |
| 29155 | +0 | +0.00 | +0 | +0.00 pp | +7.5 | +0.0 | +0.0000 | same | +0 |
| 41269 | +0 | +0.00 | +0 | +0.00 pp | -4.6 | +0.0 | +0.0000 | same | +0 |
| 49364 | +0 | +0.00 | +0 | +0.00 pp | +9.3 | +0.0 | +0.0000 | same | +0 |
| 58565 | +0 | +0.00 | +0 | +0.00 pp | -1.1 | +0.0 | +0.0000 | same | +0 |
| 61696 | +0 | +0.00 | +0 | +0.00 pp | -0.1 | +0.0 | +0.0000 | same | +0 |
| 62093 | +0 | +0.00 | +0 | +0.00 pp | +4.4 | +0.0 | +0.0000 | same | +0 |
| 82589 | +0 | +0.00 | +0 | +0.00 pp | -0.6 | +0.0 | +0.0000 | same | +0 |
| 89518 | +0 | +0.00 | +0 | +0.00 pp | -2.3 | +0.0 | +0.0000 | same | +0 |
| 89570 | +0 | +0.00 | +0 | +0.00 pp | +7.4 | +0.0 | +0.0000 | same | +0 |
| 90282 | +0 | +0.00 | +0 | +0.00 pp | +0.0 | +0.0 | +0.0000 | same | +0 |
| 90287 | +0 | +0.00 | +0 | +0.00 pp | -1.1 | +0.0 | +0.0000 | same | +0 |
| 90407 | +0 | +0.00 | +0 | +0.00 pp | +0.1 | +0.0 | +0.0000 | same | +0 |
| 90420 | +0 | +0.00 | +0 | +0.00 pp | -5.0 | +0.0 | +0.0000 | same | +0 |
| 90434 | +0 | +0.00 | +0 | +0.00 pp | +1.1 | +0.0 | +0.0000 | same | +0 |
| 90468 | +0 | +0.00 | +0 | +0.00 pp | +0.6 | +0.0 | +0.0000 | same | +0 |
| 90493 | +0 | +0.00 | +0 | +0.00 pp | -2.2 | +0.0 | +0.0000 | same | +0 |
| 90494 | +0 | +0.00 | +0 | +0.00 pp | -0.8 | +0.0 | +0.0000 | same | +0 |
| 90590 | +0 | +0.00 | +0 | +0.00 pp | -5.8 | +0.0 | +0.0000 | same | +0 |

## 2. State stability

Percentage of each bird's fixes whose HMM state changed, joined on event-id.

| Bird | old to v2 fixes | old to v2 % | v2 to v3 fixes | v2 to v3 % |
|---|---|---|---|---|
| 1 | 1 | 0.022% | 0 | 0.000% |
| 2 | 0 | 0.000% | 0 | 0.000% |
| 23058 | 0 | 0.000% | 0 | 0.000% |
| 23059 | 1 | 0.028% | 0 | 0.000% |
| 23096 | 0 | 0.000% | 0 | 0.000% |
| 23782 | 0 | 0.000% | 0 | 0.000% |
| 29155 | 0 | 0.000% | 0 | 0.000% |
| 41269 | 0 | 0.000% | 0 | 0.000% |
| 49364 | 1 | 0.039% | 0 | 0.000% |
| 58565 | 1 | 0.017% | 0 | 0.000% |
| 61696 | 0 | 0.000% | 0 | 0.000% |
| 62093 | 0 | 0.000% | 0 | 0.000% |
| 82589 | 0 | 0.000% | 0 | 0.000% |
| 89518 | 1 | 0.017% | 0 | 0.000% |
| 89570 | 0 | 0.000% | 0 | 0.000% |
| 90282 | 0 | 0.000% | 0 | 0.000% |
| 90287 | 0 | 0.000% | 0 | 0.000% |
| 90407 | 0 | 0.000% | 0 | 0.000% |
| 90420 | 0 | 0.000% | 0 | 0.000% |
| 90434 | 1 | 0.021% | 0 | 0.000% |
| 90468 | 0 | 0.000% | 0 | 0.000% |
| 90493 | 0 | 0.000% | 0 | 0.000% |
| 90494 | 2 | 0.043% | 0 | 0.000% |
| 90590 | 0 | 0.000% | 0 | 0.000% |

All birds: old to v2 8 fixes; v2 to v3 0 fixes.

### HMM state parameters

| State | Step km old | Step km v2 | Step km v3 | Turn deg old | Turn deg v2 | Turn deg v3 |
|---|---|---|---|---|---|---|
| Resting | 0.1405 | 0.1404 | 0.1404 | 6.869 | 6.871 | 6.871 |
| Foraging | 1.4374 | 1.3842 | 1.3842 | 62.191 | 62.196 | 62.196 |
| Transiting | 4.0435 | 4.0435 | 4.0435 | 9.925 | 9.927 | 9.927 |

## 3. Published statistics

Values show extra decimal places. "Changes" is judged at the precision the page publishes. Whole-bird hold-out uses the same forest settings, leaving out each of the 24 birds once. The "old" forest uses the existing `tracks_with_env.csv`.

| Statistic | Published | old | v2 | v3 | old to v2 | v2 to v3 |
|---|---|---|---|---|---|---|
| Total fixes | 93,474 | 93,474 | 93,474 | 93,474 | same | same |
| Birds | 24 | 24 | 24 | 24 | same | same |
| Foraging share of fixes (%) | 41.1 | 41.07 | 41.06 | 41.06 | same | same |
| Resting share of fixes (%) | 26.9 | 26.89 | 26.89 | 26.89 | same | same |
| Transiting share of fixes (%) | 32.0 | 32.05 | 32.05 | 32.05 | changes | same |
| Mean turning, foraging (deg) | 62.2 | 62.19 | 62.20 | 62.20 | same | same |
| Mean turning, transiting (deg) | 9.9 | 9.92 | 9.93 | 9.93 | same | same |
| Mean turning, resting (deg) | 6.9 | 6.87 | 6.87 | 6.87 | same | same |
| Mean step, resting (km) | 0.14 | 0.140 | 0.140 | 0.140 | same | same |
| Mean step, foraging (km) | 1.44 | 1.437 | 1.384 | 1.384 | changes | same |
| Mean step, transiting (km) | 4.04 | 4.043 | 4.043 | 4.043 | same | same |
| Max foraging distance, lowest bird (km) | 745 | 744.7 | 744.7 | 745.7 | same | changes |
| Max foraging distance, highest bird (km) | 2,715 | 2,715.2 | 2,715.2 | 2,713.1 | same | changes |
| Range multiple | 3.5 | 3.646 | 3.646 | 3.638 | same | same |
| Proportion foraging, lowest bird (%) | 33 | 32.6 | 32.6 | 32.6 | same | same |
| Proportion foraging, highest bird (%) | 59 | 59.0 | 59.0 | 59.0 | same | same |
| Total distance, lowest bird (km) | 3,465 | 3,464.8 | 3,464.8 | 3,464.8 | same | same |
| Total distance, highest bird (km) | 12,285 | 12,284.7 | 12,284.7 | 12,284.7 | same | same |
| Trips of 1 day or more, trip_statistics rows | not published | 25 | 24 | 24 | changes | same |
| Mean trip duration (days) | 25 | 25.18 | 14.81 | 14.82 | changes | same |
| Longest trip duration (days) | 274 | 274.00 | 21.84 | 21.83 | changes | same |
| Zone: south of 60S (%) | 0.9 | 0.943 | 0.943 | 0.943 | same | same |
| Zone: 60S to 48.8S (%) | 97.5 | 97.512 | 97.512 | 97.512 | same | same |
| Zone: north of 48.8S (%) | not published | 1.545 | 1.545 | 1.545 | same | same |
| Zone: north of 60S (%) | 99.1 | 99.057 | 99.057 | 99.057 | same | same |
| Temporal synchrony index | 0.31 | 0.310 | 0.295 | 0.295 | changes | same |
| High-risk birds | 2, 89518, 90493 | 2, 89518, 90493 | 2, 89518, 90493 | 2, 89518, 90493 | same | same |
| Cluster sizes, low / medium / high | 3 high | 11 / 10 / 3 | 13 / 8 / 3 | 13 / 8 / 3 | changes | same |
| Random Forest test accuracy (%) | 64.9 | 64.91 | 65.08 | 65.19 | changes | changes |
| Importance: distance from colony | 0.31 | 0.309 | 0.300 | 0.304 | changes | same |
| Importance: latitude | 0.24 | 0.238 | 0.239 | 0.239 | same | same |
| Importance: longitude | 0.19 | 0.194 | 0.200 | 0.198 | changes | same |
| Importance: SST | 0.15 | 0.153 | 0.159 | 0.158 | changes | same |
| Importance: chlorophyll-a | 0.11 | 0.106 | 0.101 | 0.101 | changes | same |
| RF accuracy, whole bird held out, pooled (%) | not published | 57.04 | 56.40 | 56.36 | changes | same |
| RF accuracy, whole bird held out, mean of birds (%) | not published | 57.26 | 56.67 | 56.60 | changes | changes |
| RF accuracy, whole bird held out, range across birds (%) | not published | 49.7 to 64.6 | 50.2 to 65.4 | 49.5 to 66.1 | changes | changes |
| Largest-class share of modelled fixes (%) | not published | 59.05 | 58.96 | 58.96 | changes | same |
| Closest approach, lowest bird (km) | 7 | 7.33 | 7.33 | 5.07 | same | changes |
| Closest approach, highest bird (km) | 14 | 14.22 | 14.22 | 7.83 | same | changes |
| Mean SST, foraging (C) | 6.31 | 6.323 | 6.307 | 6.307 | changes | same |
| Mean SST, not foraging (C) | 6.44 | 6.432 | 6.423 | 6.423 | changes | same |

### Foraging fixes by month

| Month | old | v2 | v3 |
|---|---|---|---|
| 1 | 164 | 0 | 0 |
| 2 | 149 | 0 | 0 |
| 3 | 92 | 0 | 0 |
| 4 | 133 | 0 | 0 |
| 5 | 108 | 0 | 0 |
| 6 | 153 | 0 | 0 |
| 7 | 152 | 0 | 0 |
| 8 | 126 | 0 | 0 |
| 9 | 111 | 0 | 0 |
| 10 | 15809 | 15631 | 15631 |
| 11 | 19147 | 20648 | 20648 |
| 12 | 2243 | 2100 | 2100 |

## 3b. Statistics that change only because of the colony point

Same from old to v2, different from v2 to v3, at published precision:

- Max foraging distance, lowest bird (km)
- Max foraging distance, highest bird (km)
- Closest approach, lowest bird (km)
- Closest approach, highest bird (km)

Change only because of the date repair:

- Transiting share of fixes (%)
- Mean step, foraging (km)
- Trips of 1 day or more, trip_statistics rows
- Mean trip duration (days)
- Longest trip duration (days)
- Temporal synchrony index
- Cluster sizes, low / medium / high
- Importance: distance from colony
- Importance: longitude
- Importance: SST
- Importance: chlorophyll-a
- RF accuracy, whole bird held out, pooled (%)
- Largest-class share of modelled fixes (%)
- Mean SST, foraging (C)
- Mean SST, not foraging (C)

Change at both steps:

- Random Forest test accuracy (%)
- RF accuracy, whole bird held out, mean of birds (%)
- RF accuracy, whole bird held out, range across birds (%)

Unchanged at both steps:

- Total fixes
- Birds
- Foraging share of fixes (%)
- Resting share of fixes (%)
- Mean turning, foraging (deg)
- Mean turning, transiting (deg)
- Mean turning, resting (deg)
- Mean step, resting (km)
- Mean step, transiting (km)
- Range multiple
- Proportion foraging, lowest bird (%)
- Proportion foraging, highest bird (%)
- Total distance, lowest bird (km)
- Total distance, highest bird (km)
- Zone: south of 60S (%)
- Zone: 60S to 48.8S (%)
- Zone: north of 48.8S (%)
- Zone: north of 60S (%)
- High-risk birds
- Importance: latitude

## 4. Flags

Ring count change of 1 or more, proportion foraging change over 1 percentage point, or cluster change.

| Step | Bird | Flag | From | To |
|---|---|---|---|---|
| old to v2 | 90468 | cluster | Medium risk | Low risk |
| old to v2 | 90494 | cluster | Medium risk | Low risk |

## 5. Numbers for the web pages

All from v3 (dates repaired, colony point 169.224E, 52.474S).

- Total fixes: 93,474
- Birds: 24
- Foraging share of fixes: 41.1%
- Resting share of fixes: 26.9%
- Transiting share of fixes: 32.1%
- Mean turning angle: foraging 62.2 degrees, transiting 9.9 degrees, resting 6.9 degrees
- Mean step length: resting 0.14 km, foraging 1.38 km, transiting 4.04 km
- Maximum foraging distance range: 746 to 2,713 km
- Range multiple: 3.6
- Proportion foraging range: 33% to 59%
- Total distance range: 3,465 to 12,285 km
- Mean trip duration: 14.8 days
- Longest trip duration: 21.8 days
- Date range: 14 Oct 2013 to 12 Dec 2013
- Latitude zones: south of 60S 0.9%, 60S to 48.8S 97.5%, north of 48.8S 1.5%, north of 60S 99.1%
- Temporal synchrony index: 0.30
- High-risk birds: 2, 89518, 90493
- Cluster sizes, low / medium / high: 13 / 8 / 3
- Random Forest test accuracy: 65.2%
- Random Forest accuracy with whole birds held out: 56.4% pooled
- Feature importances: distance from colony 0.30, latitude 0.24, longitude 0.20, SST 0.16, chlorophyll-a 0.10
- Closest approach across birds: 5.1 to 7.8 km
- Mean SST: foraging 6.31 C, not foraging 6.42 C

## 6. Bird 90494 in detail

| Measure | old | v2 | v3 |
|---|---|---|---|
| First fix | 2013-01-11 00:00:00 | 2013-10-31 03:23:09 | 2013-10-31 03:23:09 |
| Last fix | 2013-12-11 23:57:00 | 2013-11-17 02:06:56 | 2013-11-17 02:06:56 |
| Duration (days) | 335.00 | 16.95 | 16.95 |
| Away trips, 50 km rule | 3 | 1 | 1 |
| Away trips lasting 1 day or more | 2 | 1 | 1 |
| Foraging bouts | 264 | 263 | 263 |
| Ring count | 26 | 26 | 26 |
| Resting fixes | 1401 | 1401 | 1401 |
| Foraging fixes | 2043 | 2041 | 2041 |
| Transiting fixes | 1224 | 1226 | 1226 |
| Distinct trip_id values | 5 | 3 | 3 |
| Total distance (km) | 9,013.3 | 6,978.2 | 6,978.2 |
| Distance at first fix (km) | 645.26 | 14.46 | 5.31 |
| Distance at last fix (km) | 825.65 | 9.14 | 5.20 |

## 7. Away trips and distance to the colony point, per bird

| Bird | Trips old | Trips v2 | Trips v3 | Closest km v2 | Closest km v3 | First fix km v2 | First fix km v3 | Last fix km v2 | Last fix km v3 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 1 | 1 | 12.06 | 5.90 | 16.24 | 10.89 | 12.06 | 5.90 |
| 2 | 1 | 1 | 1 | 7.43 | 5.48 | 10.90 | 5.48 | 7.43 | 5.54 |
| 23058 | 1 | 1 | 1 | 13.74 | 6.64 | 17.67 | 10.71 | 13.74 | 6.64 |
| 23059 | 1 | 1 | 1 | 7.82 | 5.26 | 16.08 | 9.24 | 7.82 | 5.26 |
| 23096 | 1 | 1 | 1 | 11.78 | 7.60 | 13.31 | 9.26 | 11.78 | 7.60 |
| 23782 | 1 | 1 | 1 | 9.24 | 5.07 | 13.09 | 5.07 | 9.37 | 5.61 |
| 29155 | 1 | 1 | 1 | 8.40 | 5.70 | 11.01 | 5.70 | 8.40 | 9.32 |
| 41269 | 1 | 1 | 1 | 7.88 | 5.96 | 15.04 | 6.67 | 7.88 | 5.96 |
| 49364 | 1 | 1 | 1 | 8.94 | 6.22 | 10.99 | 7.96 | 8.94 | 6.22 |
| 58565 | 1 | 1 | 1 | 8.18 | 5.78 | 13.57 | 5.78 | 8.18 | 6.86 |
| 61696 | 1 | 1 | 1 | 13.94 | 7.83 | 13.94 | 8.76 | 14.85 | 7.83 |
| 62093 | 1 | 1 | 1 | 9.60 | 6.94 | 15.78 | 10.31 | 9.60 | 6.94 |
| 82589 | 1 | 1 | 1 | 8.01 | 6.50 | 13.19 | 6.50 | 8.01 | 9.94 |
| 89518 | 1 | 1 | 1 | 13.75 | 6.63 | 13.80 | 6.63 | 13.75 | 7.97 |
| 89570 | 1 | 1 | 1 | 11.11 | 6.34 | 11.26 | 6.34 | 11.11 | 10.08 |
| 90282 | 2 | 2 | 2 | 9.96 | 5.99 | 12.02 | 8.70 | 9.96 | 5.99 |
| 90287 | 1 | 1 | 1 | 10.99 | 7.41 | 13.04 | 10.92 | 10.99 | 7.41 |
| 90407 | 1 | 1 | 1 | 11.32 | 6.73 | 16.70 | 9.16 | 11.32 | 6.73 |
| 90420 | 1 | 1 | 1 | 8.65 | 6.37 | 16.75 | 7.85 | 8.65 | 6.37 |
| 90434 | 1 | 1 | 1 | 7.33 | 5.45 | 12.58 | 7.15 | 7.33 | 5.45 |
| 90468 | 1 | 1 | 1 | 8.60 | 5.38 | 12.46 | 8.64 | 8.60 | 5.38 |
| 90493 | 1 | 1 | 1 | 14.22 | 6.39 | 14.22 | 6.39 | 16.84 | 7.27 |
| 90494 | 3 | 1 | 1 | 9.14 | 5.20 | 14.46 | 5.31 | 9.14 | 5.20 |
| 90590 | 1 | 1 | 1 | 13.98 | 5.13 | 17.88 | 10.57 | 13.98 | 5.13 |

## 8. Movebank reference data: deployment date against first fix

Values are as stored in `data/raw/movebank_reference_data.csv`. Differences are first fix minus deploy-on-date.

| Bird | deploy-on-date | First fix, original file | First fix, after repair | Hours, original | Hours, after repair |
|---|---|---|---|---|---|
| 1 | 2013-10-13 14:20:00.000 | 2013-10-14 02:20:29 | 2013-10-14 02:20:29 | 12.01 | 12.01 |
| 2 | 2013-10-13 17:06:00.000 | 2013-10-14 05:06:05 | 2013-10-14 05:06:05 | 12.00 | 12.00 |
| 23058 | 2013-11-08 10:21:00.000 | 2013-11-08 22:21:54 | 2013-11-08 22:21:54 | 12.02 | 12.02 |
| 23059 | 2013-10-14 14:35:00.000 | 2013-10-15 02:35:36 | 2013-10-15 02:35:36 | 12.01 | 12.01 |
| 23096 | 2013-11-09 17:05:00.000 | 2013-11-10 05:05:40 | 2013-11-10 05:05:40 | 12.01 | 12.01 |
| 23782 | 2013-11-10 13:15:00.000 | 2013-11-11 01:15:15 | 2013-11-11 01:15:15 | 12.00 | 12.00 |
| 29155 | 2013-10-18 11:11:00.000 | 2013-10-18 23:11:28 | 2013-10-18 23:11:28 | 12.01 | 12.01 |
| 41269 | 2013-11-26 13:18:00.000 | 2013-11-27 01:18:35 | 2013-11-27 01:18:35 | 12.01 | 12.01 |
| 49364 | 2013-11-18 20:37:00.000 | 2013-11-19 08:37:28 | 2013-11-19 08:37:28 | 12.01 | 12.01 |
| 58565 | 2013-10-26 16:46:00.000 | 2013-10-27 04:46:44 | 2013-10-27 04:46:44 | 12.01 | 12.01 |
| 61696 | 2013-11-23 13:38:00.000 | 2013-11-24 01:38:25 | 2013-11-24 01:38:25 | 12.01 | 12.01 |
| 62093 | 2013-10-14 10:07:00.000 | 2013-10-14 22:07:20 | 2013-10-14 22:07:20 | 12.01 | 12.01 |
| 82589 | 2013-11-13 16:52:00.000 | 2013-11-14 04:52:07 | 2013-11-14 04:52:07 | 12.00 | 12.00 |
| 89518 | 2013-10-26 15:46:00.000 | 2013-10-27 03:46:41 | 2013-10-27 03:46:41 | 12.01 | 12.01 |
| 89570 | 2013-10-15 13:46:00.000 | 2013-10-16 01:46:20 | 2013-10-16 01:46:20 | 12.01 | 12.01 |
| 90282 | 2013-10-18 13:24:00.000 | 2013-10-19 01:24:53 | 2013-10-19 01:24:53 | 12.01 | 12.01 |
| 90287 | 2013-10-28 10:18:00.000 | 2013-10-28 22:18:21 | 2013-10-28 22:18:21 | 12.01 | 12.01 |
| 90407 | 2013-11-10 12:48:00.000 | 2013-11-11 00:48:16 | 2013-11-11 00:48:16 | 12.00 | 12.00 |
| 90420 | 2013-10-31 09:07:00.000 | 2013-10-31 21:07:15 | 2013-10-31 21:07:15 | 12.00 | 12.00 |
| 90434 | 2013-10-13 17:56:00.000 | 2013-10-14 05:56:36 | 2013-10-14 05:56:36 | 12.01 | 12.01 |
| 90468 | 2013-10-14 19:12:00.000 | 2013-10-17 05:32:00 | 2013-10-17 05:32:00 | 58.33 | 58.33 |
| 90493 | 2013-11-23 15:50:00.000 | 2013-11-24 03:50:53 | 2013-11-24 03:50:53 | 12.01 | 12.01 |
| 90494 | 2013-01-11 00:00:00.000 | 2013-01-11 00:00:00 | 2013-10-31 03:23:09 | 0.00 | 7,035.39 |
| 90590 | 2013-11-16 19:18:00.000 | 2013-11-17 07:18:00 | 2013-11-17 07:18:00 | 12.00 | 12.00 |
