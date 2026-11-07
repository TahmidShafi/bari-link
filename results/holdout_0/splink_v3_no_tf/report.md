# Evaluation Report: splink_v3_no_tf (holdout_0)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `a4f11e5e12edad3f...`
- **Selected $t_{\text{cost}}$**: `Weight = 7.75 (p = 0.995376)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9468** | 0.9633 | 0.9937 |
| **Recall** | **0.4963** | 0.4643 | 0.8753 |
| **F1 Score** | **0.6512** | 0.6266 | **0.9308** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.12%** |
| **False-Merge Clusters** | 25 |
| **False-Merged Records (Minority)** | 26 |
| **Split Persons** | 502 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 945.0 |
| **Clerical Review Load (per 10k records)** | 1727.8 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,798** | **4,167** | **3,634** | **+14.67%** |
| `club_formation` | 383 | 383 | 373 | +2.68% |
| `livelihood_support` | 2,160 | 2,106 | 2,105 | +0.05% |
| `microfinance_group` | 1,699 | 1,688 | 1,658 | +1.81% |
| `upg_enrolment` | 556 | 545 | 540 | +0.93% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,507 / 11,508,003
- **Reduction Ratio**: 99.6046%
- **Pair Completeness (Recall Ceiling)**: 88.36%
- **Pair Quality**: 2.85%
