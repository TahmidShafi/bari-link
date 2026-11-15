# Evaluation Report: splink_v1 (holdout_0)

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
| **Precision** | **0.9565** | 0.9626 | 0.9950 |
| **Recall** | **0.4193** | 0.3853 | 0.8565 |
| **F1 Score** | **0.5831** | 0.5503 | **0.9206** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 22 |
| **False-Merged Records (Minority)** | 22 |
| **Split Persons** | 575 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 993.0 |
| **Clerical Review Load (per 10k records)** | 2042.5 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,798** | **4,258** | **3,634** | **+17.17%** |
| `club_formation` | 383 | 382 | 373 | +2.41% |
| `livelihood_support` | 2,160 | 2,097 | 2,105 | -0.38% |
| `microfinance_group` | 1,699 | 1,690 | 1,658 | +1.93% |
| `upg_enrolment` | 556 | 545 | 540 | +0.93% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,507 / 11,508,003
- **Reduction Ratio**: 99.6046%
- **Pair Completeness (Recall Ceiling)**: 88.36%
- **Pair Quality**: 2.85%
