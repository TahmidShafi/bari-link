/**
 * Strictly isolated evaluation data layer.
 * This is the ONLY module permitted to register and query data/eval/ datasets.
 */

import { initDuckDB, runQuery, getAssetUrl } from '../data/duckdb';
import * as duckdb from '@duckdb/duckdb-wasm';

export interface ThresholdTableRow {
  t_link: number;
  precision: number;
  recall: number;
  f1: number;
  expected_cost: number;
  false_merge_clusters: number;
  doppelganger_false_merge_rate: number;
  dedup_reach: number;
  true_reach: number;
  naive_reach: number;
  review_queue_size: number;
  variant: string;
}

export interface RecordLabel {
  record_id: string;
  person_id: string;
  household_id: string;
}

let evalFilesRegistered = false;
let cachedHeadline: any = null;
let cachedLabels: Map<string, RecordLabel> | null = null;
let cachedThresholdRows: ThresholdTableRow[] | null = null;

export async function ensureEvalFilesRegistered(): Promise<void> {
  if (evalFilesRegistered) return;
  const db = await initDuckDB();

  const threshUrl = getAssetUrl('data/eval/threshold_table.parquet');
  const labelsUrl = getAssetUrl('data/eval/record_labels.parquet');

  await db.registerFileURL('threshold_table.parquet', threshUrl, duckdb.DuckDBDataProtocol.HTTP, false);
  await db.registerFileURL('record_labels.parquet', labelsUrl, duckdb.DuckDBDataProtocol.HTTP, false);

  evalFilesRegistered = true;
}

export async function getThresholdTable(
  variant: 'constraint' | 'no_constraint' | 'raw'
): Promise<ThresholdTableRow[]> {
  await ensureEvalFilesRegistered();
  if (!cachedThresholdRows) {
    const sql = `SELECT * FROM 'threshold_table.parquet' ORDER BY t_link ASC`;
    cachedThresholdRows = await runQuery<ThresholdTableRow>(sql);
  }
  return cachedThresholdRows.filter((r) => r.variant === variant);
}

export async function getRecordLabelsMap(): Promise<Map<string, RecordLabel>> {
  if (cachedLabels) return cachedLabels;
  await ensureEvalFilesRegistered();

  const sql = `SELECT record_id, person_id, household_id FROM 'record_labels.parquet'`;
  const rows = await runQuery<RecordLabel>(sql);

  cachedLabels = new Map<string, RecordLabel>();
  for (const r of rows) {
    cachedLabels.set(r.record_id, r);
  }
  return cachedLabels;
}

export async function getHeadlineFacts(): Promise<{
  totalRecords: number;
  trueUniquePersons: number;
  duplicateInflationPct: number;
}> {
  const labelsMap = await getRecordLabelsMap();
  const totalRecords = labelsMap.size;
  const uniquePersons = new Set<string>();
  for (const label of labelsMap.values()) {
    uniquePersons.add(label.person_id);
  }
  const trueUniquePersons = uniquePersons.size;
  const duplicateInflationPct =
    trueUniquePersons > 0
      ? ((totalRecords - trueUniquePersons) / trueUniquePersons) * 100
      : 0;

  return {
    totalRecords,
    trueUniquePersons,
    duplicateInflationPct,
  };
}

export async function getHeadlineFindings(): Promise<any> {
  if (cachedHeadline) return cachedHeadline;
  const url = getAssetUrl('data/eval/headline.json');
  const resp = await fetch(url);
  if (!resp.ok) {
    throw new Error(`Failed to load headline findings: ${resp.statusText}`);
  }
  cachedHeadline = await resp.json();
  return cachedHeadline;
}

export async function getPairTruth(
  recordIdL: string,
  recordIdR: string
): Promise<{
  isSamePerson: boolean;
  isSameHousehold: boolean;
  personIdL?: string;
  personIdR?: string;
}> {
  const labelsMap = await getRecordLabelsMap();
  const labelL = labelsMap.get(recordIdL);
  const labelR = labelsMap.get(recordIdR);

  if (!labelL || !labelR) {
    return { isSamePerson: false, isSameHousehold: false };
  }

  return {
    isSamePerson: labelL.person_id === labelR.person_id,
    isSameHousehold: labelL.household_id === labelR.household_id,
    personIdL: labelL.person_id,
    personIdR: labelR.person_id,
  };
}

