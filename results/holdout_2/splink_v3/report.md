# Evaluation Report: splink_v3 (holdout_2)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `5b19102078e953a8...`
- **Selected $t_{\text{cost}}$**: `Weight = 8.00 (p = 0.996109)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9440** | 0.9579 | 0.9933 |
| **Recall** | **0.5275** | 0.4913 | 0.8874 |
| **F1 Score** | **0.6768** | 0.6495 | **0.9373** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.67%** |
| **False-Merge Clusters** | 28 |
| **False-Merged Records (Minority)** | 29 |
| **Split Persons** | 466 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 904.0 |
| **Clerical Review Load (per 10k records)** | 1958.5 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,866** | **4,213** | **3,731** | **+12.92%** |
| `club_formation` | 397 | 396 | 381 | +3.94% |
| `livelihood_support` | 2,200 | 2,132 | 2,133 | -0.05% |
| `microfinance_group` | 1,714 | 1,699 | 1,667 | +1.92% |
| `upg_enrolment` | 555 | 546 | 540 | +1.11% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,281 / 11,836,545
- **Reduction Ratio**: 99.6090%
- **Pair Completeness (Recall Ceiling)**: 89.14%
- **Pair Quality**: 2.77%
