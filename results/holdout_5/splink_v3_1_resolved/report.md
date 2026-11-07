# Evaluation Report: splink_v3_1_resolved (holdout_5)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9554** | 0.9930 |
| **Recall** | **0.5649** | 0.8942 |
| **F1 Score** | **0.7100** | 0.9410 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 32 |
| **False-Merged Records (Minority)** | 33 |
| **Split Persons** | 437 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 817.0 |
| **Deduplicated Reach** | 4,133 (Error: +12.04%) |
| **Pair Completeness (Recall Ceiling)** | 89.04% |
