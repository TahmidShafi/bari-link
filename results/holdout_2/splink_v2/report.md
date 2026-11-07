# Evaluation Report: splink_v2 (holdout_2)

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
| **Precision** | **0.8937** | 0.9200 | 0.9870 |
| **Recall** | **0.5031** | 0.4642 | 0.8814 |
| **F1 Score** | **0.6438** | 0.6170 | **0.9312** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 53 |
| **False-Merged Records (Minority)** | 57 |
| **Split Persons** | 489 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,144.0 |
| **Clerical Review Load (per 10k records)** | 2359.2 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,866** | **4,215** | **3,731** | **+12.97%** |
| `club_formation` | 397 | 397 | 381 | +4.20% |
| `livelihood_support` | 2,200 | 2,100 | 2,133 | -1.55% |
| `microfinance_group` | 1,714 | 1,705 | 1,667 | +2.28% |
| `upg_enrolment` | 555 | 546 | 540 | +1.11% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,281 / 11,836,545
- **Reduction Ratio**: 99.6090%
- **Pair Completeness (Recall Ceiling)**: 89.14%
- **Pair Quality**: 2.77%
