import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';
import ts from 'typescript';

describe('Findings Zero Hard-Coded Numbers Verification', () => {
  const findingsPath = path.resolve(__dirname, '../views/Findings.tsx');
  const code = fs.readFileSync(findingsPath, 'utf8');

  it('contains NO numeric literals in Findings.tsx AST', () => {
    const sourceFile = ts.createSourceFile('Findings.tsx', code, ts.ScriptTarget.Latest, true);

    const violations: { line: number; value: string }[] = [];

    function visit(node: ts.Node) {
      if (ts.isNumericLiteral(node)) {
        const { line } = sourceFile.getLineAndCharacterOfPosition(node.getStart());
        violations.push({ line: line + 1, value: node.text });
      }
      ts.forEachChild(node, visit);
    }

    visit(sourceFile);

    expect(
      violations,
      `Found numeric literals in Findings.tsx: ${JSON.stringify(violations)}`
    ).toHaveLength(0);
  });

  it('renders strictly from headline.json and imports no hardcoded figures', () => {
    expect(code).toContain('getHeadlineFindings');
    expect(code).not.toContain('4136');
    expect(code).not.toContain('3689');
    expect(code).not.toContain('4841');
    expect(code).not.toContain('0.9656');
    expect(code).not.toContain('0.5277');
    expect(code).not.toContain('0.6823');
    expect(code).not.toContain('812.2');
  });
});

