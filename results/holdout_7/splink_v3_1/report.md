# Evaluation Report: splink_v3_1 (holdout_7)

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
| **Precision** | **0.9018** | 0.9342 | 0.9899 |
| **Recall** | **0.4914** | 0.4558 | 0.8770 |
| **F1 Score** | **0.6362** | 0.6127 | **0.9300** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.12%** |
| **False-Merge Clusters** | 36 |
| **False-Merged Records (Minority)** | 42 |
| **Split Persons** | 517 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,088.0 |
| **Clerical Review Load (per 10k records)** | 1829.6 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,837** | **4,226** | **3,706** | **+14.03%** |
| `club_formation` | 399 | 399 | 384 | +3.91% |
| `livelihood_support` | 2,165 | 2,098 | 2,103 | -0.24% |
| `microfinance_group` | 1,716 | 1,697 | 1,665 | +1.92% |
| `upg_enrolment` | 557 | 543 | 540 | +0.56% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,158 / 11,695,866
- **Reduction Ratio**: 99.6053%
- **Pair Completeness (Recall Ceiling)**: 90.66%
- **Pair Quality**: 2.75%
