# Evaluation Report: phone (holdout_3)

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
| **Precision** | **0.6748** | 0.6748 | 0.9899 |
| **Recall** | **0.0775** | 0.0775 | 0.7836 |
| **F1 Score** | **0.1391** | 0.1391 | **0.8748** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.82%** |
| **False-Merge Clusters** | 46 |
| **False-Merged Records (Minority)** | 48 |
| **Split Persons** | 820 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,574.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,855** | **4,708** | **3,716** | **+26.70%** |
| `club_formation` | 378 | 378 | 370 | +2.16% |
| `livelihood_support` | 2,208 | 2,185 | 2,135 | +2.34% |
| `microfinance_group` | 1,714 | 1,706 | 1,665 | +2.46% |
| `upg_enrolment` | 555 | 553 | 541 | +2.22% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,359,648 / 11,783,085
- **Reduction Ratio**: 79.9743%
- **Pair Completeness (Recall Ceiling)**: 7.75%
- **Pair Quality**: 0.00%
