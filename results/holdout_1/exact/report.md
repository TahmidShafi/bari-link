# Evaluation Report: exact (holdout_1)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `fd0c101a41f62d94...`
- **Selected $t_{\text{cost}}$**: `Weight = 25.00 (p = 1.000000)`
- **Selected $t_{p99}$**: `none`

> **Warning on $t_{\text{cost}}$**: Selected threshold lies on the grid boundary! The true optimum may lie outside the current grid range.

> **Note on $t_{p99}$**: No threshold achieves cluster-level precision >= 0.99 (maximum observed: 0.9648)

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9706** | 0.9706 | 0.9992 |
| **Recall** | **0.0895** | 0.0895 | 0.7832 |
| **F1 Score** | **0.1639** | 0.1639 | **0.8781** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **5.81%** |
| **False-Merge Clusters** | 4 |
| **False-Merged Records (Minority)** | 4 |
| **Split Persons** | 795 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,363.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,832** | **4,701** | **3,677** | **+27.85%** |
| `club_formation` | 388 | 387 | 374 | +3.48% |
| `livelihood_support` | 2,178 | 2,173 | 2,123 | +2.36% |
| `microfinance_group` | 1,705 | 1,700 | 1,659 | +2.47% |
| `upg_enrolment` | 561 | 560 | 540 | +3.70% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,313,980 / 11,671,696
- **Reduction Ratio**: 80.1744%
- **Pair Completeness (Recall Ceiling)**: 8.95%
- **Pair Quality**: 0.01%
