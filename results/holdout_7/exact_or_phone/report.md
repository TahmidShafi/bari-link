# Evaluation Report: exact_or_phone (holdout_7)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `52eb336c3530ae59...`
- **Selected $t_{\text{cost}}$**: `Weight = 25.00 (p = 1.000000)`
- **Selected $t_{p99}$**: `none`

> **Warning on $t_{\text{cost}}$**: Selected threshold lies on the grid boundary! The true optimum may lie outside the current grid range.

> **Note on $t_{p99}$**: No threshold achieves cluster-level precision >= 0.99 (maximum observed: 0.8860)

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.7951** | 0.8116 | 0.9902 |
| **Recall** | **0.1633** | 0.1598 | 0.8052 |
| **F1 Score** | **0.2710** | 0.2670 | **0.8882** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.12%** |
| **False-Merge Clusters** | 41 |
| **False-Merged Records (Minority)** | 44 |
| **Split Persons** | 744 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,468.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,837** | **4,585** | **3,706** | **+23.72%** |
| `club_formation` | 399 | 398 | 384 | +3.65% |
| `livelihood_support` | 2,165 | 2,134 | 2,103 | +1.47% |
| `microfinance_group` | 1,716 | 1,696 | 1,665 | +1.86% |
| `upg_enrolment` | 557 | 551 | 540 | +2.04% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,297,065 / 11,695,866
- **Reduction Ratio**: 80.3600%
- **Pair Completeness (Recall Ceiling)**: 15.98%
- **Pair Quality**: 0.01%
