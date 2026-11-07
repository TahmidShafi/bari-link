# Evaluation Report: no_link (holdout_3)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `4a590d2aadc7307b...`
- **Selected $t_{\text{cost}}$**: `Weight = 25.00 (p = 1.000000)`
- **Selected $t_{p99}$**: `none`

> **Warning on $t_{\text{cost}}$**: Selected threshold lies on the grid boundary! The true optimum may lie outside the current grid range.

> **Note on $t_{p99}$**: No pairs predicted; t_p99 is undefined.

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **1.0000** | 1.0000 | 1.0000 |
| **Recall** | **0.0000** | 0.0000 | 0.7654 |
| **F1 Score** | **0.0000** | 0.0000 | **0.8671** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 0 |
| **False-Merged Records (Minority)** | 0 |
| **Split Persons** | 878 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,419.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,855** | **4,855** | **3,716** | **+30.65%** |
| `club_formation` | 378 | 378 | 370 | +2.16% |
| `livelihood_support` | 2,208 | 2,208 | 2,135 | +3.42% |
| `microfinance_group` | 1,714 | 1,714 | 1,665 | +2.94% |
| `upg_enrolment` | 555 | 555 | 541 | +2.59% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 11,783,085 / 11,783,085
- **Reduction Ratio**: 0.0000%
- **Pair Completeness (Recall Ceiling)**: 0.00%
- **Pair Quality**: 0.00%
