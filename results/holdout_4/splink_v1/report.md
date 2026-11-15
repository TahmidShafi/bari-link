# Evaluation Report: splink_v1 (holdout_4)

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
| **Precision** | **0.9331** | 0.9412 | 0.9924 |
| **Recall** | **0.4364** | 0.4003 | 0.8663 |
| **F1 Score** | **0.5947** | 0.5617 | **0.9251** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 33 |
| **False-Merged Records (Minority)** | 35 |
| **Split Persons** | 551 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,036.0 |
| **Clerical Review Load (per 10k records)** | 2277.9 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,908** | **4,347** | **3,762** | **+15.55%** |
| `club_formation` | 392 | 392 | 380 | +3.16% |
| `livelihood_support` | 2,215 | 2,138 | 2,151 | -0.60% |
| `microfinance_group` | 1,751 | 1,736 | 1,691 | +2.66% |
| `upg_enrolment` | 550 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,653 / 12,041,778
- **Reduction Ratio**: 99.6126%
- **Pair Completeness (Recall Ceiling)**: 89.44%
- **Pair Quality**: 2.76%
