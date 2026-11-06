# Evaluation Report: splink_v1 (holdout_4)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `572b85d2140740f8...`
- **Selected $t_{\text{cost}}$**: `Weight = 9.00 (p = 0.998051)`
- **Selected $t_{p99}$**: `Weight = 15.50 (p = 0.999978)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9442** | 0.9525 | 0.9934 |
| **Recall** | **0.4705** | 0.4315 | 0.8743 |
| **F1 Score** | **0.6280** | 0.5940 | **0.9301** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 28 |
| **False-Merged Records (Minority)** | 30 |
| **Split Persons** | 520 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 962.0 |
| **Clerical Review Load (per 10k records)** | 2110.8 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,908** | **4,313** | **3,762** | **+14.65%** |
| `club_formation` | 392 | 392 | 380 | +3.16% |
| `livelihood_support` | 2,215 | 2,141 | 2,151 | -0.46% |
| `microfinance_group` | 1,751 | 1,731 | 1,691 | +2.37% |
| `upg_enrolment` | 550 | 543 | 540 | +0.56% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,653 / 12,041,778
- **Reduction Ratio**: 99.6126%
- **Pair Completeness (Recall Ceiling)**: 89.44%
- **Pair Quality**: 2.76%
