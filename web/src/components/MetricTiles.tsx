import React from 'react';

export interface DisplayMetrics {
  dedupReach: number;
  trueReach: number;
  precision: number;
  recall: number;
  f1: number;
  falseMergeClusters: number;
  doppelgangerFmRate: number;
  expectedCost: number;
  reviewQueueSize: number;
}

interface MetricTilesProps {
  metrics: DisplayMetrics | null;
}

export const MetricTiles: React.FC<MetricTilesProps> = ({ metrics }) => {
  if (!metrics) {
    return (
      <div className="tiles-grid" aria-busy="true">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="tile">
            <span className="tile-title">Loading...</span>
            <span className="tile-value">—</span>
          </div>
        ))}
      </div>
    );
  }

  const reachErrorPct =
    metrics.trueReach > 0
      ? ((metrics.dedupReach - metrics.trueReach) / metrics.trueReach) * 100
      : 0;

  const reachErrorColor =
    Math.abs(reachErrorPct) <= 2.0
      ? 'var(--success-text)'
      : Math.abs(reachErrorPct) <= 5.0
      ? 'var(--accent-text)'
      : 'var(--danger-text)';

  return (
    <div className="tiles-grid" aria-label="Live Deduplication Metrics">
      {/* 1. Deduplicated Reach */}
      <div className="tile">
        <span className="tile-title">Deduplicated Reach</span>
        <span className="tile-value num">{metrics.dedupReach.toLocaleString()}</span>
        <span className="tile-sub num" style={{ color: reachErrorColor, fontWeight: 600 }}>
          {reachErrorPct >= 0 ? `+${reachErrorPct.toFixed(1)}%` : `${reachErrorPct.toFixed(1)}%`} vs true ({metrics.trueReach.toLocaleString()})
        </span>
      </div>

      {/* 2. Cluster Precision */}
      <div className="tile">
        <span className="tile-title">Cluster Precision</span>
        <span
          className="tile-value num"
          style={{
            color: metrics.precision >= 0.95 ? 'var(--success-text)' : 'inherit',
          }}
        >
          {(metrics.precision * 100).toFixed(1)}%
        </span>
        <span className="tile-sub num">
          P: {(metrics.precision * 100).toFixed(1)}% | R: {(metrics.recall * 100).toFixed(1)}%
        </span>
      </div>

      {/* 3. Cluster F1 Score */}
      <div className="tile">
        <span className="tile-title">Cluster F1 Score</span>
        <span className="tile-value num">{metrics.f1.toFixed(3)}</span>
        <span className="tile-sub num">Harmonic mean of P & R</span>
      </div>

      {/* 4. False-Merge Clusters */}
      <div className="tile">
        <span className="tile-title">False-Merge Clusters</span>
        <span
          className="tile-value num"
          style={{
            color: metrics.falseMergeClusters > 0 ? 'var(--danger-text)' : 'var(--success-text)',
          }}
        >
          {metrics.falseMergeClusters.toLocaleString()}
        </span>
        <span className="tile-sub">Distinct persons merged</span>
      </div>

      {/* 5. Doppelganger FM Rate */}
      <div className="tile">
        <span className="tile-title">Doppelganger FM Rate</span>
        <span className="tile-value num">
          {(metrics.doppelgangerFmRate * 100).toFixed(2)}%
        </span>
        <span className="tile-sub">Hard negative name collisions</span>
      </div>

      {/* 6. Expected Cost (5:1) */}
      <div className="tile">
        <span className="tile-title">Expected Cost (5:1)</span>
        <span className="tile-value num" style={{ color: 'var(--accent)' }}>
          {metrics.expectedCost.toFixed(0)}
        </span>
        <span className="tile-sub num">5·FM + 1·MD penalty</span>
      </div>
    </div>
  );
};

