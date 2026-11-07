# Evaluation Report: splink_k_resolved (holdout_8)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 2.0$,
  $t_{\text{bridge}} = 4.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9527** | 0.9939 |
| **Recall** | **0.5284** | 0.8886 |
| **F1 Score** | **0.6797** | 0.9383 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 25 |
| **False-Merged Records (Minority)** | 28 |
| **Split Persons** | 461 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 850.0 |
| **Deduplicated Reach** | 4,174 (Error: +12.66%) |
| **Pair Completeness (Recall Ceiling)** | 89.29% |
