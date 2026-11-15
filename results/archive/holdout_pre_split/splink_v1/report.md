# Evaluation Report: splink_v1 (holdout)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `d06e46f3d96e58b1...`
- **Selected $t_{\text{cost}}$**: `0.99`
- **Selected $t_{p99}$**: `N/A`

> **Note on $t_{p99}$**: No threshold achieves cluster-level precision >= 0.99 (maximum observed: 0.8884)

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9017** | 0.9233 | 0.9864 |
| **Recall** | **0.5310** | 0.4833 | 0.8830 |
| **F1 Score** | **0.6684** | 0.6345 | **0.9319** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.12%** |
| **False-Merge Clusters** | 57 |
| **False-Merged Records (Minority)** | 58 |
| **Split Persons** | 480 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,114.0 |
| **Clerical Review Load (per 10k records)** | 3157.6 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,798** | **4,098** | **3,634** | **+12.77%** |
| `club_formation` | 383 | 381 | 373 | +2.14% |
| `livelihood_support` | 2,160 | 2,071 | 2,105 | -1.62% |
| `microfinance_group` | 1,699 | 1,678 | 1,658 | +1.21% |
| `upg_enrolment` | 556 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,507 / 11,508,003
- **Reduction Ratio**: 99.6046%
- **Pair Completeness (Recall Ceiling)**: 88.36%
- **Pair Quality**: 2.85%
