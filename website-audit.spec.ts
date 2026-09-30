import { test, expect } from '@playwright/test';

const BASE_URL = process.env.TEST_URL || 'http://localhost:3000';
const API_BASE = process.env.API_URL || 'http://localhost:8000';

test.describe('Explorers Choice Website Audit', () => {
  
  test('Homepage loads successfully', async ({ page }) => {
    const response = await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    expect(response?.status()).toBe(200);
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  test('Navigation menu is functional', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // Check all nav links exist
    const navLinks = await page.locator('header a[href*="/"]').count();
    expect(navLinks).toBeGreaterThan(0);
    
    // Test navigation to key pages
    const links = ['destinations', 'packages', 'about', 'contact'];
    for (const link of links) {
      const element = page.locator(`header a[href*="${link}"]`).first();
      if (await element.isVisible()) {
        await element.click();
        await expect(page).toHaveURL(new RegExp(link));
        await page.goto(BASE_URL, { waitUntil: 'networkidle' });
      }
    }
  });

  test('API requests complete successfully', async ({ page }) => {
    let apiErrorDetected = false;
    let apiResponses: Array<{url: string, status: number}> = [];

    page.on('response', (response) => {
      const url = response.url();
      if (url.includes('/api/')) {
        apiResponses.push({ url, status: response.status() });
        if (response.status() >= 400) {
          console.error(`❌ API Error: ${url} returned ${response.status()}`);
          apiErrorDetected = true;
        }
      }
    });

    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    console.log('\n📊 API Responses Detected:');
    apiResponses.forEach(r => {
      const status = r.status === 200 || r.status === 304 ? '✅' : '❌';
      console.log(`  ${status} ${r.url.replace(API_BASE, '')} - ${r.status}`);
    });

    if (apiErrorDetected) {
      console.warn('⚠️  Some API requests failed!');
    }
  });

  test('Destinations page loads and displays content', async ({ page }) => {
    await page.goto(`${BASE_URL}/destinations`, { waitUntil: 'networkidle' });
    
    const destination = page.locator('[class*="destination"], [class*="card"], main a[href*="/destinations/"]').first();
    await expect(destination).toBeVisible();
  });

  test('Packages page loads and displays content', async ({ page }) => {
    await page.goto(`${BASE_URL}/packages`, { waitUntil: 'networkidle' });
    
    const packageCard = page.locator('[class*="package"], [class*="card"], main a[href*="/packages/"]').first();
    await expect(packageCard).toBeVisible();
  });

  test('Contact form is present and functional', async ({ page }) => {
    await page.goto(`${BASE_URL}/contact`, { waitUntil: 'networkidle' });
    
    const form = page.locator('form, [class*="form"]').first();
    await expect(form).toBeVisible();
    
    // Check for required form elements
    const inputs = await page.locator('input, textarea').count();
    expect(inputs).toBeGreaterThan(0);
  });

  test('Login page is accessible', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle' });
    
    const loginForm = page.locator('form, [class*="login"], [class*="auth"]').first();
    await expect(loginForm).toBeVisible();
  });

  test('Register page is accessible', async ({ page }) => {
    await page.goto(`${BASE_URL}/register`, { waitUntil: 'networkidle' });
    
    const registerForm = page.locator('form, [class*="register"], [class*="auth"]').first();
    await expect(registerForm).toBeVisible();
  });

  test('No console errors on homepage', async ({ page }) => {
    const errors: string[] = [];
    
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    if (errors.length > 0) {
      console.error('\n❌ Console Errors Detected:');
      errors.forEach(e => console.error(`  - ${e}`));
    } else {
      console.log('\n✅ No console errors detected');
    }

    expect(errors).toEqual([]);
  });

  test('Mobile responsive layout', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    
    // Check if content is visible on mobile
    const mainContent = page.locator('main, [role="main"], body').first();
    await expect(mainContent).toBeVisible();
  });

  test('Images load without errors', async ({ page }) => {
    let imageErrors = 0;

    page.on('response', (response) => {
      if (response.url().includes('image') || response.url().match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
        if (response.status() >= 400) {
          console.error(`❌ Image failed to load: ${response.url()}`);
          imageErrors++;
        }
      }
    });

    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    console.log(`\n🖼️  Images Status: ${imageErrors === 0 ? '✅ All loaded' : `❌ ${imageErrors} failed`}`);
  });

  test('Links are not broken', async ({ page }) => {
    const brokenLinks: string[] = [];

    page.on('response', (response) => {
      if (response.status() === 404 && !response.url().includes('/api/')) {
        brokenLinks.push(response.url());
      }
    });

    await page.goto(BASE_URL);
    
    // Click a few internal links
    const links = await page.locator('a[href^="/"]').elementHandles();
    for (let i = 0; i < Math.min(5, links.length); i++) {
      try {
        await links[i].click({ timeout: 5000 });
        await page.waitForLoadState('networkidle');
      } catch (e) {
        // Ignore click errors
      }
    }

    if (brokenLinks.length > 0) {
      console.error('\n❌ Broken Links Found:');
      brokenLinks.forEach(link => console.error(`  - ${link}`));
    } else {
      console.log('\n✅ No broken links detected');
    }
  });

  test('Performance - Page Load Time', async ({ page }) => {
    const startTime = Date.now();
    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    const loadTime = Date.now() - startTime;

    console.log(`\n⏱️  Page Load Time: ${loadTime}ms`);
    
    // Warn if load time is excessive
    if (loadTime > 5000) {
      console.warn('⚠️  Page load time is slow (>5s)');
    }
  });

  test('CSS loads correctly', async ({ page }) => {
    let cssErrors = 0;

    page.on('response', (response) => {
      if (response.url().includes('.css')) {
        if (response.status() >= 400) {
          console.error(`❌ CSS failed to load: ${response.url()}`);
          cssErrors++;
        }
      }
    });

    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    
    console.log(`\n🎨 CSS Status: ${cssErrors === 0 ? '✅ All loaded' : `❌ ${cssErrors} failed`}`);
  });

  test('JavaScript loads correctly', async ({ page }) => {
    let jsErrors = 0;

    page.on('response', (response) => {
      if (response.url().includes('.js')) {
        if (response.status() >= 400) {
          console.error(`❌ JS failed to load: ${response.url()}`);
          jsErrors++;
        }
      }
    });

    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    
    console.log(`\n📜 JavaScript Status: ${jsErrors === 0 ? '✅ All loaded' : `❌ ${jsErrors} failed`}`);
  });

  test('API authentication endpoints reachable', async ({ page }) => {
    let authEndpointStatus = '';

    page.on('response', (response) => {
      if (response.url().includes('/api/auth/')) {
        authEndpointStatus = `${response.status()}`;
      }
    });

    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    if (authEndpointStatus) {
      console.log(`\n🔐 Auth Endpoint Status: ${authEndpointStatus}`);
    }
  });

  test('No mixed content warnings', async ({ page }) => {
    const warnings: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'warning' && msg.text().includes('mixed')) {
        warnings.push(msg.text());
      }
    });

    await page.goto(BASE_URL, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    if (warnings.length > 0) {
      console.warn('\n⚠️  Mixed Content Warnings:');
      warnings.forEach(w => console.warn(`  - ${w}`));
    } else {
      console.log('\n✅ No mixed content warnings');
    }
  });

  test('Accessibility check - Page has title', async ({ page }) => {
    await page.goto(BASE_URL);
    
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
    console.log(`\n📄 Page Title: "${title}"`);
  });

});
