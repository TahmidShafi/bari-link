# Holdout Baseline Comparison Report: Probabilistic Linkage & Resolution vs. Baselines (5-Seed Uncertainty)

This benchmark evaluates the performance of probabilistic linkage and entity resolution across 5 independent holdout seeds (holdout_0, holdout_1, holdout_2, holdout_3, holdout_4).

---

## 1. Multi-Seed Summary Comparison Table

| Method | Cluster Precision (mean ± sd) | Cluster Recall (mean ± sd) | Cluster F1 (mean ± sd) | Pair Completeness | Doppelganger FM Pooled Rate [Wilson 95% CI] | Reach Error % (mean ± sd) | Review Pairs per 10k | $t_{\text{cost}}$ / Thresholds | $t_{\text{p99}}$ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `no_link` | 1.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.00% | 0.00% [0.00%, 1.03%] | +31.00% ± 0.70% | 0.0 | 25.00 / 1.000000 | -5.00 / 0.030303 |
| `exact` | 0.9769 ± 0.0089 | 0.0979 ± 0.0155 | 0.1776 ± 0.0255 | 9.79% | 4.86% [3.10%, 7.56%] | +27.34% ± 1.03% | 0.0 | 25.00 / 1.000000 | none |
| `phone` | 0.7751 ± 0.0731 | 0.0867 ± 0.0106 | 0.1559 ± 0.0183 | 8.67% | 0.27% [0.05%, 1.51%] | +27.03% ± 0.61% | 0.0 | 25.00 / 1.000000 | none |
| `exact_or_phone` | 0.8557 ± 0.0419 | 0.1795 ± 0.0212 | 0.2964 ± 0.0302 | 17.63% | 5.14% [3.31%, 7.88%] | +23.70% ± 0.99% | 0.0 | 25.00 / 1.000000 | none |
| `splink_v1` | 0.9404 ± 0.0081 | 0.4741 ± 0.0122 | 0.6303 ± 0.0105 | 89.04% | 1.89% [0.92%, 3.85%] | +14.85% ± 0.69% | 2031.1 | 9.00 / 0.998051 | 15.50 / 0.999978 |
| `splink_v1_resolved` | 0.9484 ± 0.0067 | 0.4740 ± 0.0123 | 0.6320 ± 0.0107 | 89.04% | 1.89% [0.92%, 3.85%] | +14.97% ± 0.69% | 0.0 | $t_{\text{link}}=9.0$ / $t_{\text{bridge}}=9.0$ | resolved |

> Note: B-cubed is reported only in `metrics.json` because singleton-heavy data inflate it (`no_link` scores about 0.86).

