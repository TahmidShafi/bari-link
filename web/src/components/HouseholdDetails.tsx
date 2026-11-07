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

  const modulesList = Array.isArray(golden.modules)
    ? golden.modules
    : Array.isArray(golden.enrolled_modules)
    ? golden.enrolled_modules
    : [];

  const village = golden.village || golden.village_mode || '—';
  const union = golden.union || golden.union_mode || '—';
  const lineage = golden.field_lineage || golden.lineage;

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
          <span className="tile-value" style={{ fontSize: '1.1rem' }}>
            {modulesList.length}
          </span>
          <span className="tile-sub">{modulesList.join(', ')}</span>
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

      {lineage && (
        <div style={{ marginTop: '1rem', fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
          <strong>Evidence Lineage:</strong> {lineage}
        </div>
      )}
    </div>
  );
};
