# Evaluation Report: exact_or_phone (holdout_1)

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
| **Precision** | **0.8858** | 0.8953 | 0.9939 |
| **Recall** | **0.1736** | 0.1681 | 0.8035 |
| **F1 Score** | **0.2902** | 0.2831 | **0.8886** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **5.81%** |
| **False-Merge Clusters** | 28 |
| **False-Merged Records (Minority)** | 28 |
| **Split Persons** | 725 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,384.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,832** | **4,574** | **3,677** | **+24.39%** |
| `club_formation` | 388 | 387 | 374 | +3.48% |
| `livelihood_support` | 2,178 | 2,156 | 2,123 | +1.55% |
| `microfinance_group` | 1,705 | 1,691 | 1,659 | +1.93% |
| `upg_enrolment` | 561 | 558 | 540 | +3.33% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,313,980 / 11,671,696
- **Reduction Ratio**: 80.1744%
- **Pair Completeness (Recall Ceiling)**: 16.81%
- **Pair Quality**: 0.01%
