/**
 * Fellegi-Sunter Match-Weight Waterfall Calculation.
 * Computes prior log2 odds, each comparison's log2(bf) and term-frequency adjustment,
 * ending at the final match weight and posterior probability.
 *
 * Guaranteed contract: prior_log2_odds + sum(log2 bf) == match_weight within 1e-6.
 */

import type { WaterfallStep } from './types';

export interface WaterfallResult {
  priorProbability: number;
  priorLog2Odds: number;
  steps: WaterfallStep[];
  finalWeight: number;
  finalProbability: number;
}

export function computeWaterfall(
  pair: Record<string, any>,
  modelSummary: { prior: number; comparisons: any[] }
): WaterfallResult {
  const prior = modelSummary.prior;
  const priorLog2Odds = Math.log2(prior / (1.0 - prior));

  let runningWeight = priorLog2Odds;

  // Build comparison level map lookup: comp_name -> Map<cvv_string, level_info>
  const levelLookup = new Map<string, Record<string, any>>();
  for (const comp of modelSummary.comparisons) {
    const map = comp.level_map || comp.levels_by_cvv;
    if (map) {
      levelLookup.set(comp.name, map);
    }
  }

  // All columns starting with bf_
  const bfKeys = Object.keys(pair)
    .filter((k) => k.startsWith('bf_'))
    .sort((a, b) => {
      // Keep tf_adj right after its base comparison
      return a.localeCompare(b);
    });

  const steps: WaterfallStep[] = [];

  for (const key of bfKeys) {
    const bfVal = Number(pair[key]);
    if (isNaN(bfVal) || bfVal <= 0) continue;

    const log2Bf = Math.log2(bfVal);
    runningWeight += log2Bf;

    // Determine clean label
    let stepName = key.replace('bf_', '');
    let label = 'Comparison level';

    if (key.includes('tf_adj_')) {
      const baseComp = key.replace('bf_tf_adj_', '');
      stepName = `${baseComp} (TF Adj)`;
      label = `Term frequency adjustment for ${baseComp}`;
    } else {
      const gammaKey = `gamma_${stepName}`;
      const gammaVal = pair[gammaKey];
      const compMap = levelLookup.get(stepName);

      if (compMap && gammaVal !== undefined && compMap[String(gammaVal)]) {
        label = compMap[String(gammaVal)].label || compMap[String(gammaVal)].label_for_charts;
      } else if (gammaVal === -1) {
        label = 'Null / Missing field';
      }
    }

    const currentProb = 1.0 / (1.0 + Math.pow(2, -runningWeight));

    steps.push({
      name: stepName.replace(/_/g, ' '),
      label,
      log2_bf: log2Bf,
      running_weight: runningWeight,
      probability: currentProb,
      is_positive: log2Bf >= 0,
    });
  }

  const finalWeight = runningWeight;
  const finalProbability = 1.0 / (1.0 + Math.pow(2, -finalWeight));

  return {
    priorProbability: prior,
    priorLog2Odds,
    steps,
    finalWeight,
    finalProbability,
  };
}

