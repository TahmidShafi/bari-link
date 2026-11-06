# Evaluation Report: no_link (holdout_2)

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
| **Recall** | **0.0000** | 0.0000 | 0.7667 |
| **F1 Score** | **0.0000** | 0.0000 | **0.8680** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 0 |
| **False-Merged Records (Minority)** | 0 |
| **Split Persons** | 865 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,437.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,866** | **4,866** | **3,731** | **+30.42%** |
| `club_formation` | 397 | 397 | 381 | +4.20% |
| `livelihood_support` | 2,200 | 2,200 | 2,133 | +3.14% |
| `microfinance_group` | 1,714 | 1,714 | 1,667 | +2.82% |
| `upg_enrolment` | 555 | 555 | 540 | +2.78% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 11,836,545 / 11,836,545
- **Reduction Ratio**: 0.0000%
- **Pair Completeness (Recall Ceiling)**: 0.00%
- **Pair Quality**: 0.00%
