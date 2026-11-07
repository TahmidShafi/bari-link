# Evaluation Report: splink_v3_no_tf (holdout_4)

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
| **Precision** | **0.9361** | 0.9476 | 0.9923 |
| **Recall** | **0.4990** | 0.4649 | 0.8804 |
| **F1 Score** | **0.6510** | 0.6238 | **0.9330** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **2.50%** |
| **False-Merge Clusters** | 33 |
| **False-Merged Records (Minority)** | 35 |
| **Split Persons** | 497 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 966.0 |
| **Clerical Review Load (per 10k records)** | 1864.3 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,908** | **4,281** | **3,762** | **+13.80%** |
| `club_formation` | 392 | 392 | 380 | +3.16% |
| `livelihood_support` | 2,215 | 2,150 | 2,151 | -0.05% |
| `microfinance_group` | 1,751 | 1,737 | 1,691 | +2.72% |
| `upg_enrolment` | 550 | 545 | 540 | +0.93% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,653 / 12,041,778
- **Reduction Ratio**: 99.6126%
- **Pair Completeness (Recall Ceiling)**: 89.44%
- **Pair Quality**: 2.76%
