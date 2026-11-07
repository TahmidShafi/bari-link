# Evaluation Report: splink_v3_1_resolved (stress_0)

- **Dataset Role**: `stress`
- **Evaluation Mode**: `report`
- **Operational Thresholds**: $t_{\text{link}} = 6.5$,
  $t_{\text{bridge}} = 8.0$

## Headline Metrics

| Metric | Cluster-Level (Headline) | B-cubed |
| :--- | :--- | :--- |
| **Precision** | **0.6347** | 0.9403 |
| **Recall** | **0.5734** | 0.9047 |
| **F1 Score** | **0.6025** | 0.9221 |

| Safety & Cluster Entity Resolution Metrics | Value |
| :--- | :--- |
| **Doppelganger False-Merge Rate** | **57.07%** |
| **False-Merge Clusters** | 248 |
| **False-Merged Records (Minority)** | 252 |
| **Split Persons** | 423 |
| **Asymmetric Expected Cost ($5 \cdot FP + 1 \cdot FN$)** | 2,970.0 |
| **Deduplicated Reach** | 4,289 (Error: +5.15%) |
| **Pair Completeness (Recall Ceiling)** | 89.04% |
