# Evaluation Report: splink_v3_no_tf (holdout_2)

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
| **Precision** | **0.9413** | 0.9592 | 0.9933 |
| **Recall** | **0.5247** | 0.4906 | 0.8865 |
| **F1 Score** | **0.6738** | 0.6492 | **0.9369** |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **5.00%** |
| **False-Merge Clusters** | 27 |
| **False-Merged Records (Minority)** | 29 |
| **Split Persons** | 468 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 918.0 |
| **Clerical Review Load (per 10k records)** | 2040.7 |

## Deduplicated Beneficiary Reach

| Administrative Scope | Naive Records | De-duplicated Reach | True Beneficiaries | Reach Error % |
| :--- | :--- | :--- | :--- | :--- |
| **Overall Population** | **4,866** | **4,221** | **3,731** | **+13.13%** |
| `club_formation` | 397 | 397 | 381 | +4.20% |
| `livelihood_support` | 2,200 | 2,136 | 2,133 | +0.14% |
| `microfinance_group` | 1,714 | 1,702 | 1,667 | +2.10% |
| `upg_enrolment` | 555 | 546 | 540 | +1.11% |

## Candidate Generation & Blocking Performance

- **Candidate Pairs Evaluated**: 46,281 / 11,836,545
- **Reduction Ratio**: 99.6090%
- **Pair Completeness (Recall Ceiling)**: 89.14%
- **Pair Quality**: 2.77%
