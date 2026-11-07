# Doppelganger Stress Test Report: `stress_0`

This benchmark stress-tests models against a high-density doppelganger population with `min_pairs: 400` (559 total doppelganger person pairs: 60 natural, 499 injected).
All models are evaluated strictly at their frozen dev-selected operational thresholds.

---

## 1. Doppelganger False-Merge Stress Test Table

| Method | Operational Threshold | Cluster Precision | Cluster Recall | Cluster F1 | Natural Doppelganger FM Rate [Wilson 95% CI] | Injected Doppelganger FM Rate [Wilson 95% CI] | Pooled Doppelganger FM Rate [Wilson 95% CI] | Reach Error % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `splink_v1` | $w=9.25$ ($p=0.9984$) | 0.6209 | 0.4580 | 0.5272 | **2/60** (3.3%) [0.9%, 11.4%] | **254/499** (50.9%) [46.5%, 55.3%] | **256/559** (45.8%) [41.7%, 49.9%] | +9.32% |
| `splink_v2` | $w=9.25$ ($p=0.9984$) | 0.6276 | 0.5126 | 0.5643 | **2/60** (3.3%) [0.9%, 11.4%] | **274/499** (54.9%) [50.5%, 59.2%] | **276/559** (49.4%) [45.2%, 53.5%] | +7.53% |
| `splink_v3` | $w=8.00$ ($p=0.9961$) | 0.6280 | 0.5336 | 0.5769 | **2/60** (3.3%) [0.9%, 11.4%] | **302/499** (60.5%) [56.2%, 64.7%] | **304/559** (54.4%) [50.2%, 58.5%] | +6.74% |
| `splink_v3_no_tf` | $w=7.75$ ($p=0.9954$) | 0.6235 | 0.5490 | 0.5839 | **2/60** (3.3%) [0.9%, 11.4%] | **303/499** (60.7%) [56.4%, 64.9%] | **305/559** (54.6%) [50.4%, 58.6%] | +6.18% |
| `splink_v3_no_kinship` | $w=1.25$ ($p=0.7040$) | 0.6095 | 0.6462 | 0.6273 | **4/60** (6.7%) [2.6%, 15.9%] | **381/499** (76.4%) [72.4%, 79.9%] | **385/559** (68.9%) [64.9%, 72.6%] | +2.03% |
| `splink_v3_resolved` | $t_{\text{link}}=6.5$, $t_{\text{bridge}}=8.0$ | 0.6347 | 0.5734 | 0.6025 | **2/60** (3.3%) [0.9%, 11.4%] | **317/499** (63.5%) [59.2%, 67.6%] | **319/559** (57.1%) [52.9%, 61.1%] | +5.15% |
| `splink_v3_1_resolved` | $t_{\text{link}}=6.5$, $t_{\text{bridge}}=8.0$ | 0.6347 | 0.5734 | 0.6025 | **2/60** (3.3%) [0.9%, 11.4%] | **317/499** (63.5%) [59.2%, 67.6%] | **319/559** (57.1%) [52.9%, 61.1%] | +5.15% |
| `splink_k_resolved` | $t_{\text{link}}=2.0$, $t_{\text{bridge}}=4.0$ | 0.6171 | 0.5545 | 0.5842 | **0/60** (0.0%) [0.0%, 6.0%] | **355/499** (71.1%) [67.0%, 74.9%] | **355/559** (63.5%) [59.4%, 67.4%] | +4.93% |

---

## 2. Doppelganger Generation Mechanism & Roster Overlap Notes

### Generation Mechanism
- **Natural Doppelgangers**: Distinct persons residing in different households who naturally share the same canonical given name, guardian name, and village through demographic sampling from rural Bangladeshi frequency distributions.
- **Injected Doppelgangers**: High-density hard negative pairs explicitly synthesized across distinct households within the same village (or union) to stress-test linkage boundaries when names, guardians, and locations collide (target `min_pairs: 400`, realized: 499 injected pairs).

### Roster Overlap Statistics
- **Pairs with Both Rosters Available**: 21 / 559 pairs (3.8%).
- **Mean Roster Overlap**: 0.43 members (Maximum: 1 members).
- **Significance**: Because doppelgangers belong to distinct households, their kinship rosters show essentially zero overlap. In contrast, same-household co-residents exhibit high roster overlap ($\ge 2$ members).

### Interpretation Note
- Variants operate at different selected thresholds whose weight scales are not comparable, and only 21/559 doppelganger pairs have rosters on both records, so the stress table alone does not isolate a kinship effect.

---

## 3. Matched-Recall Doppelganger False-Merge Comparison

To control for threshold stringency across variants, doppelganger false-merge rates are evaluated at matched cluster recall levels $R \in \{0.40, 0.50, 0.60\}$ via linear interpolation along each variant's parametric threshold sweep curve. Complete curves are saved to `stress_curves.parquet` and visualized in `charts/stress_fm_vs_recall.html`.

| Method | Pooled FM @ R=0.40 | Natural FM @ R=0.40 | Injected FM @ R=0.40 | Pooled FM @ R=0.50 | Natural FM @ R=0.50 | Injected FM @ R=0.50 | Pooled FM @ R=0.60 | Natural FM @ R=0.60 | Injected FM @ R=0.60 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `splink_v1` | 41.8% | 0.0% | 46.9% | 49.3% | 3.3% | 54.8% | 56.9% | 3.3% | 63.3% |
| `splink_v2` | 43.8% | 0.0% | 49.1% | 49.1% | 3.3% | 54.6% | 54.9% | 3.3% | 61.0% |
| `splink_v3` | 46.7% | 0.0% | 52.3% | 52.4% | 3.3% | 58.2% | 58.3% | 3.3% | 64.9% |
| `splink_v3_no_tf` | 47.6% | 3.3% | 52.9% | 52.8% | 3.3% | 58.8% | 58.2% | 3.3% | 64.8% |
| `splink_v3_no_kinship` (unresolved) | 54.5% | 0.0% | 61.1% | 61.6% | 1.7% | 68.8% | 66.5% | 6.7% | 73.7% |
| `splink_v3_resolved` | 46.7% | 0.0% | 52.3% | 52.3% | 2.8% | 58.3% | 58.8% | 3.3% | 65.5% |
| `splink_v3_1_resolved` (Reference) | 46.7% | 0.0% | 52.3% | 52.3% | 2.7% | 58.3% | 58.8% | 3.3% | 65.5% |
| `splink_k_resolved` (Pipeline K) | 55.0% | 0.0% | 61.6% | 62.1% | 0.0% | 69.6% | 64.9% | 0.0% | 72.7% |

### Evaluation Benchmark Note
- On natural demographic holdouts (`holdout_5` .. `holdout_9`), doppelganger false-merge rates for Pipeline K (1.32% [0.56%, 3.04%]) vs Reference (1.58% [0.73%, 3.40%]) show no detectable difference; CIs overlap.
- Pipeline K (`splink_k_resolved`) is preferred under this synthetic benchmark and the assumed 5:1 cost ratio; not validated on real registry data.

