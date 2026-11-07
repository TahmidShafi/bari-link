/**
 * Web Worker for live union-find clustering over raw candidate pairs.
 * Pure message handling; isolated from ground truth datasets.
 */

import { clusterEdgesByThreshold, type Edge } from './unionfind';

export interface WorkerRequest {
  type: 'CLUSTER';
  allRecordIds: string[];
  edges: Edge[];
  threshold: number;
}

export interface WorkerResponse {
  type: 'CLUSTER_SUCCESS';
  threshold: number;
  clusters: Record<string, string>;
}

self.onmessage = (event: MessageEvent<WorkerRequest>) => {
  const { type, allRecordIds, edges, threshold } = event.data;
  if (type === 'CLUSTER') {
    const clusterMap = clusterEdgesByThreshold(allRecordIds, edges, threshold);
    const obj: Record<string, string> = {};
    for (const [k, v] of clusterMap.entries()) {
      obj[k] = v;
    }

    const response: WorkerResponse = {
      type: 'CLUSTER_SUCCESS',
      threshold,
      clusters: obj,
    };
    self.postMessage(response);
  }
};
