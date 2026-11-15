# Evaluation Report: splink_v1 (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `select`
- **Threshold Grid**: `weight`
- **Selected $t_{\text{cost}}$**: `Weight = 9.25 (p = 0.998360)`
- **Selected $t_{p99}$**: `Weight = 16.75 (p = 0.999991)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9569** | 0.9602 | 0.9951 |
| **Recall** | **0.4206** | 0.3897 | 0.8612 |
| **F1 Score** | **0.5844** | 0.5544 | **0.9233** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 22 |
| **False-Merged Records (Minority)** | 22 |
| **Split Persons** | 561 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 960.0 |
| **Clerical Review Load (per 10k records)** | 2207.7 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,806** | **4,271** | **3,667** | **+16.47%** |
| `club_formation` | 365 | 364 | 353 | +3.12% |
| `livelihood_support` | 2,179 | 2,105 | 2,109 | -0.19% |
| `microfinance_group` | 1,709 | 1,701 | 1,659 | +2.53% |
| `upg_enrolment` | 553 | 545 | 540 | +0.93% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 49,984 / 11,546,415
- **Reduction Ratio**: 99.5671%
- **Pair Completeness (Recall Ceiling)**: 88.69%
- **Pair Quality**: 2.53%
