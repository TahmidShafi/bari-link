import React from 'react';
import type { WaterfallResult } from '../data/waterfall';

interface PairWaterfallProps {
  waterfall: WaterfallResult;
}

export const PairWaterfall: React.FC<PairWaterfallProps> = ({ waterfall }) => {

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h3 className="card-title">Fellegi-Sunter Match-Weight Waterfall</h3>
          <p className="tile-sub">
            Log-odds decomposition: Prior odds + sum of comparison evidence contributions = final decision weight
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <span className="fact-label">Final Match Probability</span>
          <div className="fact-value num" style={{ color: 'var(--accent)' }}>
            {(waterfall.finalProbability * 100).toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: '22%' }}>Comparison Step</th>
              <th style={{ width: '38%' }}>Level Description</th>
              <th style={{ width: '15%', textAlign: 'right' }}>Evidence (log₂ BF)</th>
              <th style={{ width: '15%', textAlign: 'right' }}>Running Weight</th>
              <th style={{ width: '10%', textAlign: 'right' }}>Posterior P</th>
            </tr>
          </thead>
          <tbody>
            {/* Prior Step */}
            <tr style={{ backgroundColor: 'var(--bg-surface-subtle)', fontWeight: 600 }}>
              <td>Prior Log-Odds</td>
              <td style={{ color: 'var(--text-subtle)' }}>
                Baseline matching odds: P(match) = {waterfall.priorProbability.toExponential(3)}
              </td>
              <td style={{ textAlign: 'right' }} className="num font-mono">
                {waterfall.priorLog2Odds.toFixed(2)}
              </td>
              <td style={{ textAlign: 'right' }} className="num font-mono">
                {waterfall.priorLog2Odds.toFixed(2)}
              </td>
              <td style={{ textAlign: 'right' }} className="num">
                {(waterfall.priorProbability * 100).toFixed(4)}%
              </td>
            </tr>

            {/* Individual Evidence Steps */}
            {waterfall.steps.map((step, idx) => {
              const isPositive = step.log2_bf >= 0;
              const bfBadgeColor = isPositive ? 'var(--success-text)' : 'var(--danger-text)';
              const bfBadgeBg = isPositive ? 'var(--success-bg)' : 'var(--danger-bg)';
              const bfBorder = isPositive ? 'var(--success-border)' : 'var(--danger-border)';

              return (
                <tr key={idx}>
                  <td>
                    <strong>{step.name}</strong>
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>{step.label}</td>
                  <td style={{ textAlign: 'right' }}>
                    <span
                      className="chip num font-mono"
                      style={{
                        backgroundColor: bfBadgeBg,
                        color: bfBadgeColor,
                        borderColor: bfBorder,
                        fontWeight: 700,
                      }}
                    >
                      {step.log2_bf >= 0 ? `+${step.log2_bf.toFixed(2)}` : step.log2_bf.toFixed(2)}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right' }} className="num font-mono">
                    {step.running_weight.toFixed(2)}
                  </td>
                  <td style={{ textAlign: 'right' }} className="num">
                    {(step.probability * 100).toFixed(2)}%
                  </td>
                </tr>
              );
            })}

            {/* Final Total Step */}
            <tr
              style={{
                backgroundColor: 'var(--bg-surface-subtle)',
                fontWeight: 700,
                borderTop: '2px solid var(--border-strong)',
              }}
            >
              <td>Final Match Weight</td>
              <td>Total cumulative Fellegi-Sunter weight</td>
              <td style={{ textAlign: 'right' }} className="num font-mono">
                {waterfall.finalWeight >= 0
                  ? `+${waterfall.finalWeight.toFixed(2)}`
                  : waterfall.finalWeight.toFixed(2)}
              </td>
              <td style={{ textAlign: 'right', color: 'var(--accent)' }} className="num font-mono">
                {waterfall.finalWeight.toFixed(2)}
              </td>
              <td style={{ textAlign: 'right', color: 'var(--accent)' }} className="num">
                {(waterfall.finalProbability * 100).toFixed(2)}%
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
