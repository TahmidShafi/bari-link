/**
 * Typed Query Layer for model-visible datasets.
 * Components call these functions; no raw SQL in React components.
 * STRICT ISOLATION: NEVER references ground truth datasets.
 */

import { ensureFileRegistered, runQuery, getAssetUrl } from './duckdb';
import type {
  CandidatePair,
  HouseholdGolden,
  HouseholdGraphData,
  ModuleCount,
  RecordEntry,
} from './types';

let cachedModelSummary: any = null;
let cachedHouseholdGraph: HouseholdGraphData | null = null;

export async function getModuleCounts(): Promise<ModuleCount[]> {
  await ensureFileRegistered('records.parquet');
  const sql = `
    SELECT source_module, CAST(count(*) AS INTEGER) as count
    FROM 'records.parquet'
    GROUP BY source_module
    ORDER BY count DESC
  `;
  return runQuery<ModuleCount>(sql);
}

export async function searchRecords(term: string, limit = 20): Promise<RecordEntry[]> {
  await ensureFileRegistered('records.parquet');
  const cleanTerm = term.trim().replace(/'/g, "''");
  if (!cleanTerm) {
    const sql = `SELECT * FROM 'records.parquet' LIMIT ${limit}`;
    return runQuery<RecordEntry>(sql);
  }

  const sql = `
    SELECT *
    FROM 'records.parquet'
    WHERE full_name_raw ILIKE '${cleanTerm}%'
       OR record_id ILIKE '${cleanTerm}%'
    ORDER BY full_name_raw ASC
    LIMIT ${limit}
  `;
  return runQuery<RecordEntry>(sql);
}

export async function getRecordById(recordId: string): Promise<RecordEntry | null> {
  await ensureFileRegistered('records.parquet');
  const cleanId = recordId.trim().replace(/'/g, "''");
  const sql = `SELECT * FROM 'records.parquet' WHERE record_id = '${cleanId}' LIMIT 1`;
  const rows = await runQuery<RecordEntry>(sql);
  return rows.length > 0 ? rows[0] : null;
}

export async function getCandidatePairsForRecord(recordId: string): Promise<CandidatePair[]> {
  await ensureFileRegistered('pairs.parquet');
  const cleanId = recordId.trim().replace(/'/g, "''");
  const sql = `
    SELECT *
    FROM 'pairs.parquet'
    WHERE record_id_l = '${cleanId}' OR record_id_r = '${cleanId}'
    ORDER BY match_weight DESC
  `;
  return runQuery<CandidatePair>(sql);
}

export async function getPairDetail(
  recordIdL: string,
  recordIdR: string
): Promise<CandidatePair | null> {
  await ensureFileRegistered('pairs.parquet');
  const u = recordIdL.trim().replace(/'/g, "''");
  const v = recordIdR.trim().replace(/'/g, "''");
  const sql = `
    SELECT *
    FROM 'pairs.parquet'
    WHERE (record_id_l = '${u}' AND record_id_r = '${v}')
       OR (record_id_l = '${v}' AND record_id_r = '${u}')
    LIMIT 1
  `;
  const rows = await runQuery<CandidatePair>(sql);
  return rows.length > 0 ? rows[0] : null;
}

export async function getAllPairs(): Promise<CandidatePair[]> {
  await ensureFileRegistered('pairs.parquet');
  const sql = `
    SELECT record_id_l, record_id_r, match_weight, match_probability
    FROM 'pairs.parquet'
  `;
  return runQuery<CandidatePair>(sql);
}

export async function getAllRecordIds(): Promise<string[]> {
  await ensureFileRegistered('records.parquet');
  const sql = `SELECT record_id FROM 'records.parquet' ORDER BY record_id ASC`;
  const rows = await runQuery<{ record_id: string }>(sql);
  return rows.map((r) => r.record_id);
}

export async function getResolvedClusters(
  t_link: number,
  variant: 'constraint' | 'no_constraint'
): Promise<Map<string, string>> {
  const fileName =
    variant === 'constraint'
      ? 'clusters_by_threshold.parquet'
      : 'clusters_by_threshold_noconstraint.parquet';

  await ensureFileRegistered(fileName);
  const sql = `
    SELECT record_id, cluster_id
    FROM '${fileName}'
    WHERE abs(t_link - ${t_link}) < 0.001
  `;
  const rows = await runQuery<{ record_id: string; cluster_id: string }>(sql);
  const map = new Map<string, string>();
  for (const r of rows) {
    map.set(r.record_id, r.cluster_id);
  }
  return map;
}

export async function searchHouseholds(term: string, limit = 20): Promise<HouseholdGolden[]> {
  await ensureFileRegistered('household_golden.parquet');
  const cleanTerm = term.trim().replace(/'/g, "''");
  if (!cleanTerm) {
    const sql = `SELECT * FROM 'household_golden.parquet' LIMIT ${limit}`;
    return runQuery<HouseholdGolden>(sql);
  }

  const sql = `
    SELECT *
    FROM 'household_golden.parquet'
    WHERE household_cluster_id ILIKE '%${cleanTerm}%'
       OR village ILIKE '%${cleanTerm}%'
       OR CAST(enrolled_members AS VARCHAR) ILIKE '%${cleanTerm}%'
       OR CAST(roster_names_unenrolled AS VARCHAR) ILIKE '%${cleanTerm}%'
    LIMIT ${limit}
  `;
  return runQuery<HouseholdGolden>(sql);
}

export async function getHouseholdGolden(
  householdClusterId: string
): Promise<HouseholdGolden | null> {
  await ensureFileRegistered('household_golden.parquet');
  const cleanId = householdClusterId.trim().replace(/'/g, "''");
  const sql = `
    SELECT *
    FROM 'household_golden.parquet'
    WHERE household_cluster_id = '${cleanId}'
    LIMIT 1
  `;
  const rows = await runQuery<HouseholdGolden>(sql);
  return rows.length > 0 ? rows[0] : null;
}

export async function loadHouseholdGraph(): Promise<HouseholdGraphData> {
  if (cachedHouseholdGraph) return cachedHouseholdGraph;
  const url = getAssetUrl('data/household_graph.json');
  const resp = await fetch(url);
  if (!resp.ok) {
    throw new Error(`Failed to load household graph: ${resp.statusText}`);
  }
  cachedHouseholdGraph = await resp.json();
  return cachedHouseholdGraph!;
}

export async function loadModelSummary(): Promise<any> {
  if (cachedModelSummary) return cachedModelSummary;
  const url = getAssetUrl('data/model_summary.json');
  const resp = await fetch(url);
  if (!resp.ok) {
    throw new Error(`Failed to load model summary: ${resp.statusText}`);
  }
  cachedModelSummary = await resp.json();
  return cachedModelSummary;
}
