# Evaluation Report: no_link (holdout_1)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `4a590d2aadc7307b...`
- **Selected $t_{\text{cost}}$**: `Weight = 25.00 (p = 1.000000)`
- **Selected $t_{p99}$**: `none`

> **Warning on $t_{\text{cost}}$**: Selected threshold lies on the grid boundary! The true optimum may lie outside the current grid range.

> **Note on $t_{p99}$**: No pairs predicted; t_p99 is undefined.

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **1.0000** | 1.0000 | 1.0000 |
| **Recall** | **0.0000** | 0.0000 | 0.7610 |
| **F1 Score** | **0.0000** | 0.0000 | **0.8643** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 0 |
| **False-Merged Records (Minority)** | 0 |
| **Split Persons** | 863 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,475.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,832** | **4,832** | **3,677** | **+31.41%** |
| `club_formation` | 388 | 388 | 374 | +3.74% |
| `livelihood_support` | 2,178 | 2,178 | 2,123 | +2.59% |
| `microfinance_group` | 1,705 | 1,705 | 1,659 | +2.77% |
| `upg_enrolment` | 561 | 561 | 540 | +3.89% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 11,671,696 / 11,671,696
- **Reduction Ratio**: 0.0000%
- **Pair Completeness (Recall Ceiling)**: 0.00%
- **Pair Quality**: 0.00%
