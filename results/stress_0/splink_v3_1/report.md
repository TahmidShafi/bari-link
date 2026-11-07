# Evaluation Report: splink_v3_1 (stress_0)

- **Dataset Role**: `stress`
- **Evaluation Mode**: `report`
- **Threshold Grid**: `weight`
- **Threshold Source Run**: `demo`
- **Thresholds SHA-256**: `899e42fd581546ea...`
- **Selected $t_{\text{cost}}$**: `Weight = 8.00 (p = 0.996109)`
- **Selected $t_{p99}$**: `Weight = 20.00 (p = 0.999999)`

## Headline Metrics at Operational Threshold ($t_{\text{cost}}$)

| Metric | Cluster-Level (Headline) | Edge-Level (Diagnostic) | B-cubed |
| :--- | :--- | :--- | :--- |
| **Precision** | **0.6280** | 0.6690 | 0.9432 |
| **Recall** | **0.5336** | 0.4762 | 0.8953 |
| **F1 Score** | **0.5769** | 0.5564 | **0.9186** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **54.38%** |
| **False-Merge Clusters** | 233 |
| **False-Merged Records (Minority)** | 238 |
| **Split Persons** | 462 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 2,927.0 |
| **Clerical Review Load (per 10k records)** | 2216.2 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **5,207** | **4,354** | **4,079** | **+6.74%** |
| `club_formation` | 400 | 400 | 386 | +3.63% |
| `livelihood_support` | 2,163 | 2,105 | 2,108 | -0.14% |
| `microfinance_group` | 1,733 | 1,704 | 1,678 | +1.55% |
| `upg_enrolment` | 911 | 710 | 891 | -20.31% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 58,120 / 13,553,821
- **Reduction Ratio**: 99.5712%
- **Pair Completeness (Recall Ceiling)**: 90.21%
- **Pair Quality**: 2.22%
