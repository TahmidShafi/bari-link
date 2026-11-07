# Evaluation Report: splink_v3_no_kinship (holdout_4)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `6a46c7aeeed1d046...`
- **Selected $t_{\text{cost}}$**: `Weight = 1.25 (p = 0.704003)`
- **Selected $t_{p99}$**: `Weight = 9.25 (p = 0.998360)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9480** | 0.9651 | 0.9933 |
| **Recall** | **0.6081** | 0.5768 | 0.9081 |
| **F1 Score** | **0.7409** | 0.7221 | **0.9488** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 27 |
| **False-Merged Records (Minority)** | 30 |
| **Split Persons** | 380 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 804.0 |
| **Clerical Review Load (per 10k records)** | 169.1 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,908** | **4,152** | **3,762** | **+10.37%** |
| `club_formation` | 392 | 386 | 380 | +1.58% |
| `livelihood_support` | 2,215 | 2,157 | 2,151 | +0.28% |
| `microfinance_group` | 1,751 | 1,711 | 1,691 | +1.18% |
| `upg_enrolment` | 550 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,653 / 12,041,778
- **Reduction Ratio**: 99.6126%
- **Pair Completeness (Recall Ceiling)**: 89.44%
- **Pair Quality**: 2.76%
