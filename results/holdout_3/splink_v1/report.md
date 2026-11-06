# Evaluation Report: splink_v1 (holdout_3)

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
| **Precision** | **0.9441** | 0.9576 | 0.9934 |
| **Recall** | **0.4877** | 0.4454 | 0.8769 |
| **F1 Score** | **0.6431** | 0.6080 | **0.9316** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.82%** |
| **False-Merge Clusters** | 28 |
| **False-Merged Records (Minority)** | 29 |
| **Split Persons** | 509 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 932.0 |
| **Clerical Review Load (per 10k records)** | 2006.2 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,855** | **4,251** | **3,716** | **+14.40%** |
| `club_formation` | 378 | 377 | 370 | +1.89% |
| `livelihood_support` | 2,208 | 2,129 | 2,135 | -0.28% |
| `microfinance_group` | 1,714 | 1,703 | 1,665 | +2.28% |
| `upg_enrolment` | 555 | 545 | 541 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,863 / 11,783,085
- **Reduction Ratio**: 99.6108%
- **Pair Completeness (Recall Ceiling)**: 88.72%
- **Pair Quality**: 2.75%
