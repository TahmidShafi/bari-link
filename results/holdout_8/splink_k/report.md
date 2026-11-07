# Evaluation Report: splink_k (holdout_8)

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
| **Precision** | **0.9369** | 0.9545 | 0.9917 |
| **Recall** | **0.6007** | 0.5660 | 0.9037 |
| **F1 Score** | **0.7321** | 0.7106 | **0.9456** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 32 |
| **False-Merged Records (Minority)** | 36 |
| **Split Persons** | 404 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 848.0 |
| **Clerical Review Load (per 10k records)** | 194.3 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,838** | **4,106** | **3,705** | **+10.82%** |
| `club_formation` | 391 | 386 | 377 | +2.39% |
| `livelihood_support` | 2,178 | 2,123 | 2,124 | -0.05% |
| `microfinance_group` | 1,719 | 1,694 | 1,679 | +0.89% |
| `upg_enrolment` | 550 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,141 / 11,700,703
- **Reduction Ratio**: 99.6057%
- **Pair Completeness (Recall Ceiling)**: 89.29%
- **Pair Quality**: 2.73%
