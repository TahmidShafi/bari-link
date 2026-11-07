/**
 * Formatting constants and utility functions for display.
 * Isolated here so Views do not contain numeric literals.
 */

export const ZERO = 0;
export const FORMAT_DECIMALS_INT = 0;
export const FORMAT_DECIMALS_TENTH = 1;
export const FORMAT_DECIMALS_HUNDREDTH = 2;
export const FORMAT_DECIMALS_THOUSANDTH = 3;
export const FORMAT_DECIMALS_TEN_THOUSANDTH = 4;
export const PERCENT_MULTIPLIER = 100;

export function formatPct(val: number | undefined | null, decimals = FORMAT_DECIMALS_TENTH): string {
  if (val === undefined || val === null || isNaN(val)) return '—';
  return (val * PERCENT_MULTIPLIER).toFixed(decimals) + '%';
}

export function formatRawPct(val: number | undefined | null, decimals = FORMAT_DECIMALS_TENTH): string {
  if (val === undefined || val === null || isNaN(val)) return '—';
  return val.toFixed(decimals) + '%';
}

export function formatRate(val: number | undefined | null, decimals = FORMAT_DECIMALS_TEN_THOUSANDTH): string {
  if (val === undefined || val === null || isNaN(val)) return '—';
  return val.toFixed(decimals);
}

export function formatNum(val: number | undefined | null, decimals = FORMAT_DECIMALS_HUNDREDTH): string {
  if (val === undefined || val === null || isNaN(val)) return '—';
  return val.toFixed(decimals);
}

export function formatInt(val: number | undefined | null): string {
  if (val === undefined || val === null || isNaN(val)) return '—';
  return Math.round(val).toLocaleString();
}

export function formatDelta(val: number | undefined | null, decimals = FORMAT_DECIMALS_TENTH): string {
  if (val === undefined || val === null || isNaN(val)) return '—';
  const prefix = val > 0 ? '+' : '';
  return `${prefix}${val.toFixed(decimals)}`;
}
