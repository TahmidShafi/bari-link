# Evaluation Report: splink_v3 (holdout_3)

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
| **Precision** | **0.9406** | 0.9506 | 0.9922 |
| **Recall** | **0.5243** | 0.4884 | 0.8849 |
| **F1 Score** | **0.6733** | 0.6453 | **0.9354** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.82%** |
| **False-Merge Clusters** | 34 |
| **False-Merged Records (Minority)** | 34 |
| **Split Persons** | 480 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 910.0 |
| **Clerical Review Load (per 10k records)** | 1794.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,855** | **4,210** | **3,716** | **+13.29%** |
| `club_formation` | 378 | 377 | 370 | +1.89% |
| `livelihood_support` | 2,208 | 2,136 | 2,135 | +0.05% |
| `microfinance_group` | 1,714 | 1,700 | 1,665 | +2.10% |
| `upg_enrolment` | 555 | 545 | 541 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,863 / 11,783,085
- **Reduction Ratio**: 99.6108%
- **Pair Completeness (Recall Ceiling)**: 88.72%
- **Pair Quality**: 2.75%
