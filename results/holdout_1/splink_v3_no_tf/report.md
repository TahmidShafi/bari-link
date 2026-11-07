# Evaluation Report: splink_v3_no_tf (holdout_1)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `a4f11e5e12edad3f...`
- **Selected $t_{\text{cost}}$**: `Weight = 7.75 (p = 0.995376)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9389** | 0.9580 | 0.9930 |
| **Recall** | **0.5105** | 0.4637 | 0.8789 |
| **F1 Score** | **0.6614** | 0.6249 | **0.9325** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.65%** |
| **False-Merge Clusters** | 27 |
| **False-Merged Records (Minority)** | 30 |
| **Split Persons** | 492 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 967.0 |
| **Clerical Review Load (per 10k records)** | 1970.2 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,832** | **4,201** | **3,677** | **+14.25%** |
| `club_formation` | 388 | 386 | 374 | +3.21% |
| `livelihood_support` | 2,178 | 2,122 | 2,123 | -0.05% |
| `microfinance_group` | 1,705 | 1,692 | 1,659 | +1.99% |
| `upg_enrolment` | 561 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,322 / 11,671,696
- **Reduction Ratio**: 99.6031%
- **Pair Completeness (Recall Ceiling)**: 89.56%
- **Pair Quality**: 2.85%
