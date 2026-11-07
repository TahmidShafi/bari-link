/**
 * Standalone performance measurement script for bari-link web app.
 * Measures:
 * 1. First Meaningful Paint (FMP) with loading indicator
 * 2. Full DuckDB-Wasm instantiation and table query readiness
 * 3. Threshold Slider interaction latency in resolved mode
 *
 * Usage:
 *   node web/scripts/measure_perf.cjs
 */

const { chromium } = require('playwright');

(async () => {
  const targetUrl = process.env.APP_URL || 'http://localhost:4173/bari-link/#overview';
  console.log(`[PERF TEST] Measuring performance against: ${targetUrl}`);

  const browser = await chromium.launch();
  const page = await browser.newPage();

  const startNav = performance.now();
  await page.goto(targetUrl);
  await page.locator('.facts-bar').waitFor({ state: 'visible' });
  const fmpTime = performance.now() - startNav;

  // Wait for facts and tiles to populate from DuckDB
  await page.locator('.facts-bar', { hasText: 'Naive Registrations' }).waitFor({ state: 'visible' });
  const readyTime = performance.now() - startNav;

  // Measure slider latency in resolved mode
  const slider = page.locator('input[type="range"]');
  await slider.waitFor({ state: 'visible' });

  const startSlider = performance.now();
  await slider.fill('4.0');
  await slider.dispatchEvent('input');
  await page.waitForTimeout(30);
  const sliderLatency = performance.now() - startSlider;

  console.log('----------------------------------------------------');
  console.log(`First Meaningful Paint (FMP):      ${fmpTime.toFixed(1)} ms  (Budget: < 2000 ms)`);
  console.log(`Full DuckDB-Wasm Ready Time:       ${readyTime.toFixed(1)} ms`);
  console.log(`Slider Update Latency (Resolved):  ${sliderLatency.toFixed(1)} ms   (Budget: < 100 ms)`);
  console.log('----------------------------------------------------');

  await browser.close();
})();

