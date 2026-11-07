# Evaluation Report: exact_or_phone (holdout_6)

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
| **Precision** | **0.8456** | 0.8571 | 0.9918 |
| **Recall** | **0.1762** | 0.1720 | 0.8090 |
| **F1 Score** | **0.2917** | 0.2865 | **0.8911** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **14.29%** |
| **False-Merge Clusters** | 37 |
| **False-Merged Records (Minority)** | 37 |
| **Split Persons** | 712 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,408.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,836** | **4,564** | **3,702** | **+23.28%** |
| `club_formation` | 380 | 379 | 368 | +2.99% |
| `livelihood_support` | 2,174 | 2,153 | 2,120 | +1.56% |
| `microfinance_group` | 1,723 | 1,703 | 1,674 | +1.73% |
| `upg_enrolment` | 559 | 557 | 540 | +3.15% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,372,875 / 11,691,030
- **Reduction Ratio**: 79.7035%
- **Pair Completeness (Recall Ceiling)**: 17.20%
- **Pair Quality**: 0.01%
