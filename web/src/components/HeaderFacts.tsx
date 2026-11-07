import React, { useEffect, useState } from 'react';
import { getModuleCounts } from '../data/queries';
import { getHeadlineFacts } from '../eval/evalData';
import type { ModuleCount } from '../data/types';

export const HeaderFacts: React.FC = () => {
  const [moduleCounts, setModuleCounts] = useState<ModuleCount[]>([]);
  const [facts, setFacts] = useState<{
    totalRecords: number;
    trueUniquePersons: number;
    duplicateInflationPct: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    Promise.all([getModuleCounts(), getHeadlineFacts()])
      .then(([mods, f]) => {
        if (isMounted) {
          setModuleCounts(mods);
          setFacts(f);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load header facts:', err);
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  if (loading || !facts) {
    return (
      <div className="facts-bar" aria-busy="true">
        <span className="fact-label">Loading registry statistics...</span>
      </div>
    );
  }

  return (
    <div className="facts-bar" aria-label="Population and Enrolment Facts">
      <div className="fact-item">
        <span className="fact-label">Naive Registrations</span>
        <span className="fact-value num">{facts.totalRecords.toLocaleString()}</span>
      </div>

      <div className="fact-item">
        <span className="fact-label">True Unique Persons</span>
        <span className="fact-value num">{facts.trueUniquePersons.toLocaleString()}</span>
      </div>

      <div className="fact-item">
        <span className="fact-label">Duplicate Inflation</span>
        <span className="fact-value num" style={{ color: 'var(--accent)' }}>
          +{facts.duplicateInflationPct.toFixed(1)}%
        </span>
      </div>

      <div className="module-chips">
        {moduleCounts.map((m) => (
          <span key={m.source_module} className="chip">
            <strong>{m.source_module.replace(/_/g, ' ')}:</strong>{' '}
            <span className="num">{m.count.toLocaleString()}</span>
          </span>
        ))}
      </div>
    </div>
  );
};

