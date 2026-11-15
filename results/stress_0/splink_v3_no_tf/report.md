# Evaluation Report: splink_v3_no_tf (stress_0)

- **Dataset Role**: `stress`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `a4f11e5e12edad3f...`
- **Selected $t_{\text{cost}}$**: `Weight = 7.75 (p = 0.995376)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.6328** | 0.6735 | 0.9434 |
| **Recall** | **0.5253** | 0.4853 | 0.8919 |
| **F1 Score** | **0.5741** | 0.5641 | **0.9169** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **50.17%** |
| **False-Merge Clusters** | 229 |
| **False-Merged Records (Minority)** | 236 |
| **Split Persons** | 477 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 2,846.0 |
| **Clerical Review Load (per 10k records)** | 2185.9 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **5,142** | **4,291** | **4,003** | **+7.19%** |
| `club_formation` | 365 | 364 | 353 | +3.12% |
| `livelihood_support` | 2,179 | 2,115 | 2,109 | +0.28% |
| `microfinance_group` | 1,709 | 1,691 | 1,659 | +1.93% |
| `upg_enrolment` | 889 | 694 | 876 | -20.78% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 57,243 / 13,217,511
- **Reduction Ratio**: 99.5669%
- **Pair Completeness (Recall Ceiling)**: 89.54%
- **Pair Quality**: 2.23%
