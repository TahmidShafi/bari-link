# Evaluation Report: splink_v3_no_tf (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `a4f11e5e12edad3f...`
- **Selected $t_{\text{cost}}$**: `Weight = 7.75 (p = 0.995376)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9581** | 0.9672 | 0.9949 |
| **Recall** | **0.4817** | 0.4551 | 0.8762 |
| **F1 Score** | **0.6411** | 0.6189 | **0.9318** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **2.74%** |
| **False-Merge Clusters** | 22 |
| **False-Merged Records (Minority)** | 22 |
| **Split Persons** | 504 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 888.0 |
| **Clerical Review Load (per 10k records)** | 1937.2 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,806** | **4,199** | **3,667** | **+14.51%** |
| `club_formation` | 365 | 365 | 353 | +3.40% |
| `livelihood_support` | 2,179 | 2,111 | 2,109 | +0.09% |
| `microfinance_group` | 1,709 | 1,700 | 1,659 | +2.47% |
| `upg_enrolment` | 553 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 49,984 / 11,546,415
- **Reduction Ratio**: 99.5671%
- **Pair Completeness (Recall Ceiling)**: 88.69%
- **Pair Quality**: 2.53%
