# Evaluation Report: splink_v3_no_tf (holdout_3)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `1c4d07d45ecbe1ed...`
- **Selected $t_{\text{cost}}$**: `Weight = 7.75 (p = 0.995376)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9307** | 0.9506 | 0.9914 |
| **Recall** | **0.5391** | 0.5018 | 0.8882 |
| **F1 Score** | **0.6827** | 0.6568 | **0.9370** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.82%** |
| **False-Merge Clusters** | 35 |
| **False-Merged Records (Minority)** | 37 |
| **Split Persons** | 468 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 939.0 |
| **Clerical Review Load (per 10k records)** | 1752.8 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,855** | **4,194** | **3,716** | **+12.86%** |
| `club_formation` | 378 | 378 | 370 | +2.16% |
| `livelihood_support` | 2,208 | 2,135 | 2,135 | +0.00% |
| `microfinance_group` | 1,714 | 1,701 | 1,665 | +2.16% |
| `upg_enrolment` | 555 | 546 | 541 | +0.92% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,863 / 11,783,085
- **Reduction Ratio**: 99.6108%
- **Pair Completeness (Recall Ceiling)**: 88.72%
- **Pair Quality**: 2.75%
