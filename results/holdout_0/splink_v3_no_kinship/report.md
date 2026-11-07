# Evaluation Report: splink_v3_no_kinship (holdout_0)

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
| **Precision** | **0.9465** | 0.9634 | 0.9927 |
| **Recall** | **0.5902** | 0.5548 | 0.8995 |
| **F1 Score** | **0.7270** | 0.7041 | **0.9438** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.12%** |
| **False-Merge Clusters** | 28 |
| **False-Merged Records (Minority)** | 30 |
| **Split Persons** | 411 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 847.0 |
| **Clerical Review Load (per 10k records)** | 187.6 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,798** | **4,043** | **3,634** | **+11.25%** |
| `club_formation` | 383 | 378 | 373 | +1.34% |
| `livelihood_support` | 2,160 | 2,106 | 2,105 | +0.05% |
| `microfinance_group` | 1,699 | 1,667 | 1,658 | +0.54% |
| `upg_enrolment` | 556 | 548 | 540 | +1.48% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,507 / 11,508,003
- **Reduction Ratio**: 99.6046%
- **Pair Completeness (Recall Ceiling)**: 88.36%
- **Pair Quality**: 2.85%
