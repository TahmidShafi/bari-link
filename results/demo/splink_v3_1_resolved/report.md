# Evaluation Report: splink_v3_1_resolved (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9654** | 0.9947 |
| **Recall** | **0.5098** | 0.8839 |
| **F1 Score** | **0.6673** | 0.9361 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 25 |
| **False-Merged Records (Minority)** | 25 |
| **Split Persons** | 475 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 828.0 |
| **Deduplicated Reach** | 4,153 (Error: +13.25%) |
| **Pair Completeness (Recall Ceiling)** | 88.69% |
