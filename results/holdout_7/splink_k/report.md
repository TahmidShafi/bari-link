# Evaluation Report: splink_k (holdout_7)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `95a50ae901ef905a...`
- **Selected $t_{\text{cost}}$**: `Weight = 1.25 (p = 0.704003)`
- **Selected $t_{p99}$**: `Weight = 9.25 (p = 0.998360)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9129** | 0.9466 | 0.9897 |
| **Recall** | **0.5984** | 0.5692 | 0.9042 |
| **F1 Score** | **0.7230** | 0.7109 | **0.9451** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.12%** |
| **False-Merge Clusters** | 36 |
| **False-Merged Records (Minority)** | 42 |
| **Split Persons** | 399 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 963.0 |
| **Clerical Review Load (per 10k records)** | 177.8 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,837** | **4,099** | **3,706** | **+10.60%** |
| `club_formation` | 399 | 395 | 384 | +2.86% |
| `livelihood_support` | 2,165 | 2,097 | 2,103 | -0.29% |
| `microfinance_group` | 1,716 | 1,676 | 1,665 | +0.66% |
| `upg_enrolment` | 557 | 543 | 540 | +0.56% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,158 / 11,695,866
- **Reduction Ratio**: 99.6053%
- **Pair Completeness (Recall Ceiling)**: 90.66%
- **Pair Quality**: 2.75%
