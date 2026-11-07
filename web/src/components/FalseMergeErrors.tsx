import React, { useEffect, useState } from 'react';
import { getRecordLabelsMap } from '../eval/evalData';
import { searchRecords } from '../data/queries';
import { navigateTo } from '../router';
import type { RecordEntry } from '../data/types';

interface FalseMergeErrorsProps {
  clusterMap: Map<string, string>;
  threshold: number;
}

interface FalseMergeClusterItem {
  clusterId: string;
  records: RecordEntry[];
  personIds: string[];
}

export const FalseMergeErrors: React.FC<FalseMergeErrorsProps> = ({
  clusterMap,
  threshold,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [errorClusters, setErrorClusters] = useState<FalseMergeClusterItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen || clusterMap.size === 0) return;

    let isMounted = true;
    setLoading(true);

    getRecordLabelsMap()
      .then(async (labelsMap) => {
        // Group records by cluster
        const clusterMembers = new Map<string, string[]>();
        for (const [rid, cid] of clusterMap.entries()) {
          if (!clusterMembers.has(cid)) clusterMembers.set(cid, []);
          clusterMembers.get(cid)!.push(rid);
        }

        // Identify false merges (clusters with > 1 distinct person_id)
        const fmList: Array<{ clusterId: string; recordIds: string[]; personIds: string[] }> = [];
        for (const [cid, rids] of clusterMembers.entries()) {
          const pSet = new Set<string>();
          for (const rid of rids) {
            const l = labelsMap.get(rid);
            if (l) pSet.add(l.person_id);
          }
          if (pSet.size > 1) {
            fmList.push({
              clusterId: cid,
              recordIds: rids,
              personIds: Array.from(pSet),
            });
          }
        }

        // Limit to top 10 false merge clusters
        const topFm = fmList.slice(0, 10);

        // Fetch record details
        const recList = await searchRecords('', 5000);
        const recMap = new Map<string, RecordEntry>();
        for (const r of recList) {
          recMap.set(r.record_id, r);
        }

        const items: FalseMergeClusterItem[] = topFm.map((fm) => ({
          clusterId: fm.clusterId,
          personIds: fm.personIds,
          records: fm.recordIds.map((rid) => recMap.get(rid)!).filter(Boolean),
        }));

        if (isMounted) {
          setErrorClusters(items);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Error finding false merges:', err);
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen, clusterMap, threshold]);

  return (
    <div className="card" style={{ marginTop: '1.5rem' }}>
      <div className="card-header" style={{ marginBottom: isOpen ? '1rem' : 0, borderBottom: isOpen ? '1px solid var(--border-subtle)' : 'none' }}>
        <div>
          <h3 className="card-title">False-Merge Error Clusters Inspector</h3>
          <p className="tile-sub">
            Clusters containing records from multiple distinct individuals at <em>t</em><sub>link</sub> = {threshold.toFixed(1)}
          </p>
        </div>
        <button
          type="button"
          className="mode-btn active"
          onClick={() => setIsOpen(!isOpen)}
          aria-expanded={isOpen}
        >
          {isOpen ? 'Hide Errors ▲' : 'Show Errors ▼'}
        </button>
      </div>

      {isOpen && (
        <div>
          {loading ? (
            <div className="state-box">
              <div className="spinner" />
              <p>Analyzing cluster impurity...</p>
            </div>
          ) : errorClusters.length === 0 ? (
            <div className="state-box" style={{ padding: '1.5rem' }}>
              <p style={{ color: 'var(--success-text)', fontWeight: 600 }}>
                ✓ Zero false-merge clusters found at this operating threshold!
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                Showing {errorClusters.length} false-merge cluster(s). Click any record to inspect candidate comparisons in Pair Explorer:
              </p>
              {errorClusters.map((cluster) => (
                <div
                  key={cluster.clusterId}
                  style={{
                    border: '1px solid var(--danger-border)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '0.75rem',
                    backgroundColor: 'var(--danger-bg)',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      marginBottom: '0.5rem',
                      fontSize: '0.8125rem',
                    }}
                  >
                    <strong>Cluster: {cluster.clusterId}</strong>
                    <span style={{ color: 'var(--danger-text)', fontWeight: 600 }}>
                      Merged {cluster.personIds.length} distinct people ({cluster.personIds.join(', ')})
                    </span>
                  </div>

                  <div className="table-container">
                    <table className="data-table" style={{ backgroundColor: 'var(--bg-surface)' }}>
                      <thead>
                        <tr>
                          <th>Record ID</th>
                          <th>Full Name</th>
                          <th>Guardian</th>
                          <th>Module</th>
                          <th>Village</th>
                          <th>Age</th>
                          <th>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {cluster.records.map((rec) => (
                          <tr key={rec.record_id}>
                            <td className="num font-mono">{rec.record_id}</td>
                            <td><strong>{rec.full_name_raw}</strong></td>
                            <td>{rec.guardian_name_raw || '—'}</td>
                            <td><span className="chip">{rec.source_module}</span></td>
                            <td>{rec.village_raw}</td>
                            <td className="num">{rec.age_raw ?? '—'}</td>
                            <td>
                              <button
                                type="button"
                                className="mode-btn"
                                style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                                onClick={() => navigateTo('pairs', { record_id: rec.record_id })}
                              >
                                Open in Pair Explorer →
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
