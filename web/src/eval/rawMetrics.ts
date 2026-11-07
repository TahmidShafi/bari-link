/**
 * Pure in-browser metric calculation for "Raw Splink edges (no resolution)" mode.
 * Evaluates union-find clusters against evaluation ground truth.
 */

import type { RecordLabel } from './evalData';

export interface RawMetricsResult {
  precision: number;
  recall: number;
  f1: number;
  expected_cost: number;
  false_merge_clusters: number;
  split_persons: number;
  dedup_reach: number;
  true_reach: number;
  naive_reach: number;
  doppelganger_false_merge_rate: number;
  review_queue_size: number;
}

export function computeRawMetrics(
  clusters: Map<string, string>,
  labelsMap: Map<string, RecordLabel>,
  doppelgangerPersonPairs?: [string, string][]
): RawMetricsResult {
  // Total true pairs in population
  const personDistribution = new Map<string, number>();
  for (const label of labelsMap.values()) {
    personDistribution.set(
      label.person_id,
      (personDistribution.get(label.person_id) || 0) + 1
    );
  }

  let totalTruePairs = 0;
  for (const count of personDistribution.values()) {
    totalTruePairs += (count * (count - 1)) / 2;
  }

  const trueReach = personDistribution.size;
  const naiveReach = labelsMap.size;

  // Group records by predicted cluster_id
  const clusterMembers = new Map<string, string[]>();
  for (const [recordId, clusterId] of clusters.entries()) {
    if (!clusterMembers.has(clusterId)) {
      clusterMembers.set(clusterId, []);
    }
    clusterMembers.get(clusterId)!.push(recordId);
  }

  const dedupReach = clusterMembers.size;

  let clusterTp = 0;
  let clusterFp = 0;
  let falseMergeClusters = 0;

  // Track which clusters each person appears in
  const personClusters = new Map<string, Set<string>>();

  for (const [clusterId, memberIds] of clusterMembers.entries()) {
    const pCounts = new Map<string, number>();

    for (const rid of memberIds) {
      const label = labelsMap.get(rid);
      if (label) {
        pCounts.set(label.person_id, (pCounts.get(label.person_id) || 0) + 1);

        if (!personClusters.has(label.person_id)) {
          personClusters.set(label.person_id, new Set());
        }
        personClusters.get(label.person_id)!.add(clusterId);
      }
    }

    if (memberIds.length > 1) {
      const cSize = memberIds.length;
      const cPairs = (cSize * (cSize - 1)) / 2;

      let cTrue = 0;
      for (const count of pCounts.values()) {
        cTrue += (count * (count - 1)) / 2;
      }

      clusterTp += cTrue;
      clusterFp += cPairs - cTrue;
    }

    if (pCounts.size > 1) {
      falseMergeClusters++;
    }
  }

  // Count split persons (appearing in > 1 cluster)
  let splitPersons = 0;
  for (const cSet of personClusters.values()) {
    if (cSet.size > 1) {
      splitPersons++;
    }
  }

  // Precision, Recall, F1
  const precision =
    clusterTp + clusterFp > 0 ? clusterTp / (clusterTp + clusterFp) : 1.0;
  const recall = totalTruePairs > 0 ? clusterTp / totalTruePairs : 0.0;
  const f1 =
    precision + recall > 0 ? (2 * precision * recall) / (precision + recall) : 0.0;

  // Expected operational cost (5:1 penalty)
  const expectedCost = 5.0 * falseMergeClusters + 1.0 * splitPersons;

  // Doppelganger false merge rate if pairs provided
  let doppelRate = 0.0;
  if (doppelgangerPersonPairs && doppelgangerPersonPairs.length > 0) {
    let mergedCount = 0;
    for (const [p1, p2] of doppelgangerPersonPairs) {
      const clusters1 = personClusters.get(p1);
      const clusters2 = personClusters.get(p2);
      if (clusters1 && clusters2) {
        let sharesCluster = false;
        for (const c of clusters1) {
          if (clusters2.has(c)) {
            sharesCluster = true;
            break;
          }
        }
        if (sharesCluster) mergedCount++;
      }
    }
    doppelRate = mergedCount / doppelgangerPersonPairs.length;
  }

  return {
    precision,
    recall,
    f1,
    expected_cost: expectedCost,
    false_merge_clusters: falseMergeClusters,
    split_persons: splitPersons,
    dedup_reach: dedupReach,
    true_reach: trueReach,
    naive_reach: naiveReach,
    doppelganger_false_merge_rate: doppelRate,
    review_queue_size: 0,
  };
}

