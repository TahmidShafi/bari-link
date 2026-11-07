# Evaluation Report: splink_k_resolved (demo)

- **Dataset Role**: `dev`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 2.0$,
  $t_{\text{bridge}} = 4.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9772** | 0.9969 |
| **Recall** | **0.5105** | 0.8866 |
| **F1 Score** | **0.6707** | 0.9385 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 14 |
| **False-Merged Records (Minority)** | 14 |
| **Split Persons** | 452 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 782.0 |
| **Deduplicated Reach** | 4,150 (Error: +13.17%) |
| **Pair Completeness (Recall Ceiling)** | 88.69% |
