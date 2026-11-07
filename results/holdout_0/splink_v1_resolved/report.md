# Evaluation Report: splink_v1_resolved (holdout_0)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 8.5$,
  $t_{\text{bridge}} = 10.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.6772** | 0.9327 |
| **Recall** | **0.7556** | 0.9392 |
| **F1 Score** | **0.7143** | 0.9359 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **10.11%** |
| **False-Merge Clusters** | 224 |
| **False-Merged Records (Minority)** | 279 |
| **Split Persons** | 256 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 3,004.0 |
| **Deduplicated Reach** | 3,635 (Error: +0.03%) |
| **Pair Completeness (Recall Ceiling)** | 88.36% |
