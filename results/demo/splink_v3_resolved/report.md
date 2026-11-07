# Evaluation Report: splink_v3_resolved (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9653** | 0.9947 |
| **Recall** | **0.5084** | 0.8836 |
| **F1 Score** | **0.6661** | 0.9359 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 25 |
| **False-Merged Records (Minority)** | 25 |
| **Split Persons** | 476 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 830.0 |
| **Deduplicated Reach** | 4,155 (Error: +13.31%) |
| **Pair Completeness (Recall Ceiling)** | 88.69% |
