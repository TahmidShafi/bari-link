# Evaluation Report: exact_or_phone (holdout_2)

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
| **Precision** | **0.8854** | 0.8941 | 0.9928 |
| **Recall** | **0.2150** | 0.2116 | 0.8165 |
| **F1 Score** | **0.3460** | 0.3421 | **0.8960** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **13.33%** |
| **False-Merge Clusters** | 33 |
| **False-Merged Records (Minority)** | 33 |
| **Split Persons** | 709 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,328.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,866** | **4,561** | **3,731** | **+22.25%** |
| `club_formation` | 397 | 395 | 381 | +3.67% |
| `livelihood_support` | 2,200 | 2,163 | 2,133 | +1.41% |
| `microfinance_group` | 1,714 | 1,696 | 1,667 | +1.74% |
| `upg_enrolment` | 555 | 553 | 540 | +2.41% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,361,049 / 11,836,545
- **Reduction Ratio**: 80.0529%
- **Pair Completeness (Recall Ceiling)**: 21.16%
- **Pair Quality**: 0.01%
