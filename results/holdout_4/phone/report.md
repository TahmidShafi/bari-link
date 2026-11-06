# Evaluation Report: phone (holdout_4)

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
| **Precision** | **0.7200** | 0.7200 | 0.9928 |
| **Recall** | **0.0751** | 0.0751 | 0.7850 |
| **F1 Score** | **0.1359** | 0.1359 | **0.8767** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 32 |
| **False-Merged Records (Minority)** | 33 |
| **Split Persons** | 811 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,541.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,908** | **4,774** | **3,762** | **+26.90%** |
| `club_formation` | 392 | 392 | 380 | +3.16% |
| `livelihood_support` | 2,215 | 2,193 | 2,151 | +1.95% |
| `microfinance_group` | 1,751 | 1,740 | 1,691 | +2.90% |
| `upg_enrolment` | 550 | 550 | 540 | +1.85% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,444,748 / 12,041,778
- **Reduction Ratio**: 79.6978%
- **Pair Completeness (Recall Ceiling)**: 7.51%
- **Pair Quality**: 0.00%
