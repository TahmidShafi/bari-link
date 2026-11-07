# Evaluation Report: splink_k (holdout_5)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `95a50ae901ef905a...`
- **Selected $t_{\text{cost}}$**: `Weight = 1.25 (p = 0.704003)`
- **Selected $t_{p99}$**: `Weight = 9.25 (p = 0.998360)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9406** | 0.9596 | 0.9914 |
| **Recall** | **0.6260** | 0.5926 | 0.9094 |
| **F1 Score** | **0.7517** | 0.7327 | **0.9486** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.27%** |
| **False-Merge Clusters** | 34 |
| **False-Merged Records (Minority)** | 38 |
| **Split Persons** | 374 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 824.0 |
| **Clerical Review Load (per 10k records)** | 121.9 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,841** | **4,061** | **3,689** | **+10.08%** |
| `club_formation` | 385 | 383 | 380 | +0.79% |
| `livelihood_support` | 2,186 | 2,118 | 2,122 | -0.19% |
| `microfinance_group` | 1,718 | 1,687 | 1,671 | +0.96% |
| `upg_enrolment` | 552 | 542 | 540 | +0.37% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,788 / 11,715,220
- **Reduction Ratio**: 99.6006%
- **Pair Completeness (Recall Ceiling)**: 89.04%
- **Pair Quality**: 2.74%
