# Evaluation Report: splink_v3_1 (holdout_8)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `899e42fd581546ea...`
- **Selected $t_{\text{cost}}$**: `Weight = 8.00 (p = 0.996109)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9367** | 0.9489 | 0.9928 |
| **Recall** | **0.4929** | 0.4610 | 0.8780 |
| **F1 Score** | **0.6459** | 0.6205 | **0.9319** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 29 |
| **False-Merged Records (Minority)** | 33 |
| **Split Persons** | 505 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 950.0 |
| **Clerical Review Load (per 10k records)** | 1911.9 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,838** | **4,230** | **3,705** | **+14.17%** |
| `club_formation` | 391 | 391 | 377 | +3.71% |
| `livelihood_support` | 2,178 | 2,118 | 2,124 | -0.28% |
| `microfinance_group` | 1,719 | 1,709 | 1,679 | +1.79% |
| `upg_enrolment` | 550 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,141 / 11,700,703
- **Reduction Ratio**: 99.6057%
- **Pair Completeness (Recall Ceiling)**: 89.29%
- **Pair Quality**: 2.73%
