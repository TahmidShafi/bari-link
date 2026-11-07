import React from 'react';
import { Banner } from './components/Banner';
import { Navigation } from './components/Navigation';
import { useHashRoute, type RouteTab } from './router';
import { Overview } from './views/Overview';
import { PairExplorer } from './views/PairExplorer';
import { Households } from './views/Households';
import { Findings } from './views/Findings';

export const App: React.FC = () => {
  const { tab } = useHashRoute();

  const renderActiveView = (activeTab: RouteTab) => {
    switch (activeTab) {
      case 'overview':
        return <Overview />;
      case 'pairs':
        return <PairExplorer />;
      case 'households':
        return <Households />;
      case 'findings':
        return <Findings />;
      default:
        return <Overview />;
    }
  };

  return (
    <div className="app-container">
      {/* Persistent synthetic banner required across all views */}
      <Banner />

      {/* Main Navigation Header */}
      <header className="app-header">
        <Navigation currentTab={tab} />
      </header>

      {/* Dynamic View Content */}
      <main id="main-content" className="app-main" role="main" tabIndex={-1}>
        {renderActiveView(tab)}
      </main>

      {/* Footer */}
      <footer
        style={{
          marginTop: '3rem',
          padding: '1.5rem 0',
          borderTop: '1px solid var(--border-color)',
          textAlign: 'center',
          fontSize: '0.75rem',
          color: 'var(--text-subtle)',
        }}
      >
        <p>
          Bari-Link: Entity Resolution and Household Inference under Non-Standard Administrative Topologies.
        </p>
        <p style={{ marginTop: '0.25rem' }}>
          Zero-backend static application running in-browser via DuckDB-Wasm. All data synthetic.
        </p>
      </footer>
    </div>
  );
};
