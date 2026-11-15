import React from 'react';
import { useTweenedNumber } from '../eval/tweenNumber';

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

  const tweenDedupReach = useTweenedNumber(metrics.dedupReach) ?? metrics.dedupReach;
  const tweenPrecision = useTweenedNumber(metrics.precision) ?? metrics.precision;
  const tweenF1 = useTweenedNumber(metrics.f1) ?? metrics.f1;
  const tweenFalseMergeClusters =
    useTweenedNumber(metrics.falseMergeClusters) ?? metrics.falseMergeClusters;
  const tweenDoppelgangerFmRate =
    useTweenedNumber(metrics.doppelgangerFmRate) ?? metrics.doppelgangerFmRate;
  const tweenExpectedCost = useTweenedNumber(metrics.expectedCost) ?? metrics.expectedCost;
  const tweenReviewQueueSize =
    useTweenedNumber(metrics.reviewQueueSize) ?? metrics.reviewQueueSize;

  return (
    <div className="tiles-grid" aria-label="Live Deduplication Metrics">
      {/* 1. Deduplicated Reach */}
      <div className="tile">
        <span className="tile-title">Deduplicated Reach</span>
        <span
          className="tile-value num"
          aria-label={metrics.dedupReach.toLocaleString()}
        >
          {Math.round(tweenDedupReach).toLocaleString()}
        </span>
        <span className="tile-sub num" style={{ color: 'var(--text-muted)' }}>
          {reachErrorPct >= 0 ? `+${reachErrorPct.toFixed(1)}%` : `${reachErrorPct.toFixed(1)}%`} vs true ({metrics.trueReach.toLocaleString()})
        </span>
      </div>

      {/* 2. Cluster Precision */}
      <div className="tile">
        <span className="tile-title">Cluster Precision</span>
        <span
          className="tile-value num"
          aria-label={`${(metrics.precision * 100).toFixed(1)}%`}
        >
          {(tweenPrecision * 100).toFixed(1)}%
        </span>
        <span className="tile-sub num">
          P: {(metrics.precision * 100).toFixed(1)}% | R: {(metrics.recall * 100).toFixed(1)}%
        </span>
      </div>

      {/* 3. Cluster F1 Score */}
      <div className="tile">
        <span className="tile-title">Cluster F1 Score</span>
        <span
          className="tile-value num"
          aria-label={metrics.f1.toFixed(3)}
        >
          {tweenF1.toFixed(3)}
        </span>
        <span className="tile-sub num">Harmonic mean of P & R</span>
      </div>

      {/* 4. False-Merge Clusters */}
      <div className="tile">
        <span className="tile-title">False-Merge Clusters</span>
        <span
          className="tile-value num"
          aria-label={metrics.falseMergeClusters.toLocaleString()}
          style={{
            color: metrics.falseMergeClusters > 0 ? 'var(--danger-text)' : 'var(--accent-text)',
          }}
        >
          {Math.round(tweenFalseMergeClusters).toLocaleString()}
        </span>
        <span className="tile-sub">clusters containing &gt; 1 person</span>
      </div>

      {/* 5. Doppelganger FM Rate */}
      <div className="tile">
        <span className="tile-title">Doppelganger FM Rate</span>
        <span
          className="tile-value num"
          aria-label={`${(metrics.doppelgangerFmRate * 100).toFixed(2)}%`}
        >
          {(tweenDoppelgangerFmRate * 100).toFixed(2)}%
        </span>
        <span className="tile-sub">Hard negative name collisions</span>
      </div>

      {/* 6. Expected Cost (5:1) */}
      <div className="tile">
        <span className="tile-title">Expected Cost (5:1)</span>
        <span
          className="tile-value num"
          style={{ color: 'var(--accent)' }}
          aria-label={metrics.expectedCost.toFixed(0)}
        >
          {tweenExpectedCost.toFixed(0)}
        </span>
        <span className="tile-sub num">5·FM + 1·MD penalty</span>
      </div>

      {/* 7. Review-Queue Size */}
      <div className="tile">
        <span className="tile-title">Review-Queue Size</span>
        <span
          className="tile-value num"
          aria-label={metrics.reviewQueueSize.toLocaleString()}
        >
          {Math.round(tweenReviewQueueSize).toLocaleString()}
        </span>
        <span className="tile-sub">Pairs queued for review</span>
      </div>
    </div>
  );
};

