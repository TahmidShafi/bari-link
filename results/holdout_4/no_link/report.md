# Evaluation Report: no_link (holdout_4)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `b5cc8efe54144b0a...`
- **Selected $t_{\text{cost}}$**: `Weight = 25.00 (p = 1.000000)`
- **Selected $t_{p99}$**: `Weight = -5.00 (p = 0.030303)`

> **Warning on $t_{\text{cost}}$**: Selected threshold lies on the grid boundary! The true optimum may lie outside the current grid range.

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **1.0000** | 1.0000 | 1.0000 |
| **Recall** | **0.0000** | 0.0000 | 0.7665 |
| **F1 Score** | **0.0000** | 0.0000 | **0.8678** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 0 |
| **False-Merged Records (Minority)** | 0 |
| **Split Persons** | 878 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,439.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,908** | **4,908** | **3,762** | **+30.46%** |
| `club_formation` | 392 | 392 | 380 | +3.16% |
| `livelihood_support` | 2,215 | 2,215 | 2,151 | +2.98% |
| `microfinance_group` | 1,751 | 1,751 | 1,691 | +3.55% |
| `upg_enrolment` | 550 | 550 | 540 | +1.85% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 12,041,778 / 12,041,778
- **Reduction Ratio**: 0.0000%
- **Pair Completeness (Recall Ceiling)**: 0.00%
- **Pair Quality**: 0.00%
