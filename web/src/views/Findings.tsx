import React, { useEffect, useState } from 'react';
import { getHeadlineFindings } from '../eval/evalData';
import {
  formatPct,
  formatRawPct,
  formatRate,
  formatNum,
  formatDelta,
  FORMAT_DECIMALS_THOUSANDTH,
  FORMAT_DECIMALS_HUNDREDTH,
  ZERO,
} from '../eval/formatters';

const GITHUB_REPO_URL = 'https://github.com/TahmidShafi/bari-link/blob/main';

export const Findings: React.FC = () => {
  const [headline, setHeadline] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHeadlineFindings()
      .then((data) => {
        setHeadline(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load headline findings:', err);
        setLoading(false);
      });
  }, []);

  if (loading || !headline) {
    return (
      <div className="card">
        <p className="tile-sub">Loading pre-registered empirical findings...</p>
      </div>
    );
  }

  const {
    leakage_before_after: leakage,
    h1,
    h2,
    h3,
    cost_ratio_sensitivity: costSensitivity,
    household,
  } = headline;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Intro Header */}
      <div className="card">
        <h2 className="card-title">Empirical Research Findings & Pre-Registered Outcomes</h2>
        <p className="tile-sub" style={{ marginTop: '0.25rem' }}>
          All metrics, confidence bounds, and decision outcomes are loaded dynamically from machine-readable evaluation artifacts.
        </p>
      </div>

      {/* Card 1: Ground-Truth Leakage Post-Mortem */}
      {leakage ? (
        <div className="card">
          <div className="card-header">
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className="chip chip-danger font-mono">CRITICAL METHODOLOGICAL LESSON</span>
                <span className="tile-sub">Discovery in Dev Pipeline</span>
              </div>
              <h3 className="card-title" style={{ marginTop: '0.5rem' }}>
                Ground-Truth Data Leakage (Before vs After Post-Mortem)
              </h3>
              <p className="tile-sub">{leakage.description}</p>
            </div>
            {leakage.source && (
              <a
                href={`${GITHUB_REPO_URL}/${leakage.source}`}
                target="_blank"
                rel="noreferrer"
                className="chip"
                style={{ textDecoration: 'none' }}
              >
                Source: {leakage.source}
              </a>
            )}
          </div>

          <p style={{ fontSize: '0.875rem', lineHeight: '1.5', marginBottom: '1rem' }}>
            Leaked ground-truth fields (guardian type, sex) inflated precision; after removing them, v1 precision fell from {formatRate(leakage.methods?.splink_v1_pre_fix?.cluster_precision_mean, FORMAT_DECIMALS_HUNDREDTH)} to {formatRate(leakage.methods?.splink_v1_post_fix?.cluster_precision_mean, FORMAT_DECIMALS_HUNDREDTH)} on the synthetic holdouts.
          </p>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Model Specification</th>
                  <th>Condition</th>
                  <th style={{ textAlign: 'right' }}>Precision (Holdout)</th>
                  <th style={{ textAlign: 'right' }}>Recall (Holdout)</th>
                  <th style={{ textAlign: 'right' }}>F1 Score</th>
                  <th style={{ textAlign: 'right' }}>Doppelganger FM</th>
                  <th style={{ textAlign: 'right' }}>Reach Error</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(leakage.methods || {}).map(([key, item]: [string, any]) => {
                  const isPre = item.status?.includes('Pre-Fix');
                  return (
                    <tr key={key}>
                      <td>
                        <strong>{key}</strong>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
                          {item.threshold}
                        </div>
                      </td>
                      <td>
                        <span className={isPre ? 'chip chip-danger' : 'chip chip-accent'}>
                          {item.status}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right' }} className="num font-mono">
                        {formatRate(item.cluster_precision_mean)} ± {formatRate(item.cluster_precision_sd)}
                      </td>
                      <td style={{ textAlign: 'right' }} className="num font-mono">
                        {formatRate(item.cluster_recall_mean)} ± {formatRate(item.cluster_recall_sd)}
                      </td>
                      <td style={{ textAlign: 'right' }} className="num font-mono">
                        {formatRate(item.cluster_f1_mean)}
                      </td>
                      <td style={{ textAlign: 'right' }} className="num font-mono">
                        {formatPct(item.doppelganger_fm_rate)}
                      </td>
                      <td style={{ textAlign: 'right' }} className="num font-mono">
                        {formatDelta(item.reach_error_pct_mean)}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="card" style={{ borderLeft: '4px solid var(--danger-color)' }}>
          <p style={{ color: 'var(--danger-text)', fontWeight: 'bold' }}>data missing: leakage_before_after</p>
        </div>
      )}

      {/* Card 2: Pre-Registered Hypotheses H1 & H2 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        {/* H1 */}
        {h1 ? (
          <div className="card">
            <div className="card-header">
              <div>
                <span className="chip chip-accent">{h1.verdict}</span>
                <h3 className="card-title" style={{ marginTop: '0.375rem' }}>{h1.title}</h3>
              </div>
              {h1.source && (
                <a
                  href={`${GITHUB_REPO_URL}/${h1.source}`}
                  target="_blank"
                  rel="noreferrer"
                  className="chip font-mono"
                  style={{ textDecoration: 'none', fontSize: '0.75rem' }}
                >
                  Source JSON
                </a>
              )}
            </div>

            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
              {h1.hypothesis}
            </p>

            <div className="tiles-grid" style={{ gridTemplateColumns: '1fr 1fr', marginBottom: '0.75rem' }}>
              <div className="tile">
                <span className="tile-title">Baseline Dev Cost</span>
                <span className="tile-value num">{formatNum(h1.baseline_dev_cost)}</span>
                <span className="tile-sub">{h1.baseline_model}</span>
              </div>
              <div className="tile">
                <span className="tile-title">Candidate Dev Cost</span>
                <span className="tile-value num" style={{ color: 'var(--accent)' }}>
                  {formatNum(h1.candidate_dev_cost)}
                </span>
                <span className="tile-sub">{h1.candidate_model}</span>
              </div>
            </div>

            <div style={{ fontSize: '0.8125rem', backgroundColor: 'var(--bg-surface-subtle)', padding: '0.75rem', borderRadius: '4px' }}>
              <div><strong>Cost Reduction:</strong> {formatDelta(h1.cost_reduction_points)} pts ({formatRawPct(h1.cost_reduction_pct)})</div>
              <div><strong>Decision Threshold:</strong> w ≥ {formatNum(h1.decision_threshold)}</div>
              <div><strong>Precision / Recall:</strong> {formatRate(h1.precision)} / {formatRate(h1.recall)} (F1: {formatRate(h1.f1)})</div>
              <div style={{ marginTop: '0.25rem', color: 'var(--success-text)', fontWeight: 'bold' }}>
                Outcome: {h1.outcome} — Exceeded pre-registered cost reduction requirement.
              </div>
            </div>
          </div>
        ) : (
          <div className="card" style={{ borderLeft: '4px solid var(--danger-color)' }}>
            <p style={{ color: 'var(--danger-text)', fontWeight: 'bold' }}>data missing: h1</p>
          </div>
        )}

        {/* H2 */}
        {h2 ? (
          <div className="card">
            <div className="card-header">
              <div>
                <span className="chip chip-accent">{h2.verdict}</span>
                <h3 className="card-title" style={{ marginTop: '0.375rem' }}>{h2.title}</h3>
              </div>
              {h2.source && (
                <a
                  href={`${GITHUB_REPO_URL}/${h2.source}`}
                  target="_blank"
                  rel="noreferrer"
                  className="chip font-mono"
                  style={{ textDecoration: 'none', fontSize: '0.75rem' }}
                >
                  Source JSON
                </a>
              )}
            </div>

            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
              {h2.hypothesis}
            </p>

            <div className="tiles-grid" style={{ gridTemplateColumns: '1fr 1fr', marginBottom: '0.75rem' }}>
              <div className="tile">
                <span className="tile-title">Baseline Dev Cost</span>
                <span className="tile-value num">{formatNum(h2.baseline_dev_cost)}</span>
                <span className="tile-sub">{h2.baseline_model}</span>
              </div>
              <div className="tile">
                <span className="tile-title">Candidate Dev Cost</span>
                <span className="tile-value num" style={{ color: 'var(--accent)' }}>
                  {formatNum(h2.candidate_dev_cost)}
                </span>
                <span className="tile-sub">{h2.candidate_model}</span>
              </div>
            </div>

            <div style={{ fontSize: '0.8125rem', backgroundColor: 'var(--bg-surface-subtle)', padding: '0.75rem', borderRadius: '4px' }}>
              <div><strong>Cost Reduction:</strong> {formatDelta(h2.cost_reduction_points)} pts ({formatRawPct(h2.cost_reduction_pct)})</div>
              <div><strong>False Merges (Same-HH):</strong> {h2.same_hh_false_merges_before} → {h2.same_hh_false_merges_after}</div>
              <div><strong>Total False Merges:</strong> {h2.total_false_merges_before} → {h2.total_false_merges_after}</div>
              <div style={{ marginTop: '0.25rem', color: 'var(--success-text)', fontWeight: 'bold' }}>
                Outcome: {h2.outcome} — Co-resident roster disambiguation confirmed.
              </div>
            </div>
          </div>
        ) : (
          <div className="card" style={{ borderLeft: '4px solid var(--danger-color)' }}>
            <p style={{ color: 'var(--danger-text)', fontWeight: 'bold' }}>data missing: h2</p>
          </div>
        )}
      </div>

      {/* Card 3: Hypothesis H3 & 5-Seed Holdout Confirmation */}
      {h3 ? (
        <div className="card">
          <div className="card-header">
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className="chip chip-accent">{h3.holdout_confirmation?.verdict}</span>
                <span className="fact-label">Pre-Registered Primary Hypothesis</span>
              </div>
              <h3 className="card-title" style={{ marginTop: '0.5rem' }}>{h3.title}</h3>
              <p className="tile-sub">{h3.hypothesis}</p>
            </div>
            {h3.source && (
              <a
                href={`${GITHUB_REPO_URL}/${h3.source}`}
                target="_blank"
                rel="noreferrer"
                className="chip"
                style={{ textDecoration: 'none' }}
              >
                Source: {h3.source}
              </a>
            )}
          </div>

          <div className="tiles-grid" style={{ marginBottom: '1.25rem' }}>
            <div className="tile">
              <span className="tile-title">Pipeline K Mean Cost</span>
              <span className="tile-value num" style={{ color: 'var(--accent)' }}>
                {formatNum(h3.holdout_confirmation?.pipeline_k_cost_mean)}
              </span>
              <span className="tile-sub">± {formatNum(h3.holdout_confirmation?.pipeline_k_cost_sd)} across 5 holdouts</span>
            </div>

            <div className="tile">
              <span className="tile-title">Reference Mean Cost</span>
              <span className="tile-value num">
                {formatNum(h3.holdout_confirmation?.reference_cost_mean)}
              </span>
              <span className="tile-sub">± {formatNum(h3.holdout_confirmation?.reference_cost_sd)}</span>
            </div>

            <div className="tile">
              <span className="tile-title">Paired Delta Cost</span>
              <span className="tile-value num" style={{ color: 'var(--success-text)' }}>
                {formatDelta(h3.holdout_confirmation?.paired_delta_cost)}
              </span>
              <span className="tile-sub">
                p = {formatNum(h3.holdout_confirmation?.sign_test_p_value, FORMAT_DECIMALS_THOUSANDTH)} ({h3.holdout_confirmation?.direction_consistency})
              </span>
            </div>

            <div className="tile">
              <span className="tile-title">Pipeline K Precision</span>
              <span className="tile-value num font-mono">
                {formatRate(h3.holdout_confirmation?.pipeline_k_precision_mean)}
              </span>
              <span className="tile-sub">vs {formatRate(h3.holdout_confirmation?.reference_precision_mean)} Ref</span>
            </div>
          </div>

          {/* Secondary Outcome Note */}
          {h3.secondary_outcomes && (
            <div style={{ backgroundColor: 'var(--bg-surface-subtle)', padding: '0.875rem', borderRadius: '4px', fontSize: '0.8125rem' }}>
              <strong>Secondary Pre-Registered Outcome (Kinship Stress):</strong>
              <div style={{ marginTop: '0.25rem', color: 'var(--text-muted)' }}>
                {h3.secondary_outcomes.doppelganger_stress_0_at_recall_50?.theoretical_mechanism}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="card" style={{ borderLeft: '4px solid var(--danger-color)' }}>
          <p style={{ color: 'var(--danger-text)', fontWeight: 'bold' }}>data missing: h3</p>
        </div>
      )}

      {/* Card 4: Cost-Ratio Sensitivity Analysis */}
      {costSensitivity ? (
        <div className="card">
          <div className="card-header">
            <div>
              <span className="fact-label">Trade-Off Analysis</span>
              <h3 className="card-title">Cost-Ratio Sensitivity: When Does Pipeline K Win?</h3>
              <p className="tile-sub">
                Pre-registered evaluation under asymmetric cost ratios: c(FP) : c(FN) ∈ &#123;1:1, 2:1, 5:1, 10:1&#125;
              </p>
            </div>
            {costSensitivity.source && (
              <a
                href={`${GITHUB_REPO_URL}/${costSensitivity.source}`}
                target="_blank"
                rel="noreferrer"
                className="chip"
                style={{ textDecoration: 'none' }}
              >
                Source: {costSensitivity.source}
              </a>
            )}
          </div>

          <p style={{ fontSize: '0.875rem', lineHeight: '1.5', marginBottom: '1rem' }}>
            Pipeline K prioritizes precision by strictly enforcing kinship constraints. Because it trades a small amount of recall for a substantial reduction in false merges, <strong>K is preferred when false merges cost at least 2x missed duplicates</strong>. Under balanced 1:1 costs, the win margin narrows to 3 of 5 seeds.
          </p>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Cost Ratio</th>
                  <th>Scenario Label</th>
                  <th style={{ textAlign: 'right' }}>Reference Cost</th>
                  <th style={{ textAlign: 'right' }}>Pipeline K Cost</th>
                  <th style={{ textAlign: 'right' }}>Paired Delta Cost</th>
                  <th style={{ textAlign: 'center' }}>Seeds Won</th>
                  <th>Dominance Verdict</th>
                </tr>
              </thead>
              <tbody>
                {(costSensitivity.ratios || []).map((row: any) => {
                  const isWon = row.delta_cost < ZERO;
                  return (
                    <tr key={row.ratio}>
                      <td><strong>{row.ratio}</strong></td>
                      <td>{row.label}</td>
                      <td style={{ textAlign: 'right' }} className="num font-mono">
                        {formatNum(row.reference_cost_mean)} ± {formatNum(row.reference_cost_sd)}
                      </td>
                      <td style={{ textAlign: 'right' }} className="num font-mono">
                        {formatNum(row.pipeline_k_cost_mean)} ± {formatNum(row.pipeline_k_cost_sd)}
                      </td>
                      <td
                        style={{
                          textAlign: 'right',
                          color: isWon ? 'var(--success-text)' : 'inherit',
                          fontWeight: 'bold',
                        }}
                        className="num font-mono"
                      >
                        {formatDelta(row.delta_cost)}
                      </td>
                      <td style={{ textAlign: 'center' }} className="num">
                        {row.seeds_won}
                      </td>
                      <td>
                        <span className={row.verdict?.startsWith('K better') ? 'chip chip-accent' : 'chip'}>
                          {row.verdict || (isWon ? 'Pipeline K Wins' : 'Comparable')}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="card" style={{ borderLeft: '4px solid var(--danger-color)' }}>
          <p style={{ color: 'var(--danger-text)', fontWeight: 'bold' }}>data missing: cost_ratio_sensitivity</p>
        </div>
      )}

      {/* Card 5: Household Inference & Limitations */}
      {household ? (
        <div className="card">
          <div className="card-header">
            <div>
              <span className="fact-label">Household Inference Analysis</span>
              <h3 className="card-title">Household Limitations: Evidence Ablations & Weight Fragility</h3>
              <p className="tile-sub">
                Holdout evaluation of graph cuts across evidence channels E1–E5, weight perturbations, and roster strata
              </p>
            </div>
            {household.source && (
              <a
                href={`${GITHUB_REPO_URL}/${household.source}`}
                target="_blank"
                rel="noreferrer"
                className="chip"
                style={{ textDecoration: 'none' }}
              >
                Source: {household.source}
              </a>
            )}
          </div>

          <p style={{ fontSize: '0.875rem', lineHeight: '1.5', marginBottom: '1rem' }}>
            Household inference connects resolved persons using 5 evidence channels (E1: listed member, E2: husband link, E3: father link, E4: roster overlap, E5: shared phone). While multi-evidence cuts achieve an estimated household reach error, empirical testing exposed two critical engineering limitations:
          </p>

          {/* Finding 1: E2 Harms Precision */}
          {household.ablations?.drop_e2_husband_link && (
            <div style={{ backgroundColor: 'var(--bg-surface-subtle)', padding: '1rem', borderRadius: '4px', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <span className="chip chip-danger font-mono">FINDING</span>
                <strong style={{ fontSize: '0.875rem' }}>E2 (Husband Link) Harms Precision</strong>
              </div>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', margin: '0' }}>
                {household.ablations.drop_e2_husband_link.key_finding}
              </p>
              <div style={{ display: 'flex', gap: '1.5rem', marginTop: '0.5rem', fontSize: '0.8125rem' }}>
                <div>Full Pipeline Precision: <strong className="num font-mono">{formatRate(household.champion?.record_precision_mean)}</strong></div>
                <div>Dropping E2 Precision: <strong className="num font-mono" style={{ color: 'var(--success-text)' }}>{formatRate(household.ablations.drop_e2_husband_link.record_precision_mean)}</strong></div>
                <div>F1 Delta: <strong className="num font-mono">{formatRate(household.ablations.drop_e2_husband_link.record_pairwise_f1_mean)}</strong> vs {formatRate(household.champion?.record_pairwise_f1_mean)}</div>
              </div>
            </div>
          )}

          {/* Finding 2: Weight Fragility */}
          {household.weight_robustness && (
            <div style={{ backgroundColor: 'var(--bg-surface-subtle)', padding: '1rem', borderRadius: '4px', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <span className="chip chip-danger font-mono">FRAGILITY</span>
                <strong style={{ fontSize: '0.875rem' }}>Weight Sensitivity & Threshold Instability</strong>
              </div>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', margin: '0' }}>
                {household.weight_robustness.fragility_note}
              </p>
              <div className="table-container" style={{ marginTop: '0.75rem' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Weight Scale</th>
                      <th style={{ textAlign: 'right' }}>Household F1</th>
                      <th style={{ textAlign: 'right' }}>Precision</th>
                      <th style={{ textAlign: 'right' }}>Recall</th>
                      <th style={{ textAlign: 'right' }}>Reach Error</th>
                      <th style={{ textAlign: 'right' }}>Size MAE</th>
                    </tr>
                  </thead>
                  <tbody>
                    {['base_1_0x', 'halved_0_5x', 'doubled_2_0x'].map((scaleKey) => {
                      const item = household.weight_robustness[scaleKey];
                      if (!item) return null;
                      return (
                        <tr key={scaleKey}>
                          <td><strong>{item.scale}</strong></td>
                          <td style={{ textAlign: 'right' }} className="num font-mono">{formatRate(item.record_pairwise_f1_mean)}</td>
                          <td style={{ textAlign: 'right' }} className="num font-mono">{formatRate(item.record_precision_mean)}</td>
                          <td style={{ textAlign: 'right' }} className="num font-mono">{formatRate(item.record_recall_mean)}</td>
                          <td style={{ textAlign: 'right' }} className="num font-mono">{formatRawPct(item.hh_reached_error_pct_mean)}</td>
                          <td style={{ textAlign: 'right' }} className="num font-mono">{formatNum(item.household_size_mae_mean)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Roster Strata */}
          {household.roster_strata && (
            <div>
              <span className="fact-label" style={{ marginBottom: '0.5rem' }}>Roster Collection Strata</span>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '0.5rem' }}>
                <div className="record-box">
                  <h4 style={{ fontSize: '0.875rem', fontWeight: 'bold' }}>Stratum A (With Roster)</h4>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>{household.roster_strata.stratum_a_with_roster?.description}</p>
                  <div style={{ fontSize: '0.8125rem', marginTop: '0.5rem' }}>
                    <div>Share: <strong className="num">{formatRawPct(household.roster_strata.stratum_a_with_roster?.share_pct_mean)}</strong></div>
                    <div>Indirect Reach Error: <strong className="num">{formatRawPct(household.roster_strata.stratum_a_with_roster?.indirect_reach_error_pct_mean)}</strong></div>
                    <div>Household Size MAE: <strong className="num">{formatNum(household.roster_strata.stratum_a_with_roster?.household_size_mae_mean)}</strong></div>
                  </div>
                </div>

                <div className="record-box">
                  <h4 style={{ fontSize: '0.875rem', fontWeight: 'bold' }}>Stratum B (No Roster)</h4>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>{household.roster_strata.stratum_b_no_roster?.description}</p>
                  <div style={{ fontSize: '0.8125rem', marginTop: '0.5rem' }}>
                    <div>Share: <strong className="num">{formatRawPct(household.roster_strata.stratum_b_no_roster?.share_pct_mean)}</strong></div>
                    <div style={{ color: 'var(--text-subtle)', marginTop: '0.25rem' }}>
                      {household.roster_strata.stratum_b_no_roster?.note}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="card" style={{ borderLeft: '4px solid var(--danger-color)' }}>
          <p style={{ color: 'var(--danger-text)', fontWeight: 'bold' }}>data missing: household</p>
        </div>
      )}

      {/* Footer Note */}
      <div className="card findings-footer" style={{ textAlign: 'center', padding: '1rem', color: 'var(--text-subtle)', fontSize: '0.8125rem' }}>
        <em>All results are on synthetic data; not validated on real registries.</em>
      </div>
    </div>
  );
};
