# Evaluation Report: exact (holdout_4)

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
| **Precision** | **0.9875** | 0.9875 | 0.9996 |
| **Recall** | **0.1098** | 0.1098 | 0.7924 |
| **F1 Score** | **0.1976** | 0.1976 | **0.8840** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.25%** |
| **False-Merge Clusters** | 2 |
| **False-Merged Records (Minority)** | 2 |
| **Split Persons** | 796 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,291.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,908** | **4,760** | **3,762** | **+26.53%** |
| `club_formation` | 392 | 391 | 380 | +2.89% |
| `livelihood_support` | 2,215 | 2,208 | 2,151 | +2.65% |
| `microfinance_group` | 1,751 | 1,736 | 1,691 | +2.66% |
| `upg_enrolment` | 550 | 549 | 540 | +1.67% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,444,748 / 12,041,778
- **Reduction Ratio**: 79.6978%
- **Pair Completeness (Recall Ceiling)**: 10.98%
- **Pair Quality**: 0.01%
