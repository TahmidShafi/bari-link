import { useEffect, useState } from 'react';

export type RouteTab = 'overview' | 'pairs' | 'households' | 'findings';

export interface RouteState {
  tab: RouteTab;
  params: Record<string, string>;
}

export function parseHash(): RouteState {
  const hash = window.location.hash.slice(1); // strip leading #
  const [pathPart, queryPart] = hash.split('?');
  const cleanPath = (pathPart || 'overview').replace(/^\//, '').toLowerCase();

  let tab: RouteTab = 'overview';
  if (cleanPath.startsWith('pair')) tab = 'pairs';
  else if (cleanPath.startsWith('household')) tab = 'households';
  else if (cleanPath.startsWith('finding')) tab = 'findings';
  else tab = 'overview';

  const params: Record<string, string> = {};
  if (queryPart) {
    const searchParams = new URLSearchParams(queryPart);
    for (const [key, value] of searchParams.entries()) {
      params[key] = value;
    }
  }

  return { tab, params };
}

export function navigateTo(tab: RouteTab, params?: Record<string, string>): void {
  let hash = `#${tab}`;
  if (params && Object.keys(params).length > 0) {
    const q = new URLSearchParams(params).toString();
    hash += `?${q}`;
  }
  window.location.hash = hash;
}

export function useHashRoute(): RouteState {
  const [route, setRoute] = useState<RouteState>(parseHash);

  useEffect(() => {
    const handleHashChange = () => {
      setRoute(parseHash());
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  return route;
}

