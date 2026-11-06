# Evaluation Report: splink_v1 (holdout_0)

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
| **Precision** | **0.9492** | 0.9565 | 0.9936 |
| **Recall** | **0.4581** | 0.4187 | 0.8654 |
| **F1 Score** | **0.6180** | 0.5824 | **0.9251** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.12%** |
| **False-Merge Clusters** | 28 |
| **False-Merged Records (Minority)** | 28 |
| **Split Persons** | 545 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 976.0 |
| **Clerical Review Load (per 10k records)** | 1817.4 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,798** | **4,210** | **3,634** | **+15.85%** |
| `club_formation` | 383 | 382 | 373 | +2.41% |
| `livelihood_support` | 2,160 | 2,093 | 2,105 | -0.57% |
| `microfinance_group` | 1,699 | 1,684 | 1,658 | +1.57% |
| `upg_enrolment` | 556 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,507 / 11,508,003
- **Reduction Ratio**: 99.6046%
- **Pair Completeness (Recall Ceiling)**: 88.36%
- **Pair Quality**: 2.85%
