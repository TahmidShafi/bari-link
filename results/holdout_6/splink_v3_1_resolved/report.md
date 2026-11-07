# Evaluation Report: splink_v3_1_resolved (holdout_6)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9516** | 0.9939 |
| **Recall** | **0.5364** | 0.8913 |
| **F1 Score** | **0.6860** | 0.9398 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **3.17%** |
| **False-Merge Clusters** | 26 |
| **False-Merged Records (Minority)** | 26 |
| **Split Persons** | 440 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 858.0 |
| **Deduplicated Reach** | 4,160 (Error: +12.37%) |
| **Pair Completeness (Recall Ceiling)** | 89.02% |
