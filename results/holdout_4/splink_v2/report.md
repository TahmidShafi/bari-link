# Evaluation Report: splink_v2 (holdout_4)

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
| **Precision** | **0.9309** | 0.9385 | 0.9913 |
| **Recall** | **0.4871** | 0.4454 | 0.8771 |
| **F1 Score** | **0.6396** | 0.6041 | **0.9307** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 38 |
| **False-Merged Records (Minority)** | 40 |
| **Split Persons** | 514 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 998.0 |
| **Clerical Review Load (per 10k records)** | 2218.8 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,908** | **4,291** | **3,762** | **+14.06%** |
| `club_formation` | 392 | 392 | 380 | +3.16% |
| `livelihood_support` | 2,215 | 2,136 | 2,151 | -0.70% |
| `microfinance_group` | 1,751 | 1,735 | 1,691 | +2.60% |
| `upg_enrolment` | 550 | 543 | 540 | +0.56% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,653 / 12,041,778
- **Reduction Ratio**: 99.6126%
- **Pair Completeness (Recall Ceiling)**: 89.44%
- **Pair Quality**: 2.76%
