# Evaluation Report: splink_v3 (holdout_3)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `e4bdaee9d038dfc0...`
- **Selected $t_{\text{cost}}$**: `Weight = 8.00 (p = 0.996109)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9442** | 0.9519 | 0.9925 |
| **Recall** | **0.5243** | 0.4877 | 0.8849 |
| **F1 Score** | **0.6742** | 0.6449 | **0.9356** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.82%** |
| **False-Merge Clusters** | 33 |
| **False-Merged Records (Minority)** | 33 |
| **Split Persons** | 480 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 895.0 |
| **Clerical Review Load (per 10k records)** | 1798.1 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,855** | **4,211** | **3,716** | **+13.32%** |
| `club_formation` | 378 | 377 | 370 | +1.89% |
| `livelihood_support` | 2,208 | 2,136 | 2,135 | +0.05% |
| `microfinance_group` | 1,714 | 1,701 | 1,665 | +2.16% |
| `upg_enrolment` | 555 | 545 | 541 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,863 / 11,783,085
- **Reduction Ratio**: 99.6108%
- **Pair Completeness (Recall Ceiling)**: 88.72%
- **Pair Quality**: 2.75%
