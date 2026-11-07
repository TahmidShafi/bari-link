# Evaluation Report: splink_k_resolved (holdout_9)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 2.0$,
  $t_{\text{bridge}} = 4.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9781** | 0.9971 |
| **Recall** | **0.5114** | 0.8803 |
| **F1 Score** | **0.6717** | 0.9351 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 13 |
| **False-Merged Records (Minority)** | 13 |
| **Split Persons** | 480 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 811.0 |
| **Deduplicated Reach** | 4,141 (Error: +14.27%) |
| **Pair Completeness (Recall Ceiling)** | 88.56% |
