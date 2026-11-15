# Evaluation Report: splink_v3_resolved (holdout_0)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9482** | 0.9928 |
| **Recall** | **0.5235** | 0.8833 |
| **F1 Score** | **0.6746** | 0.9349 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.12%** |
| **False-Merge Clusters** | 30 |
| **False-Merged Records (Minority)** | 32 |
| **Split Persons** | 473 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 910.0 |
| **Deduplicated Reach** | 4,115 (Error: +13.24%) |
| **Pair Completeness (Recall Ceiling)** | 88.36% |
