import React from 'react';
import type { HouseholdGolden } from '../data/types';

interface HouseholdDetailsProps {
  golden: HouseholdGolden;
}

export const HouseholdDetails: React.FC<HouseholdDetailsProps> = ({ golden }) => {
  // Parse enrolled members if stored as JSON string or array of objects/strings
  let members: string[] = [];
  if (typeof golden.enrolled_members === 'string') {
    try {
      const parsed = JSON.parse(golden.enrolled_members);
      if (Array.isArray(parsed)) {
        members = parsed.map((m: any) =>
          typeof m === 'object' && m ? (m.display_name || m.cluster_id || JSON.stringify(m)) : String(m)
        );
      } else {
        members = [golden.enrolled_members];
      }
    } catch {
      members = [golden.enrolled_members];
    }
  } else if (Array.isArray(golden.enrolled_members)) {
    members = golden.enrolled_members.map((m: any) =>
      typeof m === 'object' && m ? (m.display_name || m.cluster_id || JSON.stringify(m)) : String(m)
    );
  }

  // Parse unenrolled roster names
  let rosterUnenrolled: string[] = [];
  if (typeof golden.roster_names_unenrolled === 'string') {
    try {
      const parsed = JSON.parse(golden.roster_names_unenrolled);
      if (Array.isArray(parsed)) rosterUnenrolled = parsed.map(String);
    } catch {
      rosterUnenrolled = [golden.roster_names_unenrolled];
    }
  } else if (Array.isArray(golden.roster_names_unenrolled)) {
    rosterUnenrolled = golden.roster_names_unenrolled.map(String);
  }

  // Extract modules list and count distinct enrolled programs
  let rawModules: any = golden.modules ?? (golden as any).enrolled_modules;
  if (typeof rawModules === 'string') {
    try {
      rawModules = JSON.parse(rawModules);
    } catch {
      rawModules = [rawModules];
    }
  }
  let modulesList: string[] = [];
  if (Array.isArray(rawModules)) {
    modulesList = rawModules.map(String);
  } else if (rawModules && typeof rawModules.toArray === 'function') {
    modulesList = Array.from(rawModules.toArray()).map(String);
  } else if (rawModules && typeof rawModules[Symbol.iterator] === 'function') {
    modulesList = Array.from(rawModules).map(String);
  }

  // Deduplicate distinct modules
  const distinctModules = Array.from(new Set(modulesList.filter(Boolean)));

  const village = golden.village || golden.village_mode || '—';
  const union = golden.union || golden.union_mode || '—';

  // Parse evidence lineage into structured table rows
  let lineageObj: Record<string, any> | null = null;
  const rawLineage = golden.field_lineage || (golden as any).lineage;
  if (typeof rawLineage === 'string') {
    try {
      lineageObj = JSON.parse(rawLineage);
    } catch {
      lineageObj = null;
    }
  } else if (rawLineage && typeof rawLineage === 'object') {
    lineageObj = rawLineage;
  }

  const lineageRows: Array<{ field: string; value: string; rule: string; source: string }> = [];
  if (lineageObj) {
    for (const [field, info] of Object.entries(lineageObj)) {
      if (info && typeof info === 'object') {
        const value =
          info.value !== undefined
            ? String(info.value)
            : info.count !== undefined
            ? String(info.count)
            : '—';
        const rule =
          info.rule !== undefined
            ? String(info.rule)
            : info.formula !== undefined
            ? `formula: ${info.formula}`
            : '—';
        const source =
          info.source_unit !== undefined
            ? String(info.source_unit)
            : info.unit_ids !== undefined
            ? Array.isArray(info.unit_ids)
              ? info.unit_ids.join(', ')
              : String(info.unit_ids)
            : info.unenrolled_skeletons !== undefined
            ? `roster (${info.unenrolled_skeletons.length} skeletons)`
            : '—';
        lineageRows.push({ field, value, rule, source });
      } else {
        lineageRows.push({ field, value: String(info), rule: '—', source: '—' });
      }
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h3 className="card-title">Household Golden Profile</h3>
          <p className="tile-sub font-mono">ID: {golden.household_cluster_id}</p>
        </div>
        <div>
          <span className="chip chip-accent">
            Estimated Size: <strong className="num">{golden.est_household_size} members</strong>
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="tiles-grid" style={{ marginBottom: '1.25rem' }}>
        <div className="tile">
          <span className="tile-title">Direct Reach</span>
          <span className="tile-value num">{golden.direct_reach}</span>
          <span className="tile-sub">Enrolled beneficiaries</span>
        </div>

        <div className="tile">
          <span className="tile-title">Indirect Reach</span>
          <span className="tile-value num">{golden.indirect_reach}</span>
          <span className="tile-sub">Unenrolled roster members</span>
        </div>

        <div className="tile">
          <span className="tile-title">Location Mode</span>
          <span className="tile-value" style={{ fontSize: '1.1rem' }}>
            {village}
          </span>
          <span className="tile-sub">Union: {union}</span>
        </div>

        <div className="tile">
          <span className="tile-title">Enrolled Programs</span>
          <span className="tile-value num" style={{ fontSize: '1.1rem' }}>
            {distinctModules.length}
          </span>
          <span className="tile-sub">{distinctModules.length > 0 ? distinctModules.join(', ') : 'None'}</span>
        </div>
      </div>

      {/* Enrolled vs Unenrolled Rosters */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <div className="record-box">
          <h4 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            Enrolled Household Members ({members.length})
          </h4>
          {members.length === 0 ? (
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-subtle)' }}>None recorded.</p>
          ) : (
            <ul style={{ paddingLeft: '1.25rem', fontSize: '0.8125rem' }}>
              {members.map((m, idx) => (
                <li key={idx} style={{ marginBottom: '0.25rem' }}>
                  <strong>{m}</strong>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="record-box">
          <h4 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>
            Unenrolled Roster Names ({rosterUnenrolled.length})
          </h4>
          {rosterUnenrolled.length === 0 ? (
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-subtle)' }}>
              No additional roster names listed in surveys.
            </p>
          ) : (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
              {rosterUnenrolled.map((r, idx) => (
                <span key={idx} className="chip">
                  {r}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {lineageRows.length > 0 && (
        <details style={{ marginTop: '1.25rem', border: '1px solid var(--border-color)', borderRadius: '4px', padding: '0.625rem 0.875rem' }}>
          <summary style={{ cursor: 'pointer', fontWeight: 600, fontSize: '0.875rem' }}>
            Evidence Lineage ({lineageRows.length} attributes resolved)
          </summary>
          <div className="table-container" style={{ marginTop: '0.5rem' }}>
            <table className="data-table" style={{ fontSize: '0.8125rem' }}>
              <thead>
                <tr>
                  <th>Field</th>
                  <th>Value</th>
                  <th>Resolution Rule</th>
                  <th>Source / Supporting Evidence</th>
                </tr>
              </thead>
              <tbody>
                {lineageRows.map((row) => (
                  <tr key={row.field}>
                    <td><strong>{row.field}</strong></td>
                    <td className="font-mono">{row.value}</td>
                    <td><code>{row.rule}</code></td>
                    <td className="font-mono" style={{ fontSize: '0.75rem' }}>{row.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      )}
    </div>
  );
};
