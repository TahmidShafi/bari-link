# Evaluation Report: splink_v3_1 (holdout_6)

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
| **Precision** | **0.9420** | 0.9565 | 0.9935 |
| **Recall** | **0.4993** | 0.4608 | 0.8816 |
| **F1 Score** | **0.6527** | 0.6220 | **0.9342** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **3.17%** |
| **False-Merge Clusters** | 26 |
| **False-Merged Records (Minority)** | 27 |
| **Split Persons** | 479 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 936.0 |
| **Clerical Review Load (per 10k records)** | 1807.3 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,836** | **4,208** | **3,702** | **+13.67%** |
| `club_formation` | 380 | 378 | 368 | +2.72% |
| `livelihood_support` | 2,174 | 2,125 | 2,120 | +0.24% |
| `microfinance_group` | 1,723 | 1,702 | 1,674 | +1.67% |
| `upg_enrolment` | 559 | 548 | 540 | +1.48% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,803 / 11,691,030
- **Reduction Ratio**: 99.6082%
- **Pair Completeness (Recall Ceiling)**: 89.02%
- **Pair Quality**: 2.78%
