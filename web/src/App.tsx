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
  const [initialEnter, setInitialEnter] = React.useState(true);

  React.useEffect(() => {
    const timer = window.setTimeout(() => setInitialEnter(false), 350);
    return () => window.clearTimeout(timer);
  }, []);

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
        <div className="header-inner">
          <div className="brand-bar">
            <h1 className="brand-title">Bari-Link</h1>
            <p className="brand-subtitle">
              Entity Resolution and Household Inference under Non-Standard Administrative Topologies.
            </p>
          </div>
          <Navigation currentTab={tab} />
        </div>
      </header>

      {/* Dynamic View Content */}
      <main
        id="main-content"
        className={`app-main${initialEnter ? ' initial-enter' : ''}`}
        role="main"
        tabIndex={-1}
      >
        {renderActiveView(tab)}
      </main>

      {/* Footer */}
      <footer className="app-footer">
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
