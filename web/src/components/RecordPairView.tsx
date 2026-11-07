import React from 'react';
import type { RecordEntry } from '../data/types';
import { TruthChip } from '../eval/truthChip';

interface RecordPairViewProps {
  recordL: RecordEntry;
  recordR: RecordEntry;
}

export const RecordPairView: React.FC<RecordPairViewProps> = ({ recordL, recordR }) => {
  const fields: Array<{ label: string; key: keyof RecordEntry }> = [
    { label: 'Full Name', key: 'full_name_raw' },
    { label: 'Guardian Name', key: 'guardian_name_raw' },
    { label: 'Guardian Type', key: 'guardian_type_raw' },
    { label: 'Reported Age', key: 'age_raw' },
    { label: 'Phone Number', key: 'phone_raw' },
    { label: 'Village', key: 'village_raw' },
    { label: 'Union', key: 'union_raw' },
    { label: 'Upazila / District', key: 'upazila_raw' },
    { label: 'Source Module', key: 'source_module' },
    { label: 'Group ID', key: 'group_id' },
  ];

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h3 className="card-title">Side-by-Side Raw Registry Records</h3>
          <p className="tile-sub">Direct comparison of surveyed administrative fields</p>
        </div>
        <TruthChip recordIdL={recordL.record_id} recordIdR={recordR.record_id} />
      </div>

      <div className="pair-comparison">
        {/* Record L */}
        <div className="record-box">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <span className="fact-label">Record L</span>
            <span className="chip num font-mono">{recordL.record_id}</span>
          </div>
          {fields.map(({ label, key }) => {
            const val = recordL[key];
            return (
              <div key={key} className="record-attr-row">
                <span className="record-attr-key">{label}</span>
                <span className="record-attr-val num">
                  {val !== null && val !== undefined && val !== '' ? String(val) : '—'}
                </span>
              </div>
            );
          })}
        </div>

        {/* Record R */}
        <div className="record-box">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <span className="fact-label">Record R</span>
            <span className="chip num font-mono">{recordR.record_id}</span>
          </div>
          {fields.map(({ label, key }) => {
            const val = recordR[key];
            const isMatch =
              val &&
              recordL[key] &&
              String(val).trim().toLowerCase() === String(recordL[key]).trim().toLowerCase();

            return (
              <div key={key} className="record-attr-row">
                <span className="record-attr-key">{label}</span>
                <span
                  className="record-attr-val num"
                  style={{
                    fontWeight: isMatch ? 700 : 'normal',
                    color: isMatch ? 'var(--accent-text)' : 'inherit',
                  }}
                >
                  {val !== null && val !== undefined && val !== '' ? String(val) : '—'}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

