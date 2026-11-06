# Evaluation Report: exact_or_phone (holdout_3)

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
| **Precision** | **0.7867** | 0.8007 | 0.9892 |
| **Recall** | **0.1586** | 0.1557 | 0.8021 |
| **F1 Score** | **0.2639** | 0.2608 | **0.8859** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **3.64%** |
| **False-Merge Clusters** | 48 |
| **False-Merged Records (Minority)** | 50 |
| **Split Persons** | 768 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,499.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,855** | **4,601** | **3,716** | **+23.82%** |
| `club_formation` | 378 | 377 | 370 | +1.89% |
| `livelihood_support` | 2,208 | 2,181 | 2,135 | +2.15% |
| `microfinance_group` | 1,714 | 1,700 | 1,665 | +2.10% |
| `upg_enrolment` | 555 | 551 | 541 | +1.85% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,359,648 / 11,783,085
- **Reduction Ratio**: 79.9743%
- **Pair Completeness (Recall Ceiling)**: 15.57%
- **Pair Quality**: 0.01%
