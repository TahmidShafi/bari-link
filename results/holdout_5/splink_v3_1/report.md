# Evaluation Report: splink_v3_1 (holdout_5)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `899e42fd581546ea...`
- **Selected $t_{\text{cost}}$**: `Weight = 8.00 (p = 0.996109)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9553** | 0.9650 | 0.9940 |
| **Recall** | **0.5344** | 0.4969 | 0.8862 |
| **F1 Score** | **0.6854** | 0.6560 | **0.9370** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 26 |
| **False-Merged Records (Minority)** | 27 |
| **Split Persons** | 468 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 851.0 |
| **Clerical Review Load (per 10k records)** | 1855.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,841** | **4,180** | **3,689** | **+13.31%** |
| `club_formation` | 385 | 385 | 380 | +1.32% |
| `livelihood_support` | 2,186 | 2,120 | 2,122 | -0.09% |
| `microfinance_group` | 1,718 | 1,704 | 1,671 | +1.97% |
| `upg_enrolment` | 552 | 543 | 540 | +0.56% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,788 / 11,715,220
- **Reduction Ratio**: 99.6006%
- **Pair Completeness (Recall Ceiling)**: 89.04%
- **Pair Quality**: 2.74%
