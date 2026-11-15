# Doppelganger Stress Test Report: `stress_0`

This benchmark stress-tests models against a high-density doppelganger population with `min_pairs: 400` (574 total doppelganger person pairs: 76 natural, 498 injected).
All models are evaluated strictly at their frozen dev-selected operational thresholds.

---

## 1. Doppelganger False-Merge Stress Test Table

| Method | Operational Threshold | Cluster Precision | Cluster Recall | Cluster F1 | Natural Doppelganger FM Rate [Wilson 95% CI] | Injected Doppelganger FM Rate [Wilson 95% CI] | Pooled Doppelganger FM Rate [Wilson 95% CI] | Reach Error % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `splink_v1` | $w=9.25$ ($p=0.9984$) | 0.6368 | 0.4593 | 0.5337 | **1/76** (1.3%) [0.2%, 7.1%] | **246/498** (49.4%) [45.0%, 53.8%] | **247/574** (43.0%) [39.0%, 47.1%] | +9.62% |
| `splink_v2` | $w=9.25$ ($p=0.9984$) | 0.6360 | 0.5007 | 0.5603 | **1/76** (1.3%) [0.2%, 7.1%] | **259/498** (52.0%) [47.6%, 56.4%] | **260/574** (45.3%) [41.3%, 49.4%] | +8.19% |
| `splink_v3` | $w=8.00$ ($p=0.9961$) | 0.6278 | 0.5176 | 0.5674 | **1/76** (1.3%) [0.2%, 7.1%] | **290/498** (58.2%) [53.9%, 62.5%] | **291/574** (50.7%) [46.6%, 54.8%] | +7.22% |
| `splink_v3_no_tf` | $w=7.75$ ($p=0.9954$) | 0.6328 | 0.5253 | 0.5741 | **1/76** (1.3%) [0.2%, 7.1%] | **287/498** (57.6%) [53.2%, 61.9%] | **288/574** (50.2%) [46.1%, 54.2%] | +7.19% |
| `splink_v3_no_kinship` | $w=1.25$ ($p=0.7040$) | 0.6162 | 0.6292 | 0.6227 | **2/76** (2.6%) [0.7%, 9.1%] | **359/498** (72.1%) [68.0%, 75.8%] | **361/574** (62.9%) [58.9%, 66.7%] | +2.85% |
| `splink_v3_resolved` | $t_{\text{link}}=6.5$, $t_{\text{bridge}}=8.0$ | 0.6376 | 0.5485 | 0.5897 | **1/76** (1.3%) [0.2%, 7.1%] | **301/498** (60.4%) [56.1%, 64.6%] | **302/574** (52.6%) [48.5%, 56.7%] | +6.02% |
| `splink_v3_1_resolved` | $t_{\text{link}}=6.5$, $t_{\text{bridge}}=8.0$ | 0.6376 | 0.5485 | 0.5897 | **1/76** (1.3%) [0.2%, 7.1%] | **301/498** (60.4%) [56.1%, 64.6%] | **302/574** (52.6%) [48.5%, 56.7%] | +6.02% |
| `splink_k_resolved` | $t_{\text{link}}=2.0$, $t_{\text{bridge}}=4.0$ | 0.6333 | 0.5506 | 0.5890 | **2/76** (2.6%) [0.7%, 9.1%] | **333/498** (66.9%) [62.6%, 70.9%] | **335/574** (58.4%) [54.3%, 62.3%] | +5.42% |

---

## 2. Doppelganger Generation Mechanism & Roster Overlap Notes

### Generation Mechanism
- **Natural Doppelgangers**: Distinct persons residing in different households who naturally share the same canonical given name, guardian name, and village through demographic sampling from rural Bangladeshi frequency distributions.
- **Injected Doppelgangers**: High-density hard negative pairs explicitly synthesized across distinct households within the same village (or union) to stress-test linkage boundaries when names, guardians, and locations collide (target `min_pairs: 400`, realized: 498 injected pairs).

### Roster Overlap Statistics
- **Pairs with Both Rosters Available**: 29 / 574 pairs (5.1%).
- **Mean Roster Overlap**: 0.24 members (Maximum: 1 members).
- **Significance**: Because doppelgangers belong to distinct households, their kinship rosters show essentially zero overlap. In contrast, same-household co-residents exhibit high roster overlap ($\ge 2$ members).

### Interpretation Note
- Variants operate at different selected thresholds whose weight scales are not comparable, and only 21/559 doppelganger pairs have rosters on both records, so the stress table alone does not isolate a kinship effect.

---

## 3. Matched-Recall Doppelganger False-Merge Comparison

To control for threshold stringency across variants, doppelganger false-merge rates are evaluated at matched cluster recall levels $R \in \{0.40, 0.50, 0.60\}$ via linear interpolation along each variant's parametric threshold sweep curve. Complete curves are saved to `stress_curves.parquet` and visualized in `charts/stress_fm_vs_recall.html`.

| Method | Pooled FM @ R=0.40 | Natural FM @ R=0.40 | Injected FM @ R=0.40 | Pooled FM @ R=0.50 | Natural FM @ R=0.50 | Injected FM @ R=0.50 | Pooled FM @ R=0.60 | Natural FM @ R=0.60 | Injected FM @ R=0.60 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `splink_v1` | 36.2% | 0.0% | 41.7% | 46.0% | 1.3% | 52.8% | 54.5% | 1.3% | 62.7% |
| `splink_v2` | 35.7% | 0.0% | 41.2% | 45.2% | 1.3% | 51.9% | 55.0% | 1.3% | 63.1% |
| `splink_v3` | 40.9% | 0.0% | 47.1% | 48.9% | 1.3% | 56.1% | 56.3% | 1.3% | 64.7% |
| `splink_v3_no_tf` | 39.6% | 1.3% | 45.4% | 48.7% | 1.3% | 55.9% | 56.6% | 3.8% | 64.6% |
| `splink_v3_no_kinship` (unresolved) | 50.2% | 0.0% | 57.8% | 55.1% | 0.0% | 63.5% | 60.7% | 2.6% | 69.5% |
| `splink_v3_resolved` | 41.1% | 0.0% | 47.4% | 49.0% | 1.3% | 56.3% | 56.2% | 1.3% | 64.6% |
| `splink_v3_1_resolved` (Reference) | 41.1% | 0.0% | 47.4% | 49.0% | 1.3% | 56.3% | 56.2% | 1.3% | 64.6% |
| `splink_k_resolved` (Pipeline K) | 50.2% | 0.0% | 57.9% | 55.6% | 1.1% | 63.9% | 60.3% | 2.6% | 69.1% |

### Evaluation Benchmark Note
- On natural demographic holdouts (`holdout_5` .. `holdout_9`), doppelganger false-merge rates for Pipeline K (1.32% [0.56%, 3.04%]) vs Reference (1.58% [0.73%, 3.40%]) show no detectable difference; CIs overlap.
- Pipeline K (`splink_k_resolved`) is preferred under this synthetic benchmark and the assumed 5:1 cost ratio; not validated on real registry data.

