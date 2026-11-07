# Evaluation Report: splink_v3 (holdout_4)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `5b19102078e953a8...`
- **Selected $t_{\text{cost}}$**: `Weight = 8.00 (p = 0.996109)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9395** | 0.9522 | 0.9929 |
| **Recall** | **0.5073** | 0.4712 | 0.8825 |
| **F1 Score** | **0.6588** | 0.6304 | **0.9344** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 30 |
| **False-Merged Records (Minority)** | 33 |
| **Split Persons** | 489 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 944.0 |
| **Clerical Review Load (per 10k records)** | 1786.9 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,908** | **4,273** | **3,762** | **+13.58%** |
| `club_formation` | 392 | 391 | 380 | +2.89% |
| `livelihood_support` | 2,215 | 2,154 | 2,151 | +0.14% |
| `microfinance_group` | 1,751 | 1,726 | 1,691 | +2.07% |
| `upg_enrolment` | 550 | 545 | 540 | +0.93% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,653 / 12,041,778
- **Reduction Ratio**: 99.6126%
- **Pair Completeness (Recall Ceiling)**: 89.44%
- **Pair Quality**: 2.76%
