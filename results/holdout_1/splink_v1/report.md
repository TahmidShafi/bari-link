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
| **Precision** | **0.6306** | 0.7134 | 0.9227 |
| **Recall** | **0.7546** | 0.7105 | 0.9396 |
| **F1 Score** | **0.6870** | 0.7120 | **0.9311** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **19.77%** |
| **False-Merge Clusters** | 245 |
| **False-Merged Records (Minority)** | 332 |
| **Split Persons** | 254 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 3,622.0 |
| **Clerical Review Load (per 10k records)** | 6868.8 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,832** | **3,639** | **3,677** | **-1.03%** |
| `club_formation` | 388 | 375 | 374 | +0.27% |
| `livelihood_support` | 2,178 | 1,994 | 2,123 | -6.08% |
| `microfinance_group` | 1,705 | 1,609 | 1,659 | -3.01% |
| `upg_enrolment` | 561 | 539 | 540 | -0.19% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,322 / 11,671,696
- **Reduction Ratio**: 99.6031%
- **Pair Completeness (Recall Ceiling)**: 89.56%
- **Pair Quality**: 2.85%
