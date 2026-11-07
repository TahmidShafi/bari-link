# Evaluation Report: splink_v1 (holdout_0)

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
| **Precision** | **0.6577** | 0.7507 | 0.9308 |
| **Recall** | **0.7481** | 0.7052 | 0.9372 |
| **F1 Score** | **0.7000** | 0.7273 | **0.9340** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **11.24%** |
| **False-Merge Clusters** | 221 |
| **False-Merged Records (Minority)** | 285 |
| **Split Persons** | 265 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 3,230.0 |
| **Clerical Review Load (per 10k records)** | 6638.2 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,798** | **3,639** | **3,634** | **+0.14%** |
| `club_formation` | 383 | 374 | 373 | +0.27% |
| `livelihood_support` | 2,160 | 2,007 | 2,105 | -4.66% |
| `microfinance_group` | 1,699 | 1,603 | 1,658 | -3.32% |
| `upg_enrolment` | 556 | 540 | 540 | +0.00% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,507 / 11,508,003
- **Reduction Ratio**: 99.6046%
- **Pair Completeness (Recall Ceiling)**: 88.36%
- **Pair Quality**: 2.85%
