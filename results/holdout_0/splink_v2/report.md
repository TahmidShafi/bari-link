# Evaluation Report: splink_v2 (holdout_0)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `bf3eb6e3610b6dc7...`
- **Selected $t_{\text{cost}}$**: `Weight = 9.25 (p = 0.998360)`
- **Selected $t_{p99}$**: `Weight = 17.25 (p = 0.999994)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.9395** | 0.9526 | 0.9926 |
| **Recall** | **0.4758** | 0.4377 | 0.8697 |
| **F1 Score** | **0.6317** | 0.5998 | **0.9271** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 31 |
| **False-Merged Records (Minority)** | 32 |
| **Split Persons** | 529 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 995.0 |
| **Clerical Review Load (per 10k records)** | 2011.3 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,798** | **4,186** | **3,634** | **+15.19%** |
| `club_formation` | 383 | 382 | 373 | +2.41% |
| `livelihood_support` | 2,160 | 2,091 | 2,105 | -0.67% |
| `microfinance_group` | 1,699 | 1,689 | 1,658 | +1.87% |
| `upg_enrolment` | 556 | 544 | 540 | +0.74% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 45,507 / 11,508,003
- **Reduction Ratio**: 99.6046%
- **Pair Completeness (Recall Ceiling)**: 88.36%
- **Pair Quality**: 2.85%
