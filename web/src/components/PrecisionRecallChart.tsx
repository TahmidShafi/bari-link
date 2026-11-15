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
  const [containerWidth, setContainerWidth] = React.useState<number>(0);
  const markerRef = useRef<{
    group: SVGGElement;
    label: SVGTextElement;
    xApply: (v: number) => number;
  } | null>(null);

  React.useLayoutEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const updateWidth = () => {
      const next = el.clientWidth;
      if (next > 0) {
        setContainerWidth((prev) => (prev !== next ? next : prev));
      }
    };
    updateWidth();
    if (typeof ResizeObserver === 'undefined') return;
    const ro = new ResizeObserver(updateWidth);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return;
    const measuredWidth = containerRef.current.clientWidth || containerWidth;
    if (!measuredWidth) return;

    // Transform points for Observable Plot line series
    const plotPoints: Array<{
      threshold: number;
      metric: string;
      value: number;
    }> = [];

    for (const row of data) {
      plotPoints.push({
        threshold: Number(row.t_link),
        metric: 'Precision',
        value: Number(row.precision),
      });
      plotPoints.push({
        threshold: Number(row.t_link),
        metric: 'Recall',
        value: Number(row.recall),
      });
    }

    const width = measuredWidth;
    const height = 240;
    const marginTop = 20;
    const marginBottom = 40;

    const plot = Plot.plot({
      width,
      height,
      marginTop,
      marginRight: 40,
      marginBottom,
      marginLeft: 50,
      style: width < 480 ? { fontSize: '11px' } : undefined,
      x: {
        label: 'Linkage Decision Threshold (t_link)',
        domain: [2.0, 14.0],
        ticks: width < 480 ? 5 : undefined,
      },
      y: {
        label: 'Metric Value',
        domain: [0, 1.05],
        grid: true,
        tickFormat: (d: number) => `${Math.round(d * 100)}%`,
      },
      color: {
        domain: ['Precision', 'Recall'],
        range: ['#0f766e', '#525257'],
        legend: true,
      },
      marks: [
        Plot.ruleY([0]),
        // Dev frozen optimum (t=2.0)
        Plot.ruleX([2.0], {
          stroke: '#525257',
          strokeWidth: 1.5,
          strokeDasharray: '2 2',
        }),
        Plot.text([2.0], {
          x: 2.0,
          y: 0.08,
          text: () => 'selected on dev data (frozen)',
          fill: '#525257',
          textAnchor: 'start',
          dx: 6,
          fontSize: width < 480 ? 11 : 10,
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

    // Overlay live threshold marker inside the chart SVG (exclude 15x15 legend swatch SVGs)
    const svg =
      plot.tagName.toLowerCase() === 'svg'
        ? (plot as unknown as SVGSVGElement)
        : plot.querySelector('svg[viewBox]');
    const xScale = (plot as unknown as { scale?: (name: string) => { apply: (v: number) => number } }).scale?.('x');

    if (svg && xScale) {
      const ns = 'http://www.w3.org/2000/svg';
      const group = document.createElementNS(ns, 'g');
      group.setAttribute('class', 'pr-threshold-marker');

      const line = document.createElementNS(ns, 'line');
      line.setAttribute('x1', '0');
      line.setAttribute('x2', '0');
      line.setAttribute('y1', String(marginTop));
      line.setAttribute('y2', String(height - marginBottom));
      line.setAttribute('stroke', '#0f766e');
      line.setAttribute('stroke-width', '2');
      line.setAttribute('stroke-dasharray', '4 4');

      const label = document.createElementNS(ns, 'text');
      label.setAttribute('x', '0');
      label.setAttribute('y', String(marginTop + 56));
      label.setAttribute('fill', '#0d5c56');
      label.setAttribute('font-size', '11');
      label.setAttribute('font-weight', '600');

      group.appendChild(line);
      group.appendChild(label);
      svg.appendChild(group);

      markerRef.current = {
        group,
        label,
        xApply: (v: number) => xScale.apply(v),
      };
    } else {
      markerRef.current = null;
    }

    return () => {
      markerRef.current = null;
      plot.remove();
    };
  }, [data, containerWidth]);

  useEffect(() => {
    const marker = markerRef.current;
    if (!marker) return;
    const x = marker.xApply(currentThreshold);
    if (!Number.isFinite(x)) return;
    marker.group.style.transform = `translateX(${x}px)`;
    marker.label.textContent = `t = ${currentThreshold.toFixed(1)}`;
    if (currentThreshold > 12.5) {
      marker.label.setAttribute('text-anchor', 'end');
      marker.label.setAttribute('dx', '-5');
    } else {
      marker.label.setAttribute('text-anchor', 'start');
      marker.label.setAttribute('dx', '5');
    }
  }, [currentThreshold, data, containerWidth]);

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Precision & Recall vs. Threshold</h3>
        <span className="fact-label">Trade-off Curve across Threshold Grid</span>
      </div>
      <div ref={containerRef} style={{ width: '100%', minHeight: '240px' }} />
      <p style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
        Holdout-optimal thresholds can differ from the dev-selected one; the frozen point is reported to avoid tuning on test data.
      </p>
    </div>
  );
};

