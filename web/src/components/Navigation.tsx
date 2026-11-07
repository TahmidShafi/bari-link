import React from 'react';
import { RouteTab, navigateTo } from '../router';

interface NavigationProps {
  currentTab: RouteTab;
}

export const Navigation: React.FC<NavigationProps> = ({ currentTab }) => {
  const tabs: Array<{ id: RouteTab; label: string }> = [
    { id: 'overview', label: 'Overview' },
    { id: 'pairs', label: 'Pair Explorer' },
    { id: 'households', label: 'Households' },
    { id: 'findings', label: 'Findings' },
  ];

  return (
    <nav className="nav-tabs" role="tablist" aria-label="Main Navigation">
      {tabs.map((tab) => {
        const isActive = currentTab === tab.id;
        return (
          <a
            key={tab.id}
            href={`#${tab.id}`}
            role="tab"
            aria-selected={isActive}
            className={`nav-tab ${isActive ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              navigateTo(tab.id);
            }}
          >
            {tab.label}
          </a>
        );
      })}
    </nav>
  );
};

