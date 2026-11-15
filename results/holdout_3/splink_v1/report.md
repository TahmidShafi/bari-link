# Evaluation Report: splink_v1 (holdout_3)

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
| **Precision** | **0.9166** | 0.9357 | 0.9904 |
| **Recall** | **0.4644** | 0.4207 | 0.8714 |
| **F1 Score** | **0.6165** | 0.5805 | **0.9271** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.82%** |
| **False-Merge Clusters** | 40 |
| **False-Merged Records (Minority)** | 42 |
| **Split Persons** | 529 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,060.0 |
| **Clerical Review Load (per 10k records)** | 2187.4 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,855** | **4,266** | **3,716** | **+14.80%** |
| `club_formation` | 378 | 377 | 370 | +1.89% |
| `livelihood_support` | 2,208 | 2,120 | 2,135 | -0.70% |
| `microfinance_group` | 1,714 | 1,703 | 1,665 | +2.28% |
| `upg_enrolment` | 555 | 545 | 541 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,863 / 11,783,085
- **Reduction Ratio**: 99.6108%
- **Pair Completeness (Recall Ceiling)**: 88.72%
- **Pair Quality**: 2.75%
