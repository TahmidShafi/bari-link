# Evaluation Report: splink_k (holdout_9)

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
| **Precision** | **0.9697** | 0.9750 | 0.9953 |
| **Recall** | **0.5808** | 0.5518 | 0.8963 |
| **F1 Score** | **0.7264** | 0.7048 | **0.9432** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 21 |
| **False-Merged Records (Minority)** | 21 |
| **Split Persons** | 418 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 758.0 |
| **Clerical Review Load (per 10k records)** | 209.8 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,814** | **4,066** | **3,624** | **+12.20%** |
| `club_formation` | 377 | 376 | 369 | +1.90% |
| `livelihood_support` | 2,172 | 2,107 | 2,098 | +0.43% |
| `microfinance_group` | 1,704 | 1,669 | 1,649 | +1.21% |
| `upg_enrolment` | 561 | 549 | 540 | +1.67% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,750 / 11,584,891
- **Reduction Ratio**: 99.6051%
- **Pair Completeness (Recall Ceiling)**: 88.56%
- **Pair Quality**: 2.88%
