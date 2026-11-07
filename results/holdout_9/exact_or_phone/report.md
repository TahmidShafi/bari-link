# Evaluation Report: exact_or_phone (holdout_9)

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
| **Precision** | **0.9023** | 0.9011 | 0.9947 |
| **Recall** | **0.1615** | 0.1595 | 0.7931 |
| **F1 Score** | **0.2740** | 0.2710 | **0.8826** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.28%** |
| **False-Merge Clusters** | 25 |
| **False-Merged Records (Minority)** | 25 |
| **Split Persons** | 786 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,376.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,814** | **4,568** | **3,624** | **+26.05%** |
| `club_formation` | 377 | 377 | 369 | +2.17% |
| `livelihood_support` | 2,172 | 2,150 | 2,098 | +2.48% |
| `microfinance_group` | 1,704 | 1,684 | 1,649 | +2.12% |
| `upg_enrolment` | 561 | 559 | 540 | +3.52% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,313,165 / 11,584,891
- **Reduction Ratio**: 80.0329%
- **Pair Completeness (Recall Ceiling)**: 15.95%
- **Pair Quality**: 0.01%
