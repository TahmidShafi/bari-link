# Evaluation Report: splink_v3_1 (holdout_9)

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
| **Precision** | **0.9591** | 0.9652 | 0.9948 |
| **Recall** | **0.4738** | 0.4482 | 0.8692 |
| **F1 Score** | **0.6342** | 0.6121 | **0.9278** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 22 |
| **False-Merged Records (Minority)** | 24 |
| **Split Persons** | 526 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 932.0 |
| **Clerical Review Load (per 10k records)** | 1759.5 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,814** | **4,189** | **3,624** | **+15.59%** |
| `club_formation` | 377 | 377 | 369 | +2.17% |
| `livelihood_support` | 2,172 | 2,100 | 2,098 | +0.10% |
| `microfinance_group` | 1,704 | 1,691 | 1,649 | +2.55% |
| `upg_enrolment` | 561 | 550 | 540 | +1.85% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,750 / 11,584,891
- **Reduction Ratio**: 99.6051%
- **Pair Completeness (Recall Ceiling)**: 88.56%
- **Pair Quality**: 2.88%
