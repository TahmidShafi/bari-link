# Evaluation Report: splink_v1 (holdout_2)

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
| **Precision** | **0.5828** | 0.6849 | 0.9143 |
| **Recall** | **0.7620** | 0.7230 | 0.9433 |
| **F1 Score** | **0.6604** | 0.7035 | **0.9286** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **20.00%** |
| **False-Merge Clusters** | 257 |
| **False-Merged Records (Minority)** | 360 |
| **Split Persons** | 239 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 4,262.0 |
| **Clerical Review Load (per 10k records)** | 6987.3 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,866** | **3,662** | **3,731** | **-1.85%** |
| `club_formation` | 397 | 386 | 381 | +1.31% |
| `livelihood_support` | 2,200 | 2,011 | 2,133 | -5.72% |
| `microfinance_group` | 1,714 | 1,588 | 1,667 | -4.74% |
| `upg_enrolment` | 555 | 538 | 540 | -0.37% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,281 / 11,836,545
- **Reduction Ratio**: 99.6090%
- **Pair Completeness (Recall Ceiling)**: 89.14%
- **Pair Quality**: 2.77%
