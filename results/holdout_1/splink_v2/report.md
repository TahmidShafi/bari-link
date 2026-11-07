# Evaluation Report: splink_v2 (holdout_1)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `bf3eb6e3610b6dc7...`
- **Selected $t_{\text{cost}}$**: `Weight = 9.25 (p = 0.998360)`
- **Selected $t_{p99}$**: `Weight = 17.25 (p = 0.999994)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9049** | 0.9224 | 0.9878 |
| **Recall** | **0.4773** | 0.4353 | 0.8717 |
| **F1 Score** | **0.6249** | 0.5914 | **0.9261** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.65%** |
| **False-Merge Clusters** | 52 |
| **False-Merged Records (Minority)** | 53 |
| **Split Persons** | 517 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,141.0 |
| **Clerical Review Load (per 10k records)** | 2202.0 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,832** | **4,208** | **3,677** | **+14.44%** |
| `club_formation` | 388 | 385 | 374 | +2.94% |
| `livelihood_support` | 2,178 | 2,095 | 2,123 | -1.32% |
| `microfinance_group` | 1,705 | 1,691 | 1,659 | +1.93% |
| `upg_enrolment` | 561 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,322 / 11,671,696
- **Reduction Ratio**: 99.6031%
- **Pair Completeness (Recall Ceiling)**: 89.56%
- **Pair Quality**: 2.85%
