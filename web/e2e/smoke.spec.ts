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
    await expect(page.locator('.mode-switch-group')).toBeVisible();
    await expect(page.locator('.tiles-grid')).toBeVisible();

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

    // Search for a known household
    const hhSearchInput = page.locator('input[placeholder*="Search by person name"]');
    await hhSearchInput.fill('hh_000c8744bd0f');
    await page.waitForTimeout(500);

    // Select matching household button
    const firstHhBtn = page.locator('.card button', { hasText: 'hh_000c8744bd0f' }).first();
    await firstHhBtn.waitFor({ state: 'visible', timeout: 15000 });
    await firstHhBtn.click();

    // Wait for Household profile and force graph SVG
    await expect(page.locator('.card-title', { hasText: 'Household Golden Profile' })).toBeVisible({
      timeout: 15000,
    });
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

    if (isDesktop) {
      await page.screenshot({
        path: path.join(screenshotsDir, 'findings.png'),
        fullPage: true,
      });
    }
  });
});
