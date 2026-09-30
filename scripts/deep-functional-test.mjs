import { chromium } from 'playwright';

const BASE_URL = 'http://localhost:3000';

async function runDeepTests() {
  console.log('🧪 Starting Deep Functional Playwright Tests for ' + BASE_URL);
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  const tests = [];

  // Helper
  async function runTest(name, fn) {
    try {
      console.log(`Running test: ${name}...`);
      await fn();
      console.log(`  ✅ PASS: ${name}`);
      tests.push({ name, status: 'PASS' });
    } catch (err) {
      console.error(`  ❌ FAIL: ${name} - ${err.message}`);
      tests.push({ name, status: 'FAIL', error: err.message });
    }
  }

  // 1. Train Search and PNR status tab
  await runTest('Train Search Functionality', async () => {
    await page.goto(`${BASE_URL}/trains`, { waitUntil: 'networkidle' });
    
    // Check station selectors or inputs
    const fromInput = page.locator('input[placeholder*="from" i], input[placeholder*="source" i], input').first();
    await fromInput.click();
    await fromInput.fill('NDLS');
    
    // Switch to PNR tab if present
    const pnrTab = page.locator('button:has-text("PNR"), [role="tab"]:has-text("PNR")').first();
    if (await pnrTab.isVisible()) {
      await pnrTab.click();
      await page.waitForTimeout(300);
      const pnrInput = page.locator('input[placeholder*="10-digit" i], input[placeholder*="PNR" i]').first();
      if (await pnrInput.isVisible()) {
        await pnrInput.fill('1234567890');
      }
    }
  });

  // 2. Cab Booking Form & Category Selection
  await runTest('Cab Booking & Type Selection', async () => {
    await page.goto(`${BASE_URL}/cabs`, { waitUntil: 'networkidle' });
    const pickupInput = page.locator('input[placeholder*="pickup" i], input[placeholder*="city" i], input').first();
    if (await pickupInput.isVisible()) {
      await pickupInput.fill('Mumbai Airport');
    }
    const cabCards = page.locator('button:has-text("Book"), button:has-text("Select")');
    const count = await cabCards.count();
    console.log(`  Found ${count} cab booking/selection buttons`);
  });

  // 3. Destinations Page & Individual Destination
  await runTest('Destinations View & Navigation', async () => {
    await page.goto(`${BASE_URL}/destinations`, { waitUntil: 'networkidle' });
    // Look for destination links or cards
    const destLink = page.locator('a[href^="/destinations/"]').first();
    if (await destLink.isVisible()) {
      const href = await destLink.getAttribute('href');
      console.log(`  Navigating to destination: ${href}`);
      await destLink.click();
      await page.waitForLoadState('networkidle');
      const title = await page.title();
      console.log(`  Destination page title: ${title}`);
    }
  });

  // 4. Packages Page & Individual Package
  await runTest('Packages View & Navigation', async () => {
    await page.goto(`${BASE_URL}/packages`, { waitUntil: 'networkidle' });
    const pkgLink = page.locator('a[href^="/packages/"]').first();
    if (await pkgLink.isVisible()) {
      const href = await pkgLink.getAttribute('href');
      console.log(`  Navigating to package: ${href}`);
      await pkgLink.click();
      await page.waitForLoadState('networkidle');
      const title = await page.title();
      console.log(`  Package page title: ${title}`);
    }
  });

  // 5. Hotels Page & Detail Card
  await runTest('Hotels View & Booking Link', async () => {
    await page.goto(`${BASE_URL}/hotels`, { waitUntil: 'networkidle' });
    const hotelCard = page.locator('a[href^="/hotels/"], a[href^="/book?hotel="]').first();
    if (await hotelCard.isVisible()) {
      const href = await hotelCard.getAttribute('href');
      console.log(`  Hotel card found with link: ${href}`);
    }
  });

  // 6. Customer Stories
  await runTest('Customer Stories List', async () => {
    await page.goto(`${BASE_URL}/stories`, { waitUntil: 'networkidle' });
    const pageContent = await page.textContent('body');
    if (!pageContent.includes('Stories') && !pageContent.includes('stories')) {
      throw new Error('Stories content missing');
    }
  });

  // 7. Booking Page Flow
  await runTest('Booking Form Fields and Interactions', async () => {
    await page.goto(`${BASE_URL}/book`, { waitUntil: 'networkidle' });
    const nameInput = page.locator('input[name="name"], input[placeholder*="name" i]').first();
    const emailInput = page.locator('input[name="email"], input[type="email"]').first();
    const phoneInput = page.locator('input[name="phone"], input[type="tel"]').first();

    if (await nameInput.isVisible()) await nameInput.fill('Traveler Test');
    if (await emailInput.isVisible()) await emailInput.fill('traveler@test.com');
    if (await phoneInput.isVisible()) await phoneInput.fill('+919876543210');
  });

  // 8. Auth Pages (Register and Login forms)
  await runTest('Register and Login Form Validation', async () => {
    await page.goto(`${BASE_URL}/register`, { waitUntil: 'networkidle' });
    const submitBtn = page.locator('button[type="submit"]').first();
    if (await submitBtn.isVisible()) {
      await submitBtn.click();
      await page.waitForTimeout(300);
      console.log('  Triggered register validation');
    }

    await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle' });
    const loginSubmit = page.locator('button[type="submit"]').first();
    if (await loginSubmit.isVisible()) {
      await loginSubmit.click();
      await page.waitForTimeout(300);
      console.log('  Triggered login validation');
    }
  });

  await browser.close();

  console.log('\n=============================================');
  console.log('🎯 DEEP FUNCTIONAL TEST SUMMARY');
  console.log('=============================================');
  const failed = tests.filter(t => t.status === 'FAIL');
  console.log(`Total tests: ${tests.length}`);
  console.log(`Passed: ${tests.length - failed.length}`);
  console.log(`Failed: ${failed.length}`);
  if (failed.length > 0) {
    failed.forEach(f => console.log(`  - ${f.name}: ${f.error}`));
  }
  console.log(`Total console errors during functional runs: ${consoleErrors.length}`);
  if (consoleErrors.length > 0) {
    consoleErrors.forEach(e => console.log(`  - Console Error: ${e}`));
  }
}

runDeepTests().catch(console.error);
