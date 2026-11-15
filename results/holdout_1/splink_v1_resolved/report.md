# Evaluation Report: splink_v1_resolved (holdout_1)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 8.5$,
  $t_{\text{bridge}} = 10.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9073** | 0.9892 |
| **Recall** | **0.4380** | 0.8637 |
| **F1 Score** | **0.5908** | 0.9222 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.65%** |
| **False-Merge Clusters** | 46 |
| **False-Merged Records (Minority)** | 48 |
| **Split Persons** | 544 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,159.0 |
| **Deduplicated Reach** | 4,246 (Error: +15.47%) |
| **Pair Completeness (Recall Ceiling)** | 89.56% |
