# Evaluation Report: splink_v1 (holdout_1)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `572b85d2140740f8...`
- **Selected $t_{\text{cost}}$**: `Weight = 9.00 (p = 0.998051)`
- **Selected $t_{p99}$**: `Weight = 15.50 (p = 0.999978)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9289** | 0.9437 | 0.9920 |
| **Recall** | **0.4692** | 0.4203 | 0.8697 |
| **F1 Score** | **0.6234** | 0.5816 | **0.9268** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.65%** |
| **False-Merge Clusters** | 32 |
| **False-Merged Records (Minority)** | 35 |
| **Split Persons** | 523 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,048.0 |
| **Clerical Review Load (per 10k records)** | 2044.7 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,832** | **4,237** | **3,677** | **+15.23%** |
| `club_formation` | 388 | 385 | 374 | +2.94% |
| `livelihood_support` | 2,178 | 2,110 | 2,123 | -0.61% |
| `microfinance_group` | 1,705 | 1,689 | 1,659 | +1.81% |
| `upg_enrolment` | 561 | 546 | 540 | +1.11% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,322 / 11,671,696
- **Reduction Ratio**: 99.6031%
- **Pair Completeness (Recall Ceiling)**: 89.56%
- **Pair Quality**: 2.85%
