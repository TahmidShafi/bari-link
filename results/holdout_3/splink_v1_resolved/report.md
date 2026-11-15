# Evaluation Report: splink_v1_resolved (holdout_3)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 8.5$,
  $t_{\text{bridge}} = 10.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9168** | 0.9901 |
| **Recall** | **0.4736** | 0.8744 |
| **F1 Score** | **0.6245** | 0.9287 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **1.82%** |
| **False-Merge Clusters** | 42 |
| **False-Merged Records (Minority)** | 44 |
| **Split Persons** | 517 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 1,052.0 |
| **Deduplicated Reach** | 4,245 (Error: +14.24%) |
| **Pair Completeness (Recall Ceiling)** | 88.72% |
