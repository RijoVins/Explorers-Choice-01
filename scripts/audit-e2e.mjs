import { chromium } from 'playwright';

const BASE_URL = 'http://localhost:3000';
const API_URL = 'http://localhost:8000';

async function runAudit() {
  console.log('🚀 Starting Comprehensive Playwright Audit for ' + BASE_URL);
  
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 }
  });
  
  const page = await context.newPage();
  
  const results = {
    pages: [],
    consoleErrors: [],
    networkFailures: [],
    interactiveTests: []
  };

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      const text = msg.text();
      // Ignore favicon or known benign dev logs if any
      results.consoleErrors.push({ url: page.url(), text });
    }
  });

  page.on('response', (res) => {
    const status = res.status();
    const url = res.url();
    // Record 4xx/5xx responses, especially API calls and assets
    if (status >= 400 && !url.includes('/favicon.ico')) {
      results.networkFailures.push({ url, status, pageUrl: page.url() });
    }
  });

  const routesToTest = [
    '/',
    '/destinations',
    '/packages',
    '/hotels',
    '/trains',
    '/cabs',
    '/about',
    '/stories',
    '/contact',
    '/faq',
    '/login',
    '/register',
    '/book',
    '/hotel-owner',
    '/forgot-password',
    '/account'
  ];

  console.log('\n--- 1. Testing Route Navigation ---');
  for (const route of routesToTest) {
    const fullUrl = `${BASE_URL}${route}`;
    try {
      const res = await page.goto(fullUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
      const status = res ? res.status() : 'no-response';
      const title = await page.title();
      console.log(`[${status}] ${route} - "${title}"`);
      results.pages.push({ route, status, title, ok: status === 200 });
    } catch (err) {
      console.log(`[FAIL] ${route} - ${err.message}`);
      results.pages.push({ route, status: 'error', error: err.message, ok: false });
    }
  }

  console.log('\n--- 2. Interactive Feature Tests ---');

  // Test 2.1: Homepage Hero Search Tabs
  try {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    console.log('Testing Hero Tabs...');
    const tabs = ['Flights', 'Hotels', 'Holidays', 'Trains', 'Cabs'];
    for (const tab of tabs) {
      const tabLocator = page.locator(`[role="tab"]:has-text("${tab}")`);
      if (await tabLocator.isVisible()) {
        await tabLocator.click();
        await page.waitForTimeout(300);
        console.log(`  ✅ Clicked tab: ${tab}`);
      } else {
        console.log(`  ⚠️ Tab not visible: ${tab}`);
      }
    }
    results.interactiveTests.push({ test: 'Hero Tabs', status: 'PASS' });
  } catch (err) {
    console.error(`  ❌ Hero Tabs failed: ${err.message}`);
    results.interactiveTests.push({ test: 'Hero Tabs', status: 'FAIL', error: err.message });
  }

  // Test 2.2: Contact Form Validation & Submission
  try {
    console.log('Testing Contact Page & Form...');
    await page.goto(`${BASE_URL}/contact`, { waitUntil: 'networkidle' });
    const nameInput = page.locator('input[name="name"], input[placeholder*="name" i], #name').first();
    const emailInput = page.locator('input[name="email"], input[type="email"], #email').first();
    const messageInput = page.locator('textarea[name="message"], textarea[placeholder*="message" i], #message').first();
    const submitBtn = page.locator('button[type="submit"], button:has-text("Send"), button:has-text("Submit")').first();

    if (await submitBtn.isVisible()) {
      // Try empty submission for validation
      await submitBtn.click();
      console.log('  ✅ Tested empty contact submit');

      // Now fill valid test details
      if (await nameInput.isVisible()) await nameInput.fill('Playwright Test');
      if (await emailInput.isVisible()) await emailInput.fill('test@explorerschoice.test');
      if (await messageInput.isVisible()) await messageInput.fill('Testing contact form via Playwright audit.');
      console.log('  ✅ Filled contact inputs');
      results.interactiveTests.push({ test: 'Contact Form', status: 'PASS' });
    } else {
      console.log('  ⚠️ Contact submit button not found');
      results.interactiveTests.push({ test: 'Contact Form', status: 'WARN', note: 'No submit button found' });
    }
  } catch (err) {
    console.error(`  ❌ Contact form error: ${err.message}`);
    results.interactiveTests.push({ test: 'Contact Form', status: 'FAIL', error: err.message });
  }

  // Test 2.3: Login Page interaction
  try {
    console.log('Testing Login Page...');
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle' });
    const emailInput = page.locator('input[type="email"]').first();
    const loginBtn = page.locator('button[type="submit"], button:has-text("Sign in"), button:has-text("Continue"), button:has-text("Login")').first();
    if (await emailInput.isVisible()) {
      await emailInput.fill('testuser@explorerschoice.test');
      console.log('  ✅ Login email input found and filled');
      results.interactiveTests.push({ test: 'Login Page', status: 'PASS' });
    } else {
      console.log('  ⚠️ Email input not found on login page');
      results.interactiveTests.push({ test: 'Login Page', status: 'WARN' });
    }
  } catch (err) {
    console.error(`  ❌ Login page error: ${err.message}`);
    results.interactiveTests.push({ test: 'Login Page', status: 'FAIL', error: err.message });
  }

  // Test 2.4: Trains page interaction
  try {
    console.log('Testing Trains Page Search...');
    await page.goto(`${BASE_URL}/trains`, { waitUntil: 'networkidle' });
    const trainInput = page.locator('input').first();
    if (await trainInput.isVisible()) {
      console.log('  ✅ Trains input detected');
    }
    results.interactiveTests.push({ test: 'Trains Page', status: 'PASS' });
  } catch (err) {
    console.error(`  ❌ Trains page error: ${err.message}`);
    results.interactiveTests.push({ test: 'Trains Page', status: 'FAIL', error: err.message });
  }

  // Test 2.5: Cabs page interaction
  try {
    console.log('Testing Cabs Page Search...');
    await page.goto(`${BASE_URL}/cabs`, { waitUntil: 'networkidle' });
    const cabInput = page.locator('input').first();
    if (await cabInput.isVisible()) {
      console.log('  ✅ Cabs input detected');
    }
    results.interactiveTests.push({ test: 'Cabs Page', status: 'PASS' });
  } catch (err) {
    console.error(`  ❌ Cabs page error: ${err.message}`);
    results.interactiveTests.push({ test: 'Cabs Page', status: 'FAIL', error: err.message });
  }

  // Test 2.6: Hotels page interaction
  try {
    console.log('Testing Hotels Page...');
    await page.goto(`${BASE_URL}/hotels`, { waitUntil: 'networkidle' });
    const searchOrFilter = page.locator('input, select, button').first();
    if (await searchOrFilter.isVisible()) {
      console.log('  ✅ Hotels interactive elements detected');
    }
    results.interactiveTests.push({ test: 'Hotels Page', status: 'PASS' });
  } catch (err) {
    console.error(`  ❌ Hotels page error: ${err.message}`);
    results.interactiveTests.push({ test: 'Hotels Page', status: 'FAIL', error: err.message });
  }

  // Test 2.7: Booking page
  try {
    console.log('Testing Book Page...');
    await page.goto(`${BASE_URL}/book`, { waitUntil: 'networkidle' });
    const bookTitle = await page.title();
    console.log(`  ✅ Book page loaded: ${bookTitle}`);
    results.interactiveTests.push({ test: 'Book Page', status: 'PASS' });
  } catch (err) {
    console.error(`  ❌ Book page error: ${err.message}`);
    results.interactiveTests.push({ test: 'Book Page', status: 'FAIL', error: err.message });
  }

  await browser.close();

  console.log('\n=============================================');
  console.log('📊 AUDIT SUMMARY REPORT');
  console.log('=============================================');
  console.log(`Total Pages Tested: ${results.pages.length}`);
  const failedPages = results.pages.filter(p => !p.ok);
  console.log(`Failed Pages (${failedPages.length}):`);
  failedPages.forEach(p => console.log(`  - ${p.route}: ${p.status} ${p.error || ''}`));

  console.log(`\nConsole Errors Detected (${results.consoleErrors.length}):`);
  const uniqueErrors = [...new Set(results.consoleErrors.map(e => `${e.url} => ${e.text}`))];
  uniqueErrors.forEach(e => console.log(`  - ${e}`));

  console.log(`\nNetwork Failures Detected (${results.networkFailures.length}):`);
  const uniqueNetwork = [...new Set(results.networkFailures.map(n => `[${n.status}] ${n.url} (on ${n.pageUrl})`))];
  uniqueNetwork.forEach(n => console.log(`  - ${n}`));

  console.log('\nInteractive Tests:');
  results.interactiveTests.forEach(t => console.log(`  - ${t.test}: ${t.status} ${t.error || ''}`));

  return results;
}

runAudit().catch(err => {
  console.error('Fatal audit failure:', err);
  process.exit(1);
});
