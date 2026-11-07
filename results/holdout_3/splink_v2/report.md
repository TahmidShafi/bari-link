# Evaluation Report: splink_v2 (holdout_3)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `bf3eb6e3610b6dc7...`
- **Selected $t_{\text{cost}}$**: `Weight = 9.25 (p = 0.998360)`
- **Selected $t_{p99}$**: `Weight = 17.25 (p = 0.999994)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9029** | 0.9240 | 0.9876 |
| **Recall** | **0.5180** | 0.4715 | 0.8828 |
| **F1 Score** | **0.6583** | 0.6244 | **0.9322** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.82%** |
| **False-Merge Clusters** | 51 |
| **False-Merged Records (Minority)** | 55 |
| **Split Persons** | 493 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,079.0 |
| **Clerical Review Load (per 10k records)** | 2105.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,855** | **4,199** | **3,716** | **+13.00%** |
| `club_formation` | 378 | 377 | 370 | +1.89% |
| `livelihood_support` | 2,208 | 2,111 | 2,135 | -1.12% |
| `microfinance_group` | 1,714 | 1,701 | 1,665 | +2.16% |
| `upg_enrolment` | 555 | 544 | 541 | +0.55% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,863 / 11,783,085
- **Reduction Ratio**: 99.6108%
- **Pair Completeness (Recall Ceiling)**: 88.72%
- **Pair Quality**: 2.75%
