# Evaluation Report: splink_v3_no_kinship (holdout_3)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `6a46c7aeeed1d046...`
- **Selected $t_{\text{cost}}$**: `Weight = 1.25 (p = 0.704003)`
- **Selected $t_{p99}$**: `Weight = 9.25 (p = 0.998360)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9278** | 0.9474 | 0.9896 |
| **Recall** | **0.6342** | 0.5962 | 0.9110 |
| **F1 Score** | **0.7535** | 0.7318 | **0.9487** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.82%** |
| **False-Merge Clusters** | 42 |
| **False-Merged Records (Minority)** | 45 |
| **Split Persons** | 376 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 869.0 |
| **Clerical Review Load (per 10k records)** | 195.7 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,855** | **4,079** | **3,716** | **+9.77%** |
| `club_formation` | 378 | 375 | 370 | +1.35% |
| `livelihood_support` | 2,208 | 2,133 | 2,135 | -0.09% |
| `microfinance_group` | 1,714 | 1,674 | 1,665 | +0.54% |
| `upg_enrolment` | 555 | 546 | 541 | +0.92% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,863 / 11,783,085
- **Reduction Ratio**: 99.6108%
- **Pair Completeness (Recall Ceiling)**: 88.72%
- **Pair Quality**: 2.75%
