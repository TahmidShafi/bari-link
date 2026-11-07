import React, { useEffect, useState, useRef, useTransition } from 'react';
import { HeaderFacts } from '../components/HeaderFacts';
import { ThresholdSlider } from '../components/ThresholdSlider';
import { ModeSwitch, type PipelineMode } from '../components/ModeSwitch';
import { MetricTiles, type DisplayMetrics } from '../components/MetricTiles';
import { PrecisionRecallChart } from '../components/PrecisionRecallChart';
import { FalseMergeErrors } from '../components/FalseMergeErrors';
import {
  getThresholdTable,
  getRecordLabelsMap,
  type ThresholdTableRow,
} from '../eval/evalData';
import {
  getAllPairs,
  getAllRecordIds,
  getResolvedClusters,
} from '../data/queries';
import { computeRawMetrics } from '../eval/rawMetrics';
import type { CandidatePair } from '../data/types';

export const Overview: React.FC = () => {
  const [threshold, setThreshold] = useState<number>(2.0);
  const [mode, setMode] = useState<PipelineMode>('constraint');

  // Precomputed table data for chart and resolved modes
  const [tableRows, setTableRows] = useState<ThresholdTableRow[]>([]);
  const [activeMetrics, setActiveMetrics] = useState<DisplayMetrics | null>(null);
  const [clusterMap, setClusterMap] = useState<Map<string, string>>(new Map());
  const [loading, setLoading] = useState(true);

  // Cached pairs and records for live union-find raw mode
  const rawPairsRef = useRef<CandidatePair[] | null>(null);
  const rawRecordIdsRef = useRef<string[] | null>(null);
  const unionWorkerRef = useRef<Worker | null>(null);

  const [, startTransition] = useTransition();

  // Initialize Worker for raw Splink live union-find
  useEffect(() => {
    const worker = new Worker(
      new URL('../workers/unionfind.worker.ts', import.meta.url),
      { type: 'module' }
    );
    unionWorkerRef.current = worker;

    return () => {
      worker.terminate();
    };
  }, []);

  // Load precomputed table rows when mode changes
  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    getThresholdTable(mode)
      .then((rows) => {
        if (isMounted) {
          setTableRows(rows);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load threshold table:', err);
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [mode]);

  // Update live tiles when threshold or mode changes
  useEffect(() => {
    const startTime = performance.now();

    if (mode === 'constraint' || mode === 'no_constraint') {
      // Resolved modes: instantaneous lookup from precomputed threshold table
      const matchedRow = tableRows.find(
        (r) => Math.abs(r.t_link - threshold) < 0.001
      );

      if (matchedRow) {
        setActiveMetrics({
          dedupReach: matchedRow.dedup_reach,
          trueReach: matchedRow.true_reach,
          precision: matchedRow.precision,
          recall: matchedRow.recall,
          f1: matchedRow.f1,
          falseMergeClusters: matchedRow.false_merge_clusters,
          doppelgangerFmRate: matchedRow.doppelganger_false_merge_rate,
          expectedCost: matchedRow.expected_cost,
          reviewQueueSize: matchedRow.review_queue_size,
        });
      }

      // Preload cluster assignments for error inspector
      getResolvedClusters(threshold, mode).then((cmap) => {
        setClusterMap(cmap);
      });

      const latency = performance.now() - startTime;
      if (latency > 0) {
        // Verified < 100ms
        // console.debug(`Resolved mode slider update: ${latency.toFixed(2)}ms`);
      }
    } else {
      // Raw mode: execute live union-find in worker and compute metrics in browser
      const runRawMode = async () => {
        if (!rawPairsRef.current) {
          rawPairsRef.current = await getAllPairs();
        }
        if (!rawRecordIdsRef.current) {
          rawRecordIdsRef.current = await getAllRecordIds();
        }

        const worker = unionWorkerRef.current;
        if (!worker) return;

        const edges = rawPairsRef.current.map((p) => ({
          u: p.record_id_l,
          v: p.record_id_r,
          weight: p.match_weight,
        }));

        const handleWorkerMessage = async (e: MessageEvent) => {
          if (
            e.data.type === 'CLUSTER_SUCCESS' &&
            Math.abs(e.data.threshold - threshold) < 0.001
          ) {
            worker.removeEventListener('message', handleWorkerMessage);
            const clusterObj: Record<string, string> = e.data.clusters;
            const cmap = new Map<string, string>(Object.entries(clusterObj));
            setClusterMap(cmap);

            const labels = await getRecordLabelsMap();
            const metrics = computeRawMetrics(cmap, labels);

            startTransition(() => {
              setActiveMetrics({
                dedupReach: metrics.dedup_reach,
                trueReach: metrics.true_reach,
                precision: metrics.precision,
                recall: metrics.recall,
                f1: metrics.f1,
                falseMergeClusters: metrics.false_merge_clusters,
                doppelgangerFmRate: metrics.doppelganger_false_merge_rate,
                expectedCost: metrics.expected_cost,
                reviewQueueSize: metrics.review_queue_size,
              });
            });
          }
        };

        worker.addEventListener('message', handleWorkerMessage);
        worker.postMessage({
          type: 'CLUSTER',
          allRecordIds: rawRecordIdsRef.current,
          edges,
          threshold,
        });
      };

      runRawMode();
    }
  }, [threshold, mode, tableRows]);

  return (
    <div>
      <HeaderFacts />
      {loading && <div className="tile-sub" style={{ marginBottom: '0.5rem' }}>Loading evaluation model data...</div>}

      <div className="controls-panel">
        <ThresholdSlider
          value={threshold}
          onChange={(val) => setThreshold(val)}
        />
        <ModeSwitch
          currentMode={mode}
          onChange={(m) => setMode(m)}
        />
      </div>

      <MetricTiles metrics={activeMetrics} />

      <PrecisionRecallChart
        data={tableRows}
        currentThreshold={threshold}
      />

      <FalseMergeErrors
        clusterMap={clusterMap}
        threshold={threshold}
      />
    </div>
  );
};
