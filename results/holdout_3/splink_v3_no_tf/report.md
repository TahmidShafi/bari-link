# Evaluation Report: splink_v3_no_tf (holdout_3)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `a4f11e5e12edad3f...`
- **Selected $t_{\text{cost}}$**: `Weight = 7.75 (p = 0.995376)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9274** | 0.9494 | 0.9911 |
| **Recall** | **0.5405** | 0.5025 | 0.8884 |
| **F1 Score** | **0.6830** | 0.6571 | **0.9370** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.82%** |
| **False-Merge Clusters** | 36 |
| **False-Merged Records (Minority)** | 38 |
| **Split Persons** | 467 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 952.0 |
| **Clerical Review Load (per 10k records)** | 1744.6 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,855** | **4,192** | **3,716** | **+12.81%** |
| `club_formation` | 378 | 378 | 370 | +2.16% |
| `livelihood_support` | 2,208 | 2,135 | 2,135 | +0.00% |
| `microfinance_group` | 1,714 | 1,700 | 1,665 | +2.10% |
| `upg_enrolment` | 555 | 546 | 541 | +0.92% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,863 / 11,783,085
- **Reduction Ratio**: 99.6108%
- **Pair Completeness (Recall Ceiling)**: 88.72%
- **Pair Quality**: 2.75%
