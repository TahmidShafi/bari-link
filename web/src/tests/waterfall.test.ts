import { describe, it, expect } from 'vitest';
import fs from 'fs';
import path from 'path';
import { computeWaterfall } from '../data/waterfall';

describe('Fellegi-Sunter Match-Weight Waterfall', () => {
  const fixturePath = path.resolve(__dirname, 'fixtures/pairs_sample.json');
  const summaryPath = path.resolve(__dirname, '../../public/data/model_summary.json');

  const pairs = JSON.parse(fs.readFileSync(fixturePath, 'utf8'));
  const modelSummary = JSON.parse(fs.readFileSync(summaryPath, 'utf8'));

  it('loads 200 real pairs fixture', () => {
    expect(pairs).toHaveLength(200);
  });

  it('prior_log2_odds + sum(log2 bf) == match_weight within 1e-6 on all 200 real pairs', () => {
    let maxDiff = 0;

    for (const pair of pairs) {
      const result = computeWaterfall(pair, modelSummary);

      const sumLog2Bf = result.steps.reduce((sum, step) => sum + step.log2_bf, 0);
      const computedWeight = result.priorLog2Odds + sumLog2Bf;

      const diff = Math.abs(computedWeight - pair.match_weight);
      if (diff > maxDiff) maxDiff = diff;

      // Mathematical guarantee: prior_log2_odds + sum(log2 bf) == match_weight within 1e-6
      expect(diff).toBeLessThan(1e-6);
      expect(Math.abs(result.finalWeight - pair.match_weight)).toBeLessThan(1e-6);

      // Verify posterior probability calculation matches sigmoid(match_weight)
      const expectedProb = 1.0 / (1.0 + Math.pow(2, -pair.match_weight));
      expect(Math.abs(result.finalProbability - expectedProb)).toBeLessThan(1e-6);
    }

    // Even tighter: difference is floating point precision ~1e-13
    expect(maxDiff).toBeLessThan(1e-10);
  });

  it('includes term-frequency adjustment columns (bf_tf_adj_*) as distinct steps', () => {
    // Find a pair that has tf_adj columns
    const pairWithTf = pairs.find((p: any) =>
      Object.keys(p).some((k) => k.startsWith('bf_tf_adj_'))
    );

    expect(pairWithTf).toBeDefined();
    const result = computeWaterfall(pairWithTf, modelSummary);

    const tfSteps = result.steps.filter((s) => s.name.includes('(TF Adj)'));
    expect(tfSteps.length).toBeGreaterThan(0);

    for (const s of tfSteps) {
      expect(s.label).toContain('Term frequency adjustment');
    }
  });
});

