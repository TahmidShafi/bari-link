import React, { useEffect, useRef } from 'react';
import * as Plot from '@observablehq/plot';
import type { ThresholdTableRow } from '../eval/evalData';

interface PrecisionRecallChartProps {
  data: ThresholdTableRow[];
  currentThreshold: number;
}

export const PrecisionRecallChart: React.FC<PrecisionRecallChartProps> = ({
  data,
  currentThreshold,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return;

    // Transform points for Observable Plot line series
    const plotPoints: Array<{
      threshold: number;
      metric: string;
      value: number;
    }> = [];

    for (const row of data) {
      plotPoints.push({
        threshold: row.t_link,
        metric: 'Precision',
        value: row.precision,
      });
      plotPoints.push({
        threshold: row.t_link,
        metric: 'Recall',
        value: row.recall,
      });
    }

    const width = containerRef.current.clientWidth || 600;

    const plot = Plot.plot({
      width,
      height: 240,
      marginTop: 20,
      marginRight: 40,
      marginBottom: 40,
      marginLeft: 50,
      x: {
        label: 'Linkage Decision Threshold (t_link)',
        domain: [2.0, 14.0],
      },
      y: {
        label: 'Metric Value',
        domain: [0, 1.05],
        grid: true,
        percent: true,
      },
      color: {
        domain: ['Precision', 'Recall'],
        range: ['#0f766e', '#f59e0b'],
        legend: true,
      },
      marks: [
        Plot.ruleY([0]),
        // Current threshold vertical line
        Plot.ruleX([currentThreshold], {
          stroke: '#dc2626',
          strokeWidth: 2,
          strokeDasharray: '4 4',
        }),
        Plot.text([currentThreshold], {
          x: currentThreshold,
          y: 1.02,
          text: (d) => `t = ${d.toFixed(1)}`,
          fill: '#dc2626',
          textAnchor: 'start',
          dx: 5,
          fontSize: 11,
          fontWeight: 'bold',
        }),
        // Precision & Recall Lines
        Plot.lineY(plotPoints, {
          x: 'threshold',
          y: 'value',
          stroke: 'metric',
          strokeWidth: 2.5,
          curve: 'monotone-x',
        }),
        // Data dots
        Plot.dot(plotPoints, {
          x: 'threshold',
          y: 'value',
          fill: 'metric',
          r: 3,
        }),
      ],
    });

    containerRef.current.replaceChildren(plot);

    return () => {
      plot.remove();
    };
  }, [data, currentThreshold]);

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Precision & Recall vs. Threshold</h3>
        <span className="fact-label">Trade-off Curve across Threshold Grid</span>
      </div>
      <div ref={containerRef} style={{ width: '100%', minHeight: '240px' }} />
    </div>
  );
};

