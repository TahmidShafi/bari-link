# Evaluation Report: splink_v3_resolved (holdout_1)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9399** | 0.9915 |
| **Recall** | **0.5403** | 0.8880 |
| **F1 Score** | **0.6862** | 0.9369 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.65%** |
| **False-Merge Clusters** | 37 |
| **False-Merged Records (Minority)** | 38 |
| **Split Persons** | 453 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 933.0 |
| **Deduplicated Reach** | 4,142 (Error: +12.65%) |
| **Pair Completeness (Recall Ceiling)** | 89.56% |
