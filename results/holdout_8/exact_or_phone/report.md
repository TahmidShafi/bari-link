# Evaluation Report: exact_or_phone (holdout_8)

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
| **Precision** | **0.8513** | 0.8553 | 0.9914 |
| **Recall** | **0.1908** | 0.1844 | 0.8100 |
| **F1 Score** | **0.3117** | 0.3034 | **0.8916** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.76%** |
| **False-Merge Clusters** | 38 |
| **False-Merged Records (Minority)** | 40 |
| **Split Persons** | 734 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,376.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,838** | **4,559** | **3,705** | **+23.05%** |
| `club_formation` | 391 | 391 | 377 | +3.71% |
| `livelihood_support` | 2,178 | 2,157 | 2,124 | +1.55% |
| `microfinance_group` | 1,719 | 1,706 | 1,679 | +1.61% |
| `upg_enrolment` | 550 | 547 | 540 | +1.30% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,343,016 / 11,700,703
- **Reduction Ratio**: 79.9754%
- **Pair Completeness (Recall Ceiling)**: 18.44%
- **Pair Quality**: 0.01%
