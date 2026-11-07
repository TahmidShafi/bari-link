# Evaluation Report: splink_v3_no_kinship (holdout_1)

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
| **Precision** | **0.9429** | 0.9589 | 0.9921 |
| **Recall** | **0.6156** | 0.5688 | 0.9062 |
| **F1 Score** | **0.7449** | 0.7140 | **0.9472** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.65%** |
| **False-Merge Clusters** | 31 |
| **False-Merged Records (Minority)** | 33 |
| **Split Persons** | 384 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 842.0 |
| **Clerical Review Load (per 10k records)** | 204.9 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,832** | **4,063** | **3,677** | **+10.50%** |
| `club_formation` | 388 | 381 | 374 | +1.87% |
| `livelihood_support` | 2,178 | 2,118 | 2,123 | -0.24% |
| `microfinance_group` | 1,705 | 1,672 | 1,659 | +0.78% |
| `upg_enrolment` | 561 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,322 / 11,671,696
- **Reduction Ratio**: 99.6031%
- **Pair Completeness (Recall Ceiling)**: 89.56%
- **Pair Quality**: 2.85%
