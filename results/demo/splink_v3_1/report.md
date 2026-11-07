# Evaluation Report: splink_v3_1 (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `select`
- **Threshold Grid**: `weight`
- **Selected $t_{\text{cost}}$**: `Weight = 8.00 (p = 0.996109)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9642** | 0.9679 | 0.9954 |
| **Recall** | **0.4726** | 0.4445 | 0.8743 |
| **F1 Score** | **0.6343** | 0.6092 | **0.9309** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 21 |
| **False-Merged Records (Minority)** | 21 |
| **Split Persons** | 510 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 876.0 |
| **Clerical Review Load (per 10k records)** | 1885.1 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,806** | **4,208** | **3,667** | **+14.75%** |
| `club_formation` | 365 | 364 | 353 | +3.12% |
| `livelihood_support` | 2,179 | 2,112 | 2,109 | +0.14% |
| `microfinance_group` | 1,709 | 1,698 | 1,659 | +2.35% |
| `upg_enrolment` | 553 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 49,984 / 11,546,415
- **Reduction Ratio**: 99.5671%
- **Pair Completeness (Recall Ceiling)**: 88.69%
- **Pair Quality**: 2.53%
