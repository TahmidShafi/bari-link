# Evaluation Report: no_link (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `select`
- **Threshold Grid**: `weight`
- **Selected $t_{\text{cost}}$**: `Weight = 25.00 (p = 1.000000)`
- **Selected $t_{p99}$**: `Weight = -5.00 (p = 0.030303)`

> **Warning on $t_{\text{cost}}$**: Selected threshold lies on the grid boundary! The true optimum may lie outside the current grid range.

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **1.0000** | 1.0000 | 1.0000 |
| **Recall** | **0.0000** | 0.0000 | 0.7630 |
| **F1 Score** | **0.0000** | 0.0000 | **0.8656** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 0 |
| **False-Merged Records (Minority)** | 0 |
| **Split Persons** | 877 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,424.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,806** | **4,806** | **3,667** | **+31.06%** |
| `club_formation` | 365 | 365 | 353 | +3.40% |
| `livelihood_support` | 2,179 | 2,179 | 2,109 | +3.32% |
| `microfinance_group` | 1,709 | 1,709 | 1,659 | +3.01% |
| `upg_enrolment` | 553 | 553 | 540 | +2.41% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 11,546,415 / 11,546,415
- **Reduction Ratio**: 0.0000%
- **Pair Completeness (Recall Ceiling)**: 0.00%
- **Pair Quality**: 0.00%
