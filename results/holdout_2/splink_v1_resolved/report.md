# Evaluation Report: splink_v1_resolved (holdout_2)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 9.0$,
  $t_{\text{bridge}} = 9.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9444** | 0.9934 |
| **Recall** | **0.4850** | 0.8771 |
| **F1 Score** | **0.6409** | 0.9316 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.67%** |
| **False-Merge Clusters** | 28 |
| **False-Merged Records (Minority)** | 30 |
| **Split Persons** | 506 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 945.0 |
| **Deduplicated Reach** | 4,263 (Error: +14.26%) |
| **Pair Completeness (Recall Ceiling)** | 89.14% |
