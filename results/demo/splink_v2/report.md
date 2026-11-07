# Evaluation Report: splink_v2 (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `select`
- **Threshold Grid**: `weight`
- **Selected $t_{\text{cost}}$**: `Weight = 9.25 (p = 0.998360)`
- **Selected $t_{p99}$**: `Weight = 17.25 (p = 0.999994)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9508** | 0.9532 | 0.9936 |
| **Recall** | **0.4614** | 0.4291 | 0.8710 |
| **F1 Score** | **0.6213** | 0.5918 | **0.9283** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 29 |
| **False-Merged Records (Minority)** | 29 |
| **Split Persons** | 527 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 937.0 |
| **Clerical Review Load (per 10k records)** | 2201.4 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,806** | **4,215** | **3,667** | **+14.94%** |
| `club_formation` | 365 | 364 | 353 | +3.12% |
| `livelihood_support` | 2,179 | 2,099 | 2,109 | -0.47% |
| `microfinance_group` | 1,709 | 1,701 | 1,659 | +2.53% |
| `upg_enrolment` | 553 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 49,984 / 11,546,415
- **Reduction Ratio**: 99.5671%
- **Pair Completeness (Recall Ceiling)**: 88.69%
- **Pair Quality**: 2.53%
