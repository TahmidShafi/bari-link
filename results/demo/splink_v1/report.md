# Evaluation Report: splink_v1 (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `select`
- **Threshold Grid**: `weight`
- **Selected $t_{\text{cost}}$**: `Weight = 9.00 (p = 0.998051)`
- **Selected $t_{p99}$**: `Weight = 15.50 (p = 0.999978)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9599** | 0.9676 | 0.9955 |
| **Recall** | **0.4544** | 0.4192 | 0.8688 |
| **F1 Score** | **0.6168** | 0.5850 | **0.9278** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 19 |
| **False-Merged Records (Minority)** | 19 |
| **Split Persons** | 534 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 912.0 |
| **Clerical Review Load (per 10k records)** | 2001.7 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,806** | **4,239** | **3,667** | **+15.60%** |
| `club_formation` | 365 | 364 | 353 | +3.12% |
| `livelihood_support` | 2,179 | 2,105 | 2,109 | -0.19% |
| `microfinance_group` | 1,709 | 1,699 | 1,659 | +2.41% |
| `upg_enrolment` | 553 | 545 | 540 | +0.93% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 49,984 / 11,546,415
- **Reduction Ratio**: 99.5671%
- **Pair Completeness (Recall Ceiling)**: 88.69%
- **Pair Quality**: 2.53%
