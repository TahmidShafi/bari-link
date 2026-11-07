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
| **Precision** | **0.6235** | 0.6705 | 0.9413 |
| **Recall** | **0.5490** | 0.4951 | 0.8984 |
| **F1 Score** | **0.5839** | 0.5696 | **0.9193** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **54.56%** |
| **False-Merge Clusters** | 239 |
| **False-Merged Records (Minority)** | 244 |
| **Split Persons** | 453 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 3,015.0 |
| **Clerical Review Load (per 10k records)** | 2179.8 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **5,207** | **4,331** | **4,079** | **+6.18%** |
| `club_formation` | 400 | 400 | 386 | +3.63% |
| `livelihood_support` | 2,163 | 2,106 | 2,108 | -0.09% |
| `microfinance_group` | 1,733 | 1,707 | 1,678 | +1.73% |
| `upg_enrolment` | 911 | 705 | 891 | -20.88% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 58,120 / 13,553,821
- **Reduction Ratio**: 99.5712%
- **Pair Completeness (Recall Ceiling)**: 90.21%
- **Pair Quality**: 2.22%
