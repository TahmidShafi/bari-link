import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

function getAllFiles(dir: string): string[] {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name !== 'node_modules' && entry.name !== 'dist' && entry.name !== 'fixtures') {
        files.push(...getAllFiles(fullPath));
      }
    } else if (
      entry.isFile() &&
      (entry.name.endsWith('.ts') || entry.name.endsWith('.tsx') || entry.name.endsWith('.js'))
    ) {
      files.push(fullPath);
    }
  }
  return files;
}

describe('Evaluation Isolation Scan', () => {
  const srcDir = path.resolve(__dirname, '..');

  it('contains NO string "eval" in src/data/** or src/workers/**', () => {
    const dataAndWorkerFiles = [
      ...getAllFiles(path.join(srcDir, 'data')),
      ...getAllFiles(path.join(srcDir, 'workers')),
    ];

    const violations: { file: string; line: number; text: string }[] = [];

    for (const file of dataAndWorkerFiles) {
      const content = fs.readFileSync(file, 'utf8');
      const lines = content.split('\n');

      lines.forEach((line, idx) => {
        // Look for "eval" as a substring (case-insensitive)
        if (/eval/i.test(line)) {
          violations.push({
            file: path.relative(srcDir, file),
            line: idx + 1,
            text: line.trim(),
          });
        }
      });
    }

    expect(
      violations,
      `Found disallowed "eval" references in data/workers:\n${violations
        .map((v) => `  ${v.file}:${v.line} -> ${v.text}`)
        .join('\n')}`
    ).toHaveLength(0);
  });

  it('contains NO string "data/eval" outside src/eval/**', () => {
    const allSrcFiles = getAllFiles(srcDir);
    const nonEvalFiles = allSrcFiles.filter((f) => !f.includes(path.join('src', 'eval')));

    const violations: { file: string; line: number; text: string }[] = [];

    for (const file of nonEvalFiles) {
      // Don't scan the test file itself for the search string
      if (file.includes('eval_isolation.test.ts')) continue;

      const content = fs.readFileSync(file, 'utf8');
      const lines = content.split('\n');

      lines.forEach((line, idx) => {
        if (line.includes('data/eval')) {
          violations.push({
            file: path.relative(srcDir, file),
            line: idx + 1,
            text: line.trim(),
          });
        }
      });
    }

    expect(
      violations,
      `Found disallowed "data/eval" references outside src/eval:\n${violations
        .map((v) => `  ${v.file}:${v.line} -> ${v.text}`)
        .join('\n')}`
    ).toHaveLength(0);
  });
});

