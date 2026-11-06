# Evaluation Report: phone (holdout_1)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `1352fa9e86978a46...`
- **Selected $t_{\text{cost}}$**: `Weight = 25.00 (p = 1.000000)`
- **Selected $t_{p99}$**: `none`

> **Warning on $t_{\text{cost}}$**: Selected threshold lies on the grid boundary! The true optimum may lie outside the current grid range.

> **Note on $t_{p99}$**: No threshold achieves cluster-level precision >= 0.99 (maximum observed: 0.8531)

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.8377** | 0.8377 | 0.9950 |
| **Recall** | **0.0875** | 0.0875 | 0.7827 |
| **F1 Score** | **0.1584** | 0.1584 | **0.8761** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 24 |
| **False-Merged Records (Minority)** | 24 |
| **Split Persons** | 791 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,471.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,832** | **4,692** | **3,677** | **+27.60%** |
| `club_formation` | 388 | 388 | 374 | +3.74% |
| `livelihood_support` | 2,178 | 2,158 | 2,123 | +1.65% |
| `microfinance_group` | 1,705 | 1,696 | 1,659 | +2.23% |
| `upg_enrolment` | 561 | 560 | 540 | +3.70% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,313,980 / 11,671,696
- **Reduction Ratio**: 80.1744%
- **Pair Completeness (Recall Ceiling)**: 8.75%
- **Pair Quality**: 0.01%
