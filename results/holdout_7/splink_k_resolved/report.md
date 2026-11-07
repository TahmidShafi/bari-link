# Evaluation Report: splink_k_resolved (holdout_7)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 2.0$,
  $t_{\text{bridge}} = 4.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9580** | 0.9951 |
| **Recall** | **0.5207** | 0.8877 |
| **F1 Score** | **0.6747** | 0.9383 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **3.09%** |
| **False-Merge Clusters** | 20 |
| **False-Merged Records (Minority)** | 22 |
| **Split Persons** | 458 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 832.0 |
| **Deduplicated Reach** | 4,192 (Error: +13.11%) |
| **Pair Completeness (Recall Ceiling)** | 90.66% |
