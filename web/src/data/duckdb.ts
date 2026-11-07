/**
 * DuckDB-Wasm client-side database management.
 * Loads jsDelivr WASM bundles via a same-origin Blob worker.
 * Lazy registers model-visible parquet files using absolute URLs derived from BASE_URL.
 */

import * as duckdb from '@duckdb/duckdb-wasm';

let dbInstance: duckdb.AsyncDuckDB | null = null;
let connInstance: duckdb.AsyncDuckDBConnection | null = null;
let initPromise: Promise<duckdb.AsyncDuckDB> | null = null;

const registeredFiles = new Set<string>();

export function getAssetUrl(relPath: string): string {
  const baseUrl = import.meta.env.BASE_URL.endsWith('/')
    ? import.meta.env.BASE_URL
    : `${import.meta.env.BASE_URL}/`;
  const cleanPath = relPath.startsWith('/') ? relPath.slice(1) : relPath;
  return new URL(`${baseUrl}${cleanPath}`, window.location.origin).href;
}

export async function initDuckDB(): Promise<duckdb.AsyncDuckDB> {
  if (dbInstance) return dbInstance;
  if (initPromise) return initPromise;

  initPromise = (async () => {
    const JSDELIVR_BUNDLES = duckdb.getJsDelivrBundles();
    const bundle = await duckdb.selectBundle(JSDELIVR_BUNDLES);

    // Same-origin Blob worker pattern
    const workerBlob = new Blob([`importScripts("${bundle.mainWorker!}");`], {
      type: 'text/javascript',
    });
    const workerUrl = URL.createObjectURL(workerBlob);
    const worker = new Worker(workerUrl);

    const logger = new duckdb.VoidLogger();
    const db = new duckdb.AsyncDuckDB(logger, worker);
    await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
    URL.revokeObjectURL(workerUrl);

    dbInstance = db;
    connInstance = await db.connect();
    return db;
  })();

  return initPromise;
}

export async function getConnection(): Promise<duckdb.AsyncDuckDBConnection> {
  await initDuckDB();
  return connInstance!;
}

export async function ensureFileRegistered(fileName: string): Promise<void> {
  const db = await initDuckDB();
  if (registeredFiles.has(fileName)) return;

  const url = getAssetUrl(`data/${fileName}`);
  await db.registerFileURL(fileName, url, duckdb.DuckDBDataProtocol.HTTP, false);
  registeredFiles.add(fileName);
}

export async function runQuery<T = any>(sql: string): Promise<T[]> {
  const conn = await getConnection();
  const result = await conn.query(sql);
  const fields = result.schema.fields.map((f) => f.name);
  const rows: T[] = [];
  for (let i = 0; i < result.numRows; i++) {
    const raw = result.get(i) as any;
    const row: any = {};
    for (const f of fields) {
      const val = raw ? raw[f] : undefined;
      if (typeof val === 'bigint') {
        row[f] = Number(val);
      } else if (val && typeof val.toArray === 'function') {
        row[f] = val.toArray();
      } else {
        row[f] = val;
      }
    }
    rows.push(row as T);
  }
  return rows;
}
