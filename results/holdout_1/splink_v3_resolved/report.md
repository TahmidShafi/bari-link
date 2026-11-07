# Evaluation Report: splink_v3_resolved (holdout_1)

- **Dataset Role**: `holdout`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.9398** | 0.9915 |
| **Recall** | **0.5397** | 0.8878 |
| **F1 Score** | **0.6856** | 0.9368 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **4.65%** |
| **False-Merge Clusters** | 37 |
| **False-Merged Records (Minority)** | 38 |
| **Split Persons** | 454 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 934.0 |
| **Deduplicated Reach** | 4,143 (Error: +12.67%) |
| **Pair Completeness (Recall Ceiling)** | 89.56% |
