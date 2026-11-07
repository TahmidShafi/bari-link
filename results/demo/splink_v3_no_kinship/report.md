# Evaluation Report: splink_v3_no_kinship (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `select`
- **Threshold Grid**: `weight`
- **Selected $t_{\text{cost}}$**: `Weight = 1.25 (p = 0.704003)`
- **Selected $t_{p99}$**: `Weight = 9.25 (p = 0.998360)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9526** | 0.9688 | 0.9940 |
| **Recall** | **0.5787** | 0.5449 | 0.9009 |
| **F1 Score** | **0.7200** | 0.6975 | **0.9452** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.11%** |
| **False-Merge Clusters** | 23 |
| **False-Merged Records (Minority)** | 26 |
| **Split Persons** | 402 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 805.0 |
| **Clerical Review Load (per 10k records)** | 189.3 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,806** | **4,079** | **3,667** | **+11.24%** |
| `club_formation` | 365 | 355 | 353 | +0.57% |
| `livelihood_support` | 2,179 | 2,113 | 2,109 | +0.19% |
| `microfinance_group` | 1,709 | 1,679 | 1,659 | +1.21% |
| `upg_enrolment` | 553 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 49,984 / 11,546,415
- **Reduction Ratio**: 99.5671%
- **Pair Completeness (Recall Ceiling)**: 88.69%
- **Pair Quality**: 2.53%
