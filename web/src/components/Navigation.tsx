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

  const navRef = React.useRef<HTMLElement | null>(null);
  const tabRefs = React.useRef<Record<string, HTMLAnchorElement | null>>({});
  const [indicator, setIndicator] = React.useState<{ left: number; width: number; ready: boolean }>({
    left: 0,
    width: 0,
    ready: false,
  });

  const updateIndicator = React.useCallback(() => {
    const activeEl = tabRefs.current[currentTab];
    const navEl = navRef.current;
    if (!activeEl || !navEl) return;
    setIndicator({
      left: activeEl.offsetLeft,
      width: activeEl.offsetWidth,
      ready: true,
    });
  }, [currentTab]);

  React.useLayoutEffect(() => {
    updateIndicator();
  }, [updateIndicator]);

  React.useEffect(() => {
    const navEl = navRef.current;
    if (!navEl || typeof ResizeObserver === 'undefined') return;
    const ro = new ResizeObserver(() => updateIndicator());
    ro.observe(navEl);
    return () => ro.disconnect();
  }, [updateIndicator]);

  return (
    <nav ref={navRef} className="nav-tabs" role="tablist" aria-label="Main Navigation">
      {tabs.map((tab) => {
        const isActive = currentTab === tab.id;
        return (
          <a
            key={tab.id}
            ref={(el) => {
              tabRefs.current[tab.id] = el;
            }}
            href={`#${tab.id}`}
            role="tab"
            aria-selected={isActive}
            className={`nav-tab ${isActive ? 'active' : ''}${isActive && !indicator.ready ? ' no-indicator' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              navigateTo(tab.id);
            }}
          >
            {tab.label}
          </a>
        );
      })}
      {indicator.ready && (
        <span
          className="nav-indicator"
          aria-hidden="true"
          style={{
            width: `${indicator.width}px`,
            transform: `translateX(${indicator.left}px)`,
          }}
        />
      )}
    </nav>
  );
};

