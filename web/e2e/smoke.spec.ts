import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

test.describe('Bari-Link Static Web App E2E Smoke Tests', () => {
  const screenshotsDir = path.resolve(__dirname, '../../docs/screenshots');

  test('full workflow: overview, slider, pair explorer, households, findings', async ({
    page,
  }, testInfo) => {
    page.on('console', (msg) => console.log(`[PAGE LOG] ${msg.text()}`));
    page.on('pageerror', (err) => console.log(`[PAGE ERROR] ${err.message}`));

    const isDesktop = testInfo.project.name === 'chromium';

    // 1. Overview: load page & persistent banner
    const t0 = performance.now();
    await page.goto('/bari-link/#overview');
    await expect(page.locator('.synthetic-banner')).toBeVisible();
    await expect(page.locator('.synthetic-banner')).toContainText(
      'All data are synthetic. No real person is represented.'
    );

    // Header facts render (wait for DuckDB initialization)
    await expect(page.locator('.facts-bar')).toBeVisible({ timeout: 15000 });
    const fmpTime = performance.now() - t0;

    await expect(page.locator('.facts-bar')).toContainText('Naive Registrations', { timeout: 15000 });
    const duckdbReadyTime = performance.now() - t0;

    // Controls and metric tiles render
    await expect(page.locator('.slider-group')).toBeVisible();
    await expect(page.locator('.slider-group')).toContainText('selected on dev data (frozen)');
    await expect(page.locator('.mode-switch-group')).toBeVisible();
    await expect(page.locator('.tiles-grid')).toBeVisible();

    // Verify Review-Queue Size and false merge recaptioned tiles
    await expect(page.locator('.tile', { hasText: 'Review-Queue Size' })).toBeVisible();
    await expect(page.locator('.tile', { hasText: 'clusters containing > 1 person' })).toBeVisible();

    // Precision & Recall Chart assertions
    const chartCard = page.locator('.card', { hasText: 'Precision & Recall' });
    await expect(chartCard).toBeVisible();
    await expect(chartCard).toContainText(
      'Holdout-optimal thresholds can differ from the dev-selected one; the frozen point is reported to avoid tuning on test data.'
    );

    // Assert that the chart contains >= 2 rendered line paths with > 10 points each
    const linePaths = chartCard.locator('g[aria-label="line"] path');
    await expect(linePaths).toHaveCount(2);

    for (let i = 0; i < 2; i++) {
      const d = await linePaths.nth(i).getAttribute('d');
      expect(d).toBeTruthy();
      const coords = d!.match(/-?\d+\.?\d*/g) || [];
      const pointCount = Math.floor(coords.length / 2);
      expect(pointCount).toBeGreaterThan(10);

      // Verify all rendered y-coordinates are valid and non-negative
      for (let j = 1; j < coords.length; j += 2) {
        const y = parseFloat(coords[j]);
        expect(y).toBeGreaterThanOrEqual(0);
      }
    }

    // Verify slider movement and measure latency
    const slider = page.locator('input[type="range"]');
    await expect(slider).toBeVisible();

    const tSlider = performance.now();
    await slider.fill('4.0');
    await slider.dispatchEvent('input');
    await page.waitForTimeout(30);
    const sliderLatency = performance.now() - tSlider;

    console.log(
      `[PERF REPORT] First Meaningful Paint: ${fmpTime.toFixed(1)} ms | Full DuckDB Ready: ${duckdbReadyTime.toFixed(1)} ms | Slider Latency: ${sliderLatency.toFixed(1)} ms`
    );

    // Switch mode to Raw Splink
    const rawBtn = page.locator('button', { hasText: 'Raw Splink edges' });
    await rawBtn.click();
    await page.waitForTimeout(500);

    // Switch back to Resolved (kinship ON)
    const resolvedBtn = page.locator('button', { hasText: 'Resolved (kinship constraint ON)' });
    await resolvedBtn.click();
    await page.waitForTimeout(300);

    // Capture Overview screenshot
    if (isDesktop) {
      await page.screenshot({
        path: path.join(screenshotsDir, 'overview.png'),
        fullPage: true,
      });
    }

    // 2. Pair Explorer
    await page.click('a[href="#pairs"]');
    await page.waitForURL('**/#pairs**');
    await expect(page.locator('h2', { hasText: 'Candidate Pair' })).toBeVisible();

    // Search for a record known to have candidate pairs
    const pairSearchInput = page.locator('input[placeholder*="Search by full name"]');
    await pairSearchInput.fill('4ac1788f1d');
    await page.waitForTimeout(500);

    // Click the matching record button
    const recordBtn = page.locator('.card button', { hasText: '4ac1788f1d' }).first();
    await recordBtn.waitFor({ state: 'visible', timeout: 15000 });
    await recordBtn.click();

    // Wait for candidate pair, side-by-side comparison and waterfall to render
    await expect(page.locator('.pair-comparison')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('h3.card-title', { hasText: 'Fellegi-Sunter Match-Weight Waterfall' })).toBeVisible({ timeout: 15000 });

    if (isDesktop) {
      await page.screenshot({
        path: path.join(screenshotsDir, 'pairs.png'),
        fullPage: true,
      });
    }

    // 3. Households
    await page.click('a[href="#households"]');
    await page.waitForURL('**/#households**');
    await expect(page.locator('h2', { hasText: 'Household Entity Resolution' })).toBeVisible();

    // Verify default deterministic selection is a multi-member household (hh_006865b83e45)
    const goldenCard = page.locator('.card', { hasText: 'Household Golden Profile' });
    await expect(goldenCard).toBeVisible({ timeout: 15000 });
    await expect(goldenCard).toContainText('hh_006865b83e45');
    await expect(goldenCard.locator('.tile', { hasText: /^Direct Reach/ })).toContainText('3');

    // Distinct enrolled programs > 0
    const programsTile = goldenCard.locator('.tile', { hasText: 'Enrolled Programs' });
    await expect(programsTile).toBeVisible();
    await expect(programsTile).toContainText('3');

    // Verify lineage table exists in collapsible details
    const lineageDetails = goldenCard.locator('details', { hasText: 'Evidence Lineage' });
    await expect(lineageDetails).toBeVisible();
    await lineageDetails.locator('summary').click();
    await expect(lineageDetails.locator('th', { hasText: 'Field' })).toBeVisible();
    await expect(lineageDetails.locator('th', { hasText: 'Resolution Rule' })).toBeVisible();
    await expect(lineageDetails.locator('th', { hasText: 'Source / Supporting Evidence' })).toBeVisible();

    // Force graph SVG renders
    await expect(page.locator('svg.household-subgraph')).toBeVisible({ timeout: 15000 });

    if (isDesktop) {
      await page.screenshot({
        path: path.join(screenshotsDir, 'households.png'),
        fullPage: true,
      });
    }

    // 4. Findings
    await page.click('a[href="#findings"]');
    await page.waitForURL('**/#findings**');
    await expect(page.locator('h2', { hasText: 'Empirical Research Findings' })).toBeVisible({
      timeout: 15000,
    });

    // Verify key cards
    await expect(page.locator('.card-title', { hasText: 'Ground-Truth Data Leakage' })).toBeVisible();
    await expect(page.locator('.card-title', { hasText: 'H1: Guardian Disambiguation' })).toBeVisible();
    await expect(page.locator('.card-title', { hasText: 'H3: Kinship as Deterministic Constraint' })).toBeVisible();
    await expect(page.locator('.card-title', { hasText: 'Cost-Ratio Sensitivity' })).toBeVisible();
    await expect(page.locator('.card-title', { hasText: 'Household Limitations' })).toBeVisible();

    // Assert bound wording in cards
    await expect(page.locator('.card', { hasText: 'Ground-Truth Data Leakage' })).toContainText(
      'Leaked ground-truth fields (guardian type, sex) inflated precision; after removing them, v1 precision fell from 0.94 to 0.61 on the synthetic holdouts.'
    );
    await expect(page.locator('.card', { hasText: 'Cost-Ratio Sensitivity' })).toContainText(
      'K is preferred when false merges cost at least 2x missed duplicates'
    );
    await expect(page.locator('.card', { hasText: 'Cost-Ratio Sensitivity' })).toContainText(
      'No clear difference (3/5 seeds)'
    );
    await expect(page.locator('.card', { hasText: 'H3: Kinship as Deterministic Constraint' })).toContainText(
      '5/5 seeds; one-sided sign test p = 0.031 (two-sided 0.0625)'
    );
    await expect(page.locator('.card', { hasText: 'Household Limitations' })).toContainText('indicating');

    // Assert footer note
    await expect(page.locator('.findings-footer')).toBeVisible();
    await expect(page.locator('.findings-footer')).toContainText(
      'All results are on synthetic data; not validated on real registries.'
    );

    // Assert no data missing errors
    await expect(page.locator('text=data missing:')).toHaveCount(0);

    if (isDesktop) {
      await page.screenshot({
        path: path.join(screenshotsDir, 'findings.png'),
        fullPage: true,
      });
    }
  });
});
