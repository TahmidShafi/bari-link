# Holdout Baseline Comparison Report: Probabilistic Linkage & Resolution vs. Baselines (5-Seed Uncertainty)

This benchmark evaluates the performance of probabilistic linkage and entity resolution across 5 independent holdout seeds (holdout_0, holdout_1, holdout_2, holdout_3, holdout_4).

---

## 1. Multi-Seed Summary Comparison Table

| Method | Cluster Precision (mean ± sd) | Cluster Recall (mean ± sd) | Cluster F1 (mean ± sd) | Pair Completeness | Doppelganger FM Pooled Rate [Wilson 95% CI] | Reach Error % (mean ± sd) | Review Pairs per 10k | $t_{\text{cost}}$ / Thresholds | $t_{\text{p99}}$ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `no_link` | 1.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.00% | 0.00% [0.00%, 1.03%] | +31.00% ± 0.70% | 0.0 | 25.00 / 1.000000 | none |
| `exact` | 0.9769 ± 0.0089 | 0.0979 ± 0.0155 | 0.1776 ± 0.0255 | 9.79% | 4.86% [3.10%, 7.56%] | +27.34% ± 1.03% | 0.0 | 25.00 / 1.000000 | none |
| `phone` | 0.7751 ± 0.0731 | 0.0867 ± 0.0106 | 0.1559 ± 0.0183 | 8.67% | 0.27% [0.05%, 1.51%] | +27.03% ± 0.61% | 0.0 | 25.00 / 1.000000 | none |
| `exact_or_phone` | 0.8557 ± 0.0419 | 0.1795 ± 0.0212 | 0.2964 ± 0.0302 | 17.63% | 5.14% [3.31%, 7.88%] | +23.70% ± 0.99% | 0.0 | 25.00 / 1.000000 | none |
| `splink_v1` | 0.6068 ± 0.0421 | 0.7564 ± 0.0106 | 0.6728 ± 0.0266 | 89.04% | 16.76% [13.30%, 20.90%] | -1.22% ± 0.87% | 6919.2 | 9.25 / 0.998360 | 16.75 / 0.999991 |
| `splink_v1_resolved` | 0.6303 ± 0.0327 | 0.7615 ± 0.0090 | 0.6893 ± 0.0197 | 89.04% | 16.22% [12.81%, 20.32%] | -1.32% ± 0.80% | 4326.4 | $t_{\text{link}}=8.5$ / $t_{\text{bridge}}=10.0$ | resolved |
| `splink_v3` | 0.9439 ± 0.0050 | 0.5107 ± 0.0159 | 0.6627 ± 0.0126 | 89.04% | 1.89% [0.92%, 3.85%] | +13.76% ± 0.76% | 1826.3 | 8.00 / 0.996109 | 20.00 / 0.999999 |
| `splink_v3_resolved` | 0.9500 ± 0.0071 | 0.5488 ± 0.0185 | 0.6956 ± 0.0157 | 89.04% | 1.89% [0.92%, 3.85%] | +12.26% ± 0.70% | 2464.0 | $t_{\text{link}}=6.5$ / $t_{\text{bridge}}=8.0$ | resolved |

> Note: B-cubed is reported only in `metrics.json` because singleton-heavy data inflate it (`no_link` scores about 0.86).

