# Evaluation Report: phone (holdout_0)

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
| **Precision** | **0.8155** | 0.8155 | 0.9940 |
| **Recall** | **0.0933** | 0.0933 | 0.7812 |
| **F1 Score** | **0.1674** | 0.1674 | **0.8748** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 28 |
| **False-Merged Records (Minority)** | 28 |
| **Split Persons** | 799 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,487.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,798** | **4,640** | **3,634** | **+27.68%** |
| `club_formation` | 383 | 383 | 373 | +2.68% |
| `livelihood_support` | 2,160 | 2,144 | 2,105 | +1.85% |
| `microfinance_group` | 1,699 | 1,689 | 1,658 | +1.87% |
| `upg_enrolment` | 556 | 556 | 540 | +2.96% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,312,311 / 11,508,003
- **Reduction Ratio**: 79.9069%
- **Pair Completeness (Recall Ceiling)**: 9.33%
- **Pair Quality**: 0.01%
