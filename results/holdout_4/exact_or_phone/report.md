# Evaluation Report: exact_or_phone (holdout_4)

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
| **Precision** | **0.8454** | 0.8528 | 0.9922 |
| **Recall** | **0.1786** | 0.1772 | 0.8092 |
| **F1 Score** | **0.2949** | 0.2934 | **0.8914** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.25%** |
| **False-Merge Clusters** | 34 |
| **False-Merged Records (Minority)** | 35 |
| **Split Persons** | 734 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,417.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,908** | **4,637** | **3,762** | **+23.26%** |
| `club_formation` | 392 | 391 | 380 | +2.89% |
| `livelihood_support` | 2,215 | 2,186 | 2,151 | +1.63% |
| `microfinance_group` | 1,751 | 1,727 | 1,691 | +2.13% |
| `upg_enrolment` | 550 | 549 | 540 | +1.67% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,444,748 / 12,041,778
- **Reduction Ratio**: 79.6978%
- **Pair Completeness (Recall Ceiling)**: 17.72%
- **Pair Quality**: 0.01%
