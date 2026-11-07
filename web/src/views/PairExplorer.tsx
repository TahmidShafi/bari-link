import React, { useEffect, useState, useTransition } from 'react';
import {
  searchRecords,
  getRecordById,
  getCandidatePairsForRecord,
  loadModelSummary,
} from '../data/queries';
import { computeWaterfall, type WaterfallResult } from '../data/waterfall';
import type { CandidatePair, RecordEntry } from '../data/types';
import { RecordPairView } from '../components/RecordPairView';
import { PairWaterfall } from '../components/PairWaterfall';
import { useHashRoute, navigateTo } from '../router';

export const PairExplorer: React.FC = () => {
  const { params } = useHashRoute();
  const initialRecordId = params.record_id || '';

  const [searchTerm, setSearchTerm] = useState(initialRecordId);
  const [searchResults, setSearchResults] = useState<RecordEntry[]>([]);
  const [selectedRecord, setSelectedRecord] = useState<RecordEntry | null>(null);
  const [candidatePairs, setCandidatePairs] = useState<CandidatePair[]>([]);
  const [selectedPair, setSelectedPair] = useState<CandidatePair | null>(null);
  const [pairRecordL, setPairRecordL] = useState<RecordEntry | null>(null);
  const [pairRecordR, setPairRecordR] = useState<RecordEntry | null>(null);
  const [waterfall, setWaterfall] = useState<WaterfallResult | null>(null);
  const [modelSummary, setModelSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);

  const [, startTransition] = useTransition();

  // Load model summary once
  useEffect(() => {
    loadModelSummary().then(setModelSummary).catch(console.error);
  }, []);

  // Handle URL param changes (e.g. navigated from False Merge inspector)
  useEffect(() => {
    if (params.record_id) {
      setSearchTerm(params.record_id);
      getRecordById(params.record_id).then((rec) => {
        if (rec) {
          handleSelectRecord(rec);
        }
      });
    }
  }, [params.record_id]);

  // Initial search if empty
  useEffect(() => {
    if (!initialRecordId) {
      searchRecords('', 10).then(setSearchResults);
    }
  }, []);

  // Execute prefix search
  const handleSearch = (term: string) => {
    setSearchTerm(term);
    setSearching(true);
    startTransition(() => {
      searchRecords(term, 20)
        .then((recs) => {
          setSearchResults(recs);
          setSearching(false);
        })
        .catch(() => setSearching(false));
    });
  };

  // Select a record -> fetch candidate pairs
  const handleSelectRecord = async (record: RecordEntry) => {
    setSelectedRecord(record);
    setSelectedPair(null);
    setPairRecordL(null);
    setPairRecordR(null);
    setWaterfall(null);
    setLoading(true);

    try {
      const pairs = await getCandidatePairsForRecord(record.record_id);
      setCandidatePairs(pairs);

      // Auto-select first pair if available
      if (pairs.length > 0) {
        handleSelectPair(pairs[0]);
      }
    } catch (err) {
      console.error('Failed to load candidate pairs:', err);
    } finally {
      setLoading(false);
    }
  };

  // Select candidate pair -> compute waterfall & fetch raw records
  const handleSelectPair = async (pair: CandidatePair) => {
    setSelectedPair(pair);
    setLoading(true);

    try {
      const [recL, recR] = await Promise.all([
        getRecordById(pair.record_id_l),
        getRecordById(pair.record_id_r),
      ]);

      setPairRecordL(recL);
      setPairRecordR(recR);

      // Ensure model summary is available
      const summary = modelSummary || (await loadModelSummary());
      if (summary) {
        const wf = computeWaterfall(pair, summary);
        setWaterfall(wf);
      }
    } catch (err) {
      console.error('Failed to load pair details:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Search Bar & Header */}
      <div className="card">
        <h2 className="card-title">Candidate Pair & Evidence Waterfall Explorer</h2>
        <p className="tile-sub" style={{ marginBottom: '1rem' }}>
          Inspect Fellegi-Sunter log-odds evidence decomposition for probabilistic record comparisons
        </p>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <input
            type="text"
            className="input-search"
            placeholder="Search by full name or record ID (e.g., rec_)..."
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
          {loading && <span className="tile-sub">Loading pair...</span>}
        </div>

        {/* Search Results list */}
        {searchResults.length > 0 && !selectedRecord && (
          <div style={{ marginTop: '1rem' }}>
            <span className="fact-label">Matching Registry Records</span>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                gap: '0.5rem',
                marginTop: '0.5rem',
                maxHeight: '260px',
                overflowY: 'auto',
              }}
            >
              {searchResults.map((rec) => (
                <button
                  key={rec.record_id}
                  onClick={() => {
                    navigateTo('pairs', { record_id: rec.record_id });
                    handleSelectRecord(rec);
                  }}
                  style={{
                    textAlign: 'left',
                    padding: '0.625rem 0.75rem',
                    backgroundColor: 'var(--bg-surface-subtle)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{rec.full_name_raw}</div>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      fontSize: '0.75rem',
                      color: 'var(--text-subtle)',
                      marginTop: '0.25rem',
                    }}
                  >
                    <span className="font-mono">{rec.record_id}</span>
                    <span>{rec.source_module}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Selected Record Info & Candidate Pairs Bar */}
      {selectedRecord && (
        <div className="card">
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '0.5rem',
              marginBottom: '1rem',
            }}
          >
            <div>
              <span className="fact-label">Active Query Record</span>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 700, margin: '0.25rem 0' }}>
                {selectedRecord.full_name_raw}
              </h3>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <span className="chip font-mono">{selectedRecord.record_id}</span>
                <span className="chip chip-accent">{selectedRecord.source_module}</span>
                <span className="tile-sub">Village: {selectedRecord.village_raw || '—'}</span>
              </div>
            </div>

            <button
              onClick={() => {
                setSelectedRecord(null);
                setSelectedPair(null);
                setCandidatePairs([]);
                navigateTo('pairs');
              }}
              style={{
                padding: '0.375rem 0.75rem',
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                borderRadius: '4px',
                fontSize: '0.75rem',
                cursor: 'pointer',
              }}
            >
              Clear Selection
            </button>
          </div>

          <div className="fact-label" style={{ marginBottom: '0.5rem' }}>
            Candidate Comparison Pairs ({candidatePairs.length})
          </div>

          {candidatePairs.length === 0 ? (
            <p style={{ fontSize: '0.875rem', color: 'var(--text-subtle)' }}>
              No candidate pairs survived blocking stages for this record.
            </p>
          ) : (
            <div
              style={{
                display: 'flex',
                gap: '0.5rem',
                overflowX: 'auto',
                paddingBottom: '0.5rem',
              }}
            >
              {candidatePairs.map((pair) => {
                const otherId =
                  pair.record_id_l === selectedRecord.record_id
                    ? pair.record_id_r
                    : pair.record_id_l;
                const isSelected =
                  selectedPair &&
                  selectedPair.record_id_l === pair.record_id_l &&
                  selectedPair.record_id_r === pair.record_id_r;

                return (
                  <button
                    key={`${pair.record_id_l}-${pair.record_id_r}`}
                    onClick={() => handleSelectPair(pair)}
                    style={{
                      padding: '0.5rem 0.75rem',
                      minWidth: '200px',
                      textAlign: 'left',
                      borderRadius: '4px',
                      border: isSelected
                        ? '2px solid var(--accent)'
                        : '1px solid var(--border-color)',
                      backgroundColor: isSelected
                        ? 'var(--accent-subtle)'
                        : 'var(--bg-surface-subtle)',
                      cursor: 'pointer',
                      flexShrink: 0,
                    }}
                  >
                    <div
                      style={{
                        fontSize: '0.75rem',
                        color: 'var(--text-subtle)',
                        fontFamily: 'monospace',
                      }}
                    >
                      vs {otherId}
                    </div>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        marginTop: '0.25rem',
                        fontWeight: 600,
                        fontSize: '0.8125rem',
                      }}
                    >
                      <span>Weight:</span>
                      <span className="num font-mono">{pair.match_weight.toFixed(2)}</span>
                    </div>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: '0.75rem',
                        color: 'var(--text-subtle)',
                      }}
                    >
                      <span>Probability:</span>
                      <span className="num">{(pair.match_probability * 100).toFixed(1)}%</span>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Side-by-side Raw Comparison */}
      {pairRecordL && pairRecordR && (
        <RecordPairView recordL={pairRecordL} recordR={pairRecordR} />
      )}

      {/* Waterfall Table & Graph */}
      {waterfall && <PairWaterfall waterfall={waterfall} />}
    </div>
  );
};
