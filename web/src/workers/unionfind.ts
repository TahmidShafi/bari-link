/**
 * Pure, deterministic Disjoint Set Union (Union-Find) algorithm.
 * Path compression + union by rank.
 * STRICT RULE: No ground truth logic or imports.
 */

export interface Edge {
  u: string;
  v: string;
  weight: number;
}

export class UnionFind {
  private parent: Map<string, string>;
  private rank: Map<string, number>;

  constructor(elements: string[]) {
    this.parent = new Map<string, string>();
    this.rank = new Map<string, number>();
    for (const el of elements) {
      this.parent.set(el, el);
      this.rank.set(el, 0);
    }
  }

  public find(x: string): string {
    let root = x;
    while (this.parent.get(root) !== root) {
      root = this.parent.get(root)!;
    }
    // Path compression
    let curr = x;
    while (curr !== root) {
      const next = this.parent.get(curr)!;
      this.parent.set(curr, root);
      curr = next;
    }
    return root;
  }

  public union(x: string, y: string): boolean {
    const rootX = this.find(x);
    const rootY = this.find(y);
    if (rootX === rootY) return false;

    const rankX = this.rank.get(rootX)!;
    const rankY = this.rank.get(rootY)!;

    if (rankX < rankY) {
      this.parent.set(rootX, rootY);
    } else if (rankX > rankY) {
      this.parent.set(rootY, rootX);
    } else {
      // Deterministic tie break: alphabetical on root ID
      if (rootX < rootY) {
        this.parent.set(rootY, rootX);
        this.rank.set(rootX, rankX + 1);
      } else {
        this.parent.set(rootX, rootY);
        this.rank.set(rootY, rankY + 1);
      }
    }
    return true;
  }
}

/**
 * Run union-find over candidate edges with weight >= threshold.
 * Returns map of record_id -> canonical_cluster_id.
 */
export function clusterEdgesByThreshold(
  allRecordIds: string[],
  edges: Edge[],
  threshold: number
): Map<string, string> {
  const dsu = new UnionFind(allRecordIds);

  // Filter and sort edges deterministically
  const activeEdges = edges
    .filter((e) => e.weight >= threshold)
    .sort((a, b) => {
      if (b.weight !== a.weight) return b.weight - a.weight;
      if (a.u !== b.u) return a.u.localeCompare(b.u);
      return a.v.localeCompare(b.v);
    });

  for (const edge of activeEdges) {
    dsu.union(edge.u, edge.v);
  }

  const clusters = new Map<string, string>();
  for (const id of allRecordIds) {
    const root = dsu.find(id);
    clusters.set(id, `raw_${root}`);
  }

  return clusters;
}
