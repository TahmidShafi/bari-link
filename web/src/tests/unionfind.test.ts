import { describe, it, expect } from 'vitest';
import { UnionFind, clusterEdgesByThreshold, type Edge } from '../workers/unionfind';

describe('UnionFind (DSU)', () => {
  it('initializes each element as its own root', () => {
    const dsu = new UnionFind(['a', 'b', 'c']);
    expect(dsu.find('a')).toBe('a');
    expect(dsu.find('b')).toBe('b');
    expect(dsu.find('c')).toBe('c');
  });

  it('unions two elements and preserves transitivity', () => {
    const dsu = new UnionFind(['a', 'b', 'c', 'd']);
    expect(dsu.union('a', 'b')).toBe(true);
    expect(dsu.find('a')).toBe(dsu.find('b'));

    // Redundant union returns false
    expect(dsu.union('a', 'b')).toBe(false);

    // Transitive union: b and c -> a, b, c in same cluster
    expect(dsu.union('b', 'c')).toBe(true);
    expect(dsu.find('a')).toBe(dsu.find('c'));

    // d remains isolated
    expect(dsu.find('d')).toBe('d');
    expect(dsu.find('d')).not.toBe(dsu.find('a'));
  });

  it('performs deterministic tie-breaking regardless of call order', () => {
    const dsu1 = new UnionFind(['x', 'y']);
    dsu1.union('x', 'y');

    const dsu2 = new UnionFind(['x', 'y']);
    dsu2.union('y', 'x');

    expect(dsu1.find('x')).toBe(dsu2.find('x'));
    expect(dsu1.find('y')).toBe(dsu2.find('y'));
  });

  it('filters edges by threshold in clusterEdgesByThreshold', () => {
    const records = ['r1', 'r2', 'r3', 'r4'];
    const edges: Edge[] = [
      { u: 'r1', v: 'r2', weight: 5.0 },
      { u: 'r2', v: 'r3', weight: 2.0 },
      { u: 'r3', v: 'r4', weight: 8.0 },
    ];

    // High threshold: only r3-r4 edge active
    const highThreshClusters = clusterEdgesByThreshold(records, edges, 7.0);
    expect(highThreshClusters.get('r1')).not.toBe(highThreshClusters.get('r2'));
    expect(highThreshClusters.get('r3')).toBe(highThreshClusters.get('r4'));

    // Low threshold: all edges active -> single cluster
    const lowThreshClusters = clusterEdgesByThreshold(records, edges, 1.0);
    const root1 = lowThreshClusters.get('r1');
    expect(lowThreshClusters.get('r2')).toBe(root1);
    expect(lowThreshClusters.get('r3')).toBe(root1);
    expect(lowThreshClusters.get('r4')).toBe(root1);
  });
});

