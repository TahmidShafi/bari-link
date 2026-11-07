# Evaluation Report: splink_v3_1_resolved (holdout_8)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9351** | 0.9916 |
| **Recall** | **0.5213** | 0.8857 |
| **F1 Score** | **0.6694** | 0.9357 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 35 |
| **False-Merged Records (Minority)** | 39 |
| **Split Persons** | 473 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 930.0 |
| **Deduplicated Reach** | 4,184 (Error: +12.93%) |
| **Pair Completeness (Recall Ceiling)** | 89.29% |
