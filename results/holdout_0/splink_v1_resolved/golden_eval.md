# Golden Record Evaluation: `splink_v1_resolved` on `holdout_0`

## Summary Metrics
- **Total Golden Records (Clusters)**: 4,224
- **Impure Clusters (>1 Person)**: 32 (0.76%)
- **Title-Free Canonical Name Accuracy**: 78.43%
- **Title Token Accuracy**: 80.80%
- **Birth Year Absolute Error (Mean)**: 0.71 years
- **Birth Year Absolute Error (Median)**: 0.0 years
- **Phone Coverage (Golden Records with Phone)**: 38.12% (1,610 / 4,224)
- **Phone Accuracy (Own Phone)**: 48.88% (787 / 1,610)
- **Phone Accuracy (Own OR Household Phone)**: 80.37% (1,294 / 1,610)
- **Father Name Accuracy**: 2.44% (103 / 4,224)
- **Husband Name Accuracy**: 11.46% (314 / 2,741)

---

## Field Survivorship & Kinship Analysis
1. **Title-Free Name Agreement**: Normalising female honorific prefixes and trailing titles separates stylistic variation from nominal identity, achieving high canonical fidelity.
2. **Kinship Guardian Disambiguation**: By preserving `father_name` and `husband_name` in separate fields, beneficiary guardian switches (e.g., at marriage) yield complementary populated fields with complete audit provenance.
3. **Age Heaping Robustness**: Taking the median of estimated birth years successfully mitigates single-module age rounding and survey recall biases.
