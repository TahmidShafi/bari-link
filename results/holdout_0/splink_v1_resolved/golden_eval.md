# Golden Record Evaluation: `splink_v1_resolved` on `holdout_0`

## Summary Metrics
- **Total Golden Records (Clusters)**: 4,214
- **Impure Clusters (>1 Person)**: 24 (0.57%)
- **Title-Free Canonical Name Accuracy**: 78.62%
- **Title Token Accuracy**: 81.04%
- **Birth Year Absolute Error (Mean)**: 0.71 years
- **Birth Year Absolute Error (Median)**: 0.0 years
- **Phone Coverage (Golden Records with Phone)**: 38.16% (1,608 / 4,214)
- **Phone Accuracy (Own Phone)**: 48.94% (787 / 1,608)
- **Phone Accuracy (Own OR Household Phone)**: 80.60% (1,296 / 1,608)
- **Father Name Accuracy**: 29.00% (1,222 / 4,214)
- **Husband Name Accuracy**: 11.52% (314 / 2,725)

---

## Field Survivorship & Kinship Analysis
1. **Title-Free Name Agreement**: Normalising female honorific prefixes and trailing titles separates stylistic variation from nominal identity, achieving high canonical fidelity.
2. **Kinship Guardian Disambiguation**: By preserving `father_name` and `husband_name` in separate fields, beneficiary guardian switches (e.g., at marriage) yield complementary populated fields with complete audit provenance.
3. **Age Heaping Robustness**: Taking the median of estimated birth years successfully mitigates single-module age rounding and survey recall biases.
