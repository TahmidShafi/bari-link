import React, { useEffect, useState } from 'react';
import { getPairTruth } from './evalData';

interface TruthChipProps {
  recordIdL: string;
  recordIdR: string;
}

export const TruthChip: React.FC<TruthChipProps> = ({ recordIdL, recordIdR }) => {
  const [truth, setTruth] = useState<{
    isSamePerson: boolean;
    isSameHousehold: boolean;
    personIdL?: string;
    personIdR?: string;
  } | null>(null);

  useEffect(() => {
    let isMounted = true;
    getPairTruth(recordIdL, recordIdR)
      .then((res) => {
        if (isMounted) setTruth(res);
      })
      .catch(() => {
        if (isMounted) setTruth(null);
      });
    return () => {
      isMounted = false;
    };
  }, [recordIdL, recordIdR]);

  if (!truth) return null;

  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
      {truth.isSamePerson ? (
        <span
          className="chip"
          style={{
            backgroundColor: 'var(--success-bg)',
            color: 'var(--success-text)',
            borderColor: 'var(--success-border)',
            fontWeight: 600,
          }}
          title={`Ground Truth Match: Same individual (${truth.personIdL})`}
        >
          ✓ Truth: Same Person ({truth.personIdL})
        </span>
      ) : (
        <span
          className="chip"
          style={{
            backgroundColor: 'var(--danger-bg)',
            color: 'var(--danger-text)',
            borderColor: 'var(--danger-border)',
            fontWeight: 600,
          }}
          title={`Ground Truth Negative: Distinct individuals (${truth.personIdL} vs ${truth.personIdR})`}
        >
          ✕ Truth: Different Persons ({truth.personIdL} vs {truth.personIdR})
        </span>
      )}
      {truth.isSameHousehold && !truth.isSamePerson && (
        <span
          className="chip"
          style={{
            backgroundColor: 'var(--warning-bg)',
            color: 'var(--warning-text)',
            borderColor: 'var(--warning-border)',
          }}
        >
          Same Household Co-Residents
        </span>
      )}
    </div>
  );
};

