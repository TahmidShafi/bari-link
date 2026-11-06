# Evaluation Report: splink_v1 (holdout_2)

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
| **Precision** | **0.9356** | 0.9481 | 0.9923 |
| **Recall** | **0.4850** | 0.4447 | 0.8771 |
| **F1 Score** | **0.6389** | 0.6054 | **0.9311** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.67%** |
| **False-Merge Clusters** | 33 |
| **False-Merged Records (Minority)** | 35 |
| **Split Persons** | 506 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 980.0 |
| **Clerical Review Load (per 10k records)** | 2176.3 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,866** | **4,258** | **3,731** | **+14.12%** |
| `club_formation` | 397 | 396 | 381 | +3.94% |
| `livelihood_support` | 2,200 | 2,122 | 2,133 | -0.52% |
| `microfinance_group` | 1,714 | 1,702 | 1,667 | +2.10% |
| `upg_enrolment` | 555 | 545 | 540 | +0.93% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,281 / 11,836,545
- **Reduction Ratio**: 99.6090%
- **Pair Completeness (Recall Ceiling)**: 89.14%
- **Pair Quality**: 2.77%
