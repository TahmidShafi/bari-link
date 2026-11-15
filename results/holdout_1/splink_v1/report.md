# Evaluation Report: splink_v1 (holdout_1)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `4e303cd4a82445ed...`
- **Selected $t_{\text{cost}}$**: `Weight = 9.25 (p = 0.998360)`
- **Selected $t_{p99}$**: `Weight = 16.75 (p = 0.999991)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9103** | 0.9272 | 0.9899 |
| **Recall** | **0.4264** | 0.3885 | 0.8606 |
| **F1 Score** | **0.5808** | 0.5475 | **0.9207** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.65%** |
| **False-Merge Clusters** | 43 |
| **False-Merged Records (Minority)** | 44 |
| **Split Persons** | 554 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,156.0 |
| **Clerical Review Load (per 10k records)** | 2235.1 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,832** | **4,268** | **3,677** | **+16.07%** |
| `club_formation` | 388 | 385 | 374 | +2.94% |
| `livelihood_support` | 2,178 | 2,104 | 2,123 | -0.89% |
| `microfinance_group` | 1,705 | 1,689 | 1,659 | +1.81% |
| `upg_enrolment` | 561 | 546 | 540 | +1.11% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,322 / 11,671,696
- **Reduction Ratio**: 99.6031%
- **Pair Completeness (Recall Ceiling)**: 89.56%
- **Pair Quality**: 2.85%
