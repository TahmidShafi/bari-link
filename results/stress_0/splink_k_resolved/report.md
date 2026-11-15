# Evaluation Report: splink_k_resolved (stress_0)

- **Dataset Role**: `stress`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 2.0$,
  $t_{\text{bridge}} = 4.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.6333** | 0.9396 |
| **Recall** | **0.5506** | 0.9007 |
| **F1 Score** | **0.5890** | 0.9197 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **58.36%** |
| **False-Merge Clusters** | 250 |
| **False-Merged Records (Minority)** | 255 |
| **Split Persons** | 428 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 2,910.0 |
| **Deduplicated Reach** | 4,220 (Error: +5.42%) |
| **Pair Completeness (Recall Ceiling)** | 89.54% |
