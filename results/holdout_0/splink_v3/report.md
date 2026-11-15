# Evaluation Report: splink_v3 (holdout_0)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `e4bdaee9d038dfc0...`
- **Selected $t_{\text{cost}}$**: `Weight = 8.00 (p = 0.996109)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9497** | 0.9628 | 0.9941 |
| **Recall** | **0.4881** | 0.4575 | 0.8735 |
| **F1 Score** | **0.6448** | 0.6202 | **0.9299** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.12%** |
| **False-Merge Clusters** | 23 |
| **False-Merged Records (Minority)** | 25 |
| **Split Persons** | 512 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 942.0 |
| **Clerical Review Load (per 10k records)** | 1694.5 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,798** | **4,172** | **3,634** | **+14.80%** |
| `club_formation` | 383 | 382 | 373 | +2.41% |
| `livelihood_support` | 2,160 | 2,104 | 2,105 | -0.05% |
| `microfinance_group` | 1,699 | 1,683 | 1,658 | +1.51% |
| `upg_enrolment` | 556 | 546 | 540 | +1.11% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,507 / 11,508,003
- **Reduction Ratio**: 99.6046%
- **Pair Completeness (Recall Ceiling)**: 88.36%
- **Pair Quality**: 2.85%
