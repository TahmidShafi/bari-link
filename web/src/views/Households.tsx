import React, { useEffect, useState, useTransition } from 'react';
import {
  searchHouseholds,
  getHouseholdGolden,
  loadHouseholdGraph,
} from '../data/queries';
import type { HouseholdGolden, HouseholdGraphData } from '../data/types';
import { HouseholdDetails } from '../components/HouseholdDetails';
import { HouseholdGraph } from '../components/HouseholdGraph';
import { useHashRoute, navigateTo } from '../router';

export const Households: React.FC = () => {
  const { params } = useHashRoute();
  const initialHhId = params.household_id || '';

  const [searchTerm, setSearchTerm] = useState(initialHhId);
  const [searchResults, setSearchResults] = useState<HouseholdGolden[]>([]);
  const [selectedHousehold, setSelectedHousehold] = useState<HouseholdGolden | null>(null);
  const [graphData, setGraphData] = useState<HouseholdGraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);

  const [, startTransition] = useTransition();

  // Load graph data once
  useEffect(() => {
    loadHouseholdGraph()
      .then(setGraphData)
      .catch((err) => console.error('Failed to load household graph:', err));
  }, []);

  // Handle URL param changes
  useEffect(() => {
    if (params.household_id) {
      setSearchTerm(params.household_id);
      getHouseholdGolden(params.household_id).then((hh) => {
        if (hh) {
          handleSelectHousehold(hh);
        }
      });
    }
  }, [params.household_id]);

  // Initial load if empty
  useEffect(() => {
    if (!initialHhId) {
      searchHouseholds('', 12).then((results) => {
        setSearchResults(results);
        if (results.length > 0 && !selectedHousehold) {
          handleSelectHousehold(results[0]);
        }
      });
    }
  }, []);

  const handleSearch = (term: string) => {
    setSearchTerm(term);
    setSearching(true);
    startTransition(() => {
      searchHouseholds(term, 20)
        .then((res) => {
          setSearchResults(res);
          setSearching(false);
        })
        .catch(() => setSearching(false));
    });
  };

  const handleSelectHousehold = async (hh: HouseholdGolden) => {
    setSelectedHousehold(hh);
    setLoading(true);

    try {
      // Ensure graph is loaded
      if (!graphData) {
        const gd = await loadHouseholdGraph();
        setGraphData(gd);
      }
    } catch (err) {
      console.error('Failed to load graph data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Search Header */}
      <div className="card">
        <h2 className="card-title">Household Entity Resolution & 1-Hop Network Subgraph</h2>
        <p className="tile-sub" style={{ marginBottom: '1rem' }}>
          Inspect golden household attributes, multi-program enrolments, roster linkages, and evidence relationships (E1–E5)
        </p>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <input
            type="text"
            className="input-search"
            placeholder="Search by person name, village, or household ID (e.g., hh_)..."
            value={searchTerm}
            onChange={(e) => handleSearch(e.target.value)}
            style={{
              flex: 1,
              padding: '0.625rem 0.875rem',
              border: '1px solid var(--border-color)',
              borderRadius: '4px',
              fontSize: '0.875rem',
              outline: 'none',
              fontFamily: 'inherit',
            }}
          />
          {searching && <span className="tile-sub">Searching...</span>}
          {loading && <span className="tile-sub">Loading household...</span>}
        </div>

        {/* Search Results list */}
        {searchResults.length > 0 && (
          <div style={{ marginTop: '1rem' }}>
            <span className="fact-label">Matching Households</span>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
                gap: '0.5rem',
                marginTop: '0.5rem',
                maxHeight: '180px',
                overflowY: 'auto',
              }}
            >
              {searchResults.map((hh) => {
                const isSelected =
                  selectedHousehold &&
                  selectedHousehold.household_cluster_id === hh.household_cluster_id;

                return (
                  <button
                    key={hh.household_cluster_id}
                    onClick={() => {
                      navigateTo('households', { household_id: hh.household_cluster_id });
                      handleSelectHousehold(hh);
                    }}
                    style={{
                      textAlign: 'left',
                      padding: '0.5rem 0.75rem',
                      backgroundColor: isSelected
                        ? 'var(--accent-subtle)'
                        : 'var(--bg-surface-subtle)',
                      border: isSelected
                        ? '2px solid var(--accent)'
                        : '1px solid var(--border-color)',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }}
                  >
                    <div className="font-mono" style={{ fontWeight: 600, fontSize: '0.8125rem' }}>
                      {hh.household_cluster_id}
                    </div>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: '0.75rem',
                        color: 'var(--text-subtle)',
                        marginTop: '0.25rem',
                      }}
                    >
                      <span>{hh.village || hh.village_mode || '—'}</span>
                      <span>
                        Size: <strong className="num">{hh.est_household_size}</strong>
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Selected Household Golden Profile */}
      {selectedHousehold && <HouseholdDetails golden={selectedHousehold} />}

      {/* 1-Hop Force Graph */}
      {selectedHousehold && graphData && (
        <HouseholdGraph
          householdClusterId={selectedHousehold.household_cluster_id}
          graphData={graphData}
        />
      )}
    </div>
  );
};
