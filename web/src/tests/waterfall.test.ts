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

  it('reproduces Splink-derived comparison level labels exactly across 100 real pairs fixture', () => {
    const labelsFixturePath = path.resolve(__dirname, 'fixtures/pair_labels_100.json');
    const pairs100 = JSON.parse(fs.readFileSync(labelsFixturePath, 'utf8'));

    expect(pairs100).toHaveLength(100);

    for (const { pair, expected_labels } of pairs100) {
      const result = computeWaterfall(pair, modelSummary);

      for (const step of result.steps) {
        if (step.name.includes('(TF Adj)')) continue;
        const compKey = step.name.replace(/ /g, '_');
        if (expected_labels[compKey]) {
          expect(step.label).toBe(expected_labels[compKey]);
        }
      }
    }
  });

  it('correctly labels holdout_5 pair 4ac1788f1d vs 9c69280acb (P0 regression check)', () => {
    // Specifically test the exact pair reported in the bug report
    const pair = {
      record_id_l: '4ac1788f1d',
      record_id_r: '9c69280acb',
      match_weight: 18.3696,
      match_probability: 0.999997,
      gamma_given_name: 5,
      bf_given_name: 59.227,
      bf_tf_adj_given_name: 2.068,
      gamma_guardian_name: 7,
      bf_guardian_name: 295.796,
      bf_tf_adj_guardian_name: 0.515,
      gamma_phone: 2,
      bf_phone: 4313.07,
      gamma_birth_year: -1,
      bf_birth_year: 1.0,
      gamma_village: 2,
      bf_village: 3.989,
      gamma_union_raw: 1,
      bf_union_raw: 18.0,
      gamma_sex_raw: -1,
      bf_sex_raw: 1.0,
      gamma_title_token: 1,
      bf_title_token: 3.683,
    };

    const result = computeWaterfall(pair, modelSummary);

    const stepVillage = result.steps.find((s) => s.name === 'village');
    expect(stepVillage?.label).toBe('Exact match on village_canon');

    const stepPhone = result.steps.find((s) => s.name === 'phone');
    expect(stepPhone?.label).toBe('Exact match on phone_norm');

    const stepGuardian = result.steps.find((s) => s.name === 'guardian name');
    expect(stepGuardian?.label).toBe('Exact match on guardian_canon');

    const stepBirthYear = result.steps.find((s) => s.name === 'birth year');
    expect(stepBirthYear?.label).toBe('birth_year_est is NULL');
  });
});

