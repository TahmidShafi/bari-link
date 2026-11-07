# Evaluation Report: splink_v3 (holdout_1)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `5b19102078e953a8...`
- **Selected $t_{\text{cost}}$**: `Weight = 8.00 (p = 0.996109)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9432** | 0.9549 | 0.9932 |
| **Recall** | **0.5064** | 0.4590 | 0.8787 |
| **F1 Score** | **0.6590** | 0.6200 | **0.9324** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.65%** |
| **False-Merge Clusters** | 28 |
| **False-Merged Records (Minority)** | 29 |
| **Split Persons** | 490 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 953.0 |
| **Clerical Review Load (per 10k records)** | 1891.6 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,832** | **4,199** | **3,677** | **+14.20%** |
| `club_formation` | 388 | 385 | 374 | +2.94% |
| `livelihood_support` | 2,178 | 2,121 | 2,123 | -0.09% |
| `microfinance_group` | 1,705 | 1,686 | 1,659 | +1.63% |
| `upg_enrolment` | 561 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,322 / 11,671,696
- **Reduction Ratio**: 99.6031%
- **Pair Completeness (Recall Ceiling)**: 89.56%
- **Pair Quality**: 2.85%
