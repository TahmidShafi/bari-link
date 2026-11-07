# Evaluation Report: splink_v1_resolved (holdout_4)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 9.0$,
  $t_{\text{bridge}} = 9.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9508** | 0.9943 |
| **Recall** | **0.4705** | 0.8743 |
| **F1 Score** | **0.6295** | 0.9305 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **0.00%** |
| **False-Merge Clusters** | 24 |
| **False-Merged Records (Minority)** | 26 |
| **Split Persons** | 520 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 937.0 |
| **Deduplicated Reach** | 4,317 (Error: +14.75%) |
| **Pair Completeness (Recall Ceiling)** | 89.44% |
