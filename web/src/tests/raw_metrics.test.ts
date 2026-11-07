import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';
import { clusterEdgesByThreshold, type Edge } from '../workers/unionfind';
import { computeRawMetrics } from '../eval/rawMetrics';
import type { RecordLabel } from '../eval/evalData';

describe('Raw Splink Metrics In-Browser Evaluation', () => {
  const fixturePath = path.resolve(__dirname, 'fixtures/raw_eval_fixture.json');
  const fixture = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));

  const recordIds: string[] = fixture.record_ids;
  const edges: Edge[] = fixture.pairs;
  const labelsMap = new Map<string, RecordLabel>();
  for (const l of fixture.record_labels) {
    labelsMap.set(l.record_id, l);
  }
  const doppelPairs: [string, string][] = fixture.doppel_pairs;
  const thresholdRows: any[] = fixture.threshold_rows;

  it('loads all 25 threshold grid rows from fixture', () => {
    expect(thresholdRows).toHaveLength(25);
  });

  it('matches Python raw variant across all 25 grid thresholds (counts exact, rates within 1e-9)', () => {
    for (const expectedRow of thresholdRows) {
      const t = expectedRow.t_link;

      // 1. Run browser union-find clustering over pairs edges with weight >= t
      const clusters = clusterEdgesByThreshold(recordIds, edges, t);

      // 2. Compute in-browser evaluation metrics against eval labels
      const browserMetrics = computeRawMetrics(clusters, labelsMap, doppelPairs);

      // 3. Assert counts exact
      expect(browserMetrics.dedup_reach).toBe(expectedRow.dedup_reach);
      expect(browserMetrics.true_reach).toBe(expectedRow.true_reach);
      expect(browserMetrics.naive_reach).toBe(expectedRow.naive_reach);
      expect(browserMetrics.false_merge_clusters).toBe(expectedRow.false_merge_clusters);

      // 4. Assert rates within 1e-9 tolerance
      expect(Math.abs(browserMetrics.precision - expectedRow.precision)).toBeLessThan(1e-9);
      expect(Math.abs(browserMetrics.recall - expectedRow.recall)).toBeLessThan(1e-9);
      expect(Math.abs(browserMetrics.f1 - expectedRow.f1)).toBeLessThan(1e-9);
      expect(Math.abs(browserMetrics.expected_cost - expectedRow.expected_cost)).toBeLessThan(1e-9);
      expect(
        Math.abs(browserMetrics.doppelganger_false_merge_rate - expectedRow.doppelganger_false_merge_rate)
      ).toBeLessThan(1e-9);
    }
  });
});

