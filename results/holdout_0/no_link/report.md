# Evaluation Report: no_link (holdout_0)

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
| **Recall** | **0.0000** | 0.0000 | 0.7574 |
| **F1 Score** | **0.0000** | 0.0000 | **0.8620** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 0 |
| **False-Merged Records (Minority)** | 0 |
| **Split Persons** | 877 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,469.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,798** | **4,798** | **3,634** | **+32.03%** |
| `club_formation` | 383 | 383 | 373 | +2.68% |
| `livelihood_support` | 2,160 | 2,160 | 2,105 | +2.61% |
| `microfinance_group` | 1,699 | 1,699 | 1,658 | +2.47% |
| `upg_enrolment` | 556 | 556 | 540 | +2.96% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 11,508,003 / 11,508,003
- **Reduction Ratio**: 0.0000%
- **Pair Completeness (Recall Ceiling)**: 0.00%
- **Pair Quality**: 0.00%
