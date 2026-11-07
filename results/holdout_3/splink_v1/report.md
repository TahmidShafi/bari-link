# Evaluation Report: splink_v1 (holdout_3)

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
| **Precision** | **0.6138** | 0.7116 | 0.9208 |
| **Recall** | **0.7717** | 0.7336 | 0.9441 |
| **F1 Score** | **0.6837** | 0.7224 | **0.9323** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **14.55%** |
| **False-Merge Clusters** | 261 |
| **False-Merged Records (Minority)** | 329 |
| **Split Persons** | 241 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 3,769.0 |
| **Clerical Review Load (per 10k records)** | 6801.2 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,855** | **3,669** | **3,716** | **-1.26%** |
| `club_formation` | 378 | 372 | 370 | +0.54% |
| `livelihood_support` | 2,208 | 2,015 | 2,135 | -5.62% |
| `microfinance_group` | 1,714 | 1,612 | 1,665 | -3.18% |
| `upg_enrolment` | 555 | 534 | 541 | -1.29% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,863 / 11,783,085
- **Reduction Ratio**: 99.6108%
- **Pair Completeness (Recall Ceiling)**: 88.72%
- **Pair Quality**: 2.75%
