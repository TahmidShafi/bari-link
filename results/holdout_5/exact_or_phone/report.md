# Evaluation Report: exact_or_phone (holdout_5)

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
| **Precision** | **0.8731** | 0.8794 | 0.9923 |
| **Recall** | **0.1957** | 0.1922 | 0.8102 |
| **F1 Score** | **0.3197** | 0.3155 | **0.8920** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **5.06%** |
| **False-Merge Clusters** | 36 |
| **False-Merged Records (Minority)** | 36 |
| **Split Persons** | 717 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,364.0 |
| **Clerical Review Load (per 10k records)** | 0.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,841** | **4,547** | **3,689** | **+23.26%** |
| `club_formation` | 385 | 384 | 380 | +1.05% |
| `livelihood_support` | 2,186 | 2,158 | 2,122 | +1.70% |
| `microfinance_group` | 1,718 | 1,700 | 1,671 | +1.74% |
| `upg_enrolment` | 552 | 550 | 540 | +1.85% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 2,361,587 / 11,715,220
- **Reduction Ratio**: 79.8417%
- **Pair Completeness (Recall Ceiling)**: 19.22%
- **Pair Quality**: 0.01%
