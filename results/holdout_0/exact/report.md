# Evaluation Report: exact (holdout_0)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `fd0c101a41f62d94...`
- **Selected $t_{\text{cost}}$**: `Weight = 25.00 (p = 1.000000)`
- **Selected $t_{p99}$**: `none`

> **Warning on $t_{\text{cost}}$**: Selected threshold lies on the grid boundary! The true optimum may lie outside the current grid range.

> **Note on $t_{p99}$**: No threshold achieves cluster-level precision >= 0.99 (maximum observed: 0.9648)

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9769** | 0.9769 | 0.9994 |
| **Recall** | **0.0865** | 0.0865 | 0.7790 |
| **F1 Score** | **0.1588** | 0.1588 | **0.8756** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **3.37%** |
| **False-Merge Clusters** | 3 |
| **False-Merged Records (Minority)** | 3 |
| **Split Persons** | 809 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,357.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,798** | **4,676** | **3,634** | **+28.67%** |
| `club_formation` | 383 | 380 | 373 | +1.88% |
| `livelihood_support` | 2,160 | 2,154 | 2,105 | +2.33% |
| `microfinance_group` | 1,699 | 1,691 | 1,658 | +1.99% |
| `upg_enrolment` | 556 | 554 | 540 | +2.59% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,312,311 / 11,508,003
- **Reduction Ratio**: 79.9069%
- **Pair Completeness (Recall Ceiling)**: 8.65%
- **Pair Quality**: 0.01%
