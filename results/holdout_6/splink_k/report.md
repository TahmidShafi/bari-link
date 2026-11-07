# Evaluation Report: splink_k (holdout_6)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `95a50ae901ef905a...`
- **Selected $t_{\text{cost}}$**: `Weight = 1.25 (p = 0.704003)`
- **Selected $t_{p99}$**: `Weight = 9.25 (p = 0.998360)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9405** | 0.9595 | 0.9926 |
| **Recall** | **0.5965** | 0.5629 | 0.9058 |
| **F1 Score** | **0.7300** | 0.7096 | **0.9472** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.76%** |
| **False-Merge Clusters** | 28 |
| **False-Merged Records (Minority)** | 30 |
| **Split Persons** | 380 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 847.0 |
| **Clerical Review Load (per 10k records)** | 196.4 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,836** | **4,091** | **3,702** | **+10.51%** |
| `club_formation` | 380 | 374 | 368 | +1.63% |
| `livelihood_support` | 2,174 | 2,125 | 2,120 | +0.24% |
| `microfinance_group` | 1,723 | 1,684 | 1,674 | +0.60% |
| `upg_enrolment` | 559 | 547 | 540 | +1.30% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,803 / 11,691,030
- **Reduction Ratio**: 99.6082%
- **Pair Completeness (Recall Ceiling)**: 89.02%
- **Pair Quality**: 2.78%
