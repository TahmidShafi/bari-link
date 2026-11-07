# Evaluation Report: splink_v1 (holdout_4)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `4e303cd4a82445ed...`
- **Selected $t_{\text{cost}}$**: `Weight = 9.25 (p = 0.998360)`
- **Selected $t_{p99}$**: `Weight = 16.75 (p = 0.999991)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.5494** | 0.6867 | 0.9083 |
| **Recall** | **0.7457** | 0.7144 | 0.9392 |
| **F1 Score** | **0.6327** | 0.7003 | **0.9235** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **18.75%** |
| **False-Merge Clusters** | 263 |
| **False-Merged Records (Minority)** | 388 |
| **Split Persons** | 261 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 4,766.0 |
| **Clerical Review Load (per 10k records)** | 7300.3 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,908** | **3,683** | **3,762** | **-2.10%** |
| `club_formation` | 392 | 379 | 380 | -0.26% |
| `livelihood_support` | 2,215 | 2,010 | 2,151 | -6.56% |
| `microfinance_group` | 1,751 | 1,630 | 1,691 | -3.61% |
| `upg_enrolment` | 550 | 531 | 540 | -1.67% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,653 / 12,041,778
- **Reduction Ratio**: 99.6126%
- **Pair Completeness (Recall Ceiling)**: 89.44%
- **Pair Quality**: 2.76%
