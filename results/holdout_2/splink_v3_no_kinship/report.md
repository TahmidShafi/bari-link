# Evaluation Report: splink_v3_no_kinship (holdout_2)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `6a46c7aeeed1d046...`
- **Selected $t_{\text{cost}}$**: `Weight = 1.25 (p = 0.704003)`
- **Selected $t_{p99}$**: `Weight = 9.25 (p = 0.998360)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9470** | 0.9665 | 0.9933 |
| **Recall** | **0.6340** | 0.6026 | 0.9143 |
| **F1 Score** | **0.7595** | 0.7424 | **0.9521** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.67%** |
| **False-Merge Clusters** | 26 |
| **False-Merged Records (Minority)** | 29 |
| **Split Persons** | 353 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 781.0 |
| **Clerical Review Load (per 10k records)** | 141.8 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,866** | **4,086** | **3,731** | **+9.51%** |
| `club_formation` | 397 | 391 | 381 | +2.62% |
| `livelihood_support` | 2,200 | 2,133 | 2,133 | +0.00% |
| `microfinance_group` | 1,714 | 1,677 | 1,667 | +0.60% |
| `upg_enrolment` | 555 | 546 | 540 | +1.11% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,281 / 11,836,545
- **Reduction Ratio**: 99.6090%
- **Pair Completeness (Recall Ceiling)**: 89.14%
- **Pair Quality**: 2.77%
