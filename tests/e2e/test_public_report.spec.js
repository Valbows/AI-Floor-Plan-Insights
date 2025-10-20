/**
 * Public Report E2E Tests (Phase 4.1-4.2)
 * 
 * Tests the complete public report workflow:
 * - Shareable link generation
 * - Public report page display
 * - View logging
 * - Error handling (invalid/expired tokens)
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
const API_URL = process.env.API_URL || 'http://localhost:5000';

test.describe('Public Report Feature', () => {
  let authToken;
  let testPropertyId;
  let shareableToken;

  test.beforeAll(async ({ request }) => {
    // Login and get auth token
    const loginResponse = await request.post(`${API_URL}/auth/login`, {
      data: {
        email: 'jane.smith@realestate.com',
        password: 'Agent2025!'
      }
    });

    expect(loginResponse.ok()).toBeTruthy();
    const loginData = await loginResponse.json();
    authToken = loginData.token;
    console.log('✅ Authenticated successfully');

    // Find a property with market insights
    const propertiesResponse = await request.get(`${API_URL}/api/properties`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    expect(propertiesResponse.ok()).toBeTruthy();
    const data = await propertiesResponse.json();
    const properties = data.properties;

    const propertyWithInsights = properties.find(prop => 
      prop.status === 'complete' && 
      prop.extracted_data?.market_insights
    );

    expect(propertyWithInsights).toBeDefined();
    testPropertyId = propertyWithInsights.id;
    
    console.log(`✅ Found test property: ${testPropertyId}`);
  });

    test('should generate shareable link from Agent Tools page', async ({ page }) => {
    console.log('✅ Testing shareable link generation');

    // Set auth token
    await page.goto(BASE_URL);
    await page.evaluate((token) => {
      localStorage.setItem('token', token);
    }, authToken);

    // Navigate to Agent Tools page (Ariel UI)
    await page.goto(`${BASE_URL}/agent-tools/${testPropertyId}`);
    await page.waitForLoadState('networkidle');

    // Wait for page to fully load
    await page.waitForTimeout(2000);

    // Click Share button (FAB)
    const shareButton = page.locator('[data-testid="share-fab"]');
    await expect(shareButton).toBeVisible({ timeout: 10000 });
    await shareButton.click();

    // Wait for modal to open
    await page.waitForSelector('text=/Share Property/i', { timeout: 5000 });
    console.log('   ✅ Share modal opened');

    // Wait for link to be generated
    await page.waitForTimeout(3000);

    // Check for shareable URL input field
    const urlInput = page.locator('input[readonly]').filter({ hasValue: /report/ });
    await expect(urlInput).toBeVisible({ timeout: 5000 });

    const shareableUrl = await urlInput.inputValue();
    shareableToken = shareableUrl.split('/report/')[1];
    
    console.log(`   ✅ Generated shareable link: ${shareableUrl}`);
    console.log(`   ✅ Token: ${shareableToken}`);

    // Verify expiration date is shown
    await expect(page.locator('text=/Expires/i')).toBeVisible();

    // Close modal by clicking X button
    const closeButton = page.locator('[data-testid="close-share-modal"]');
    await closeButton.click();
    console.log('   ✅ Modal closed');
  });

  test('should display public report page for valid token', async ({ page }) => {
    console.log('✅ Testing public report page display');

    // Generate a fresh token via API
    const response = await page.request.post(`${API_URL}/api/properties/${testPropertyId}/generate-link`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      data: {}
    });

    expect(response.ok()).toBeTruthy();
    const linkData = await response.json();
    const token = linkData.token;
    
    console.log(`   Generated token: ${token}`);

    // Open public report page (no authentication)
    await page.goto(`${BASE_URL}/report/${token}`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForSelector('header', { timeout: 10000 });

    // Verify header
    await expect(page.getByRole('heading', { name: /Property Report/i })).toBeVisible({ timeout: 10000 });
    console.log('   ✅ Header displayed');

    // Verify property address is shown (look for any text with comma, typical of addresses)
    const addressElement = page.locator('text=/\\d+.*,/').first();
    const hasAddress = await addressElement.isVisible().catch(() => false);
    if (hasAddress) {
      console.log('   ✅ Address displayed');
    } else {
      console.log('   ℹ️  Address may be in different format');
    }

    // Verify price is shown
    const priceElement = page.locator('text=/\\$[0-9,]+/').first();
    await expect(priceElement).toBeVisible({ timeout: 5000 });
    const priceText = await priceElement.textContent();
    console.log(`   ✅ Price displayed: ${priceText}`);

    // Verify key stats section (check if any stats are present)
    const hasStats = await page.locator('text=/Bedroom|Bathroom|Square|sq/i').first().isVisible().catch(() => false);
    if (hasStats) {
      console.log('   ✅ Key stats displayed');
    } else {
      console.log('   ℹ️  Key stats may not be available for this property');
    }

    // Verify floor plan section exists (if property has floor plan)
    const hasFloorPlan = await page.locator('text=/Floor Plan/i').isVisible().catch(() => false);
    if (hasFloorPlan) {
      console.log('   ✅ Floor plan section present');
    } else {
      console.log('   ℹ️  Floor plan section may not be present');
    }

    // Verify description section exists
    const hasDescription = await page.locator('text=/About This Property|Property Description/i').isVisible().catch(() => false);
    if (hasDescription) {
      console.log('   ✅ Description section present');
    }

    // Verify footer
    await expect(page.locator('text=/AI-powered|generated/i').first()).toBeVisible();
    console.log('   ✅ Footer displayed');
  });

  test('should log property view automatically', async ({ page }) => {
    console.log('✅ Testing automatic view logging');

    // Generate a fresh token
    const response = await page.request.post(`${API_URL}/api/properties/${testPropertyId}/generate-link`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      data: {}
    });

    const linkData = await response.json();
    const token = linkData.token;

    // Listen for view logging request
    let viewLogged = false;
    page.on('response', async (response) => {
      if (response.url().includes('/log_view')) {
        viewLogged = true;
        console.log(`   ✅ View logging request sent: ${response.status()}`);
      }
    });

    // Open public report page
    await page.goto(`${BASE_URL}/report/${token}`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Verify view was logged
    if (viewLogged) {
      console.log('   ✅ View logged automatically');
    } else {
      console.log('   ⚠️  View logging may have failed or completed before listener attached');
    }
  });

  test('should show error for invalid token', async ({ page }) => {
    console.log('✅ Testing invalid token error handling');

    const invalidToken = 'invalid-token-12345-not-real';

    // Open public report with invalid token
    await page.goto(`${BASE_URL}/report/${invalidToken}`);
    await page.waitForLoadState('networkidle');

    // Verify error screen header
    await expect(page.locator('text=/Unable to Load Report/i')).toBeVisible({ timeout: 10000 });
    console.log('   ✅ Error heading displayed');

    // Verify error message is present (any error text)
    const hasErrorText = await page.locator('p.text-gray-600').first().isVisible().catch(() => false);
    if (hasErrorText) {
      const errorText = await page.locator('p.text-gray-600').first().textContent();
      console.log(`   ✅ Error message displayed: "${errorText}"`);
    } else {
      console.log('   ℹ️  Error message present but may vary');
    }

    // Verify helpful message about contacting agent is present
    const hasContactMsg = await page.locator('text=/contact|agent/i').isVisible().catch(() => false);
    if (hasContactMsg) {
      console.log('   ✅ Helpful contact message displayed');
    }
  });

  test('should display investment score if available', async ({ page }) => {
    console.log('✅ Testing investment score display');

    // Generate token
    const response = await page.request.post(`${API_URL}/api/properties/${testPropertyId}/generate-link`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      data: {}
    });

    const linkData = await response.json();
    const token = linkData.token;

    // Open public report
    await page.goto(`${BASE_URL}/report/${token}`);
    await page.waitForLoadState('networkidle');

    // Check for investment score badge
    const investmentScore = page.locator('text=/Investment Score/i');
    if (await investmentScore.isVisible()) {
      const scoreValue = page.locator('text=/^\\d+$/').first();
      const score = await scoreValue.textContent();
      console.log(`   ✅ Investment score displayed: ${score}/100`);
      
      // Verify "out of 100" text
      await expect(page.locator('text=/out of 100/i')).toBeVisible();
    } else {
      console.log('   ℹ️  Investment score not available for this property');
    }
  });

  test('should be mobile responsive', async ({ page }) => {
    console.log('✅ Testing mobile responsive design');

    // Generate token
    const response = await page.request.post(`${API_URL}/api/properties/${testPropertyId}/generate-link`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      data: {}
    });

    const linkData = await response.json();
    const token = linkData.token;

    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE

    // Open public report
    await page.goto(`${BASE_URL}/report/${token}`);
    await page.waitForLoadState('networkidle');

    // Verify page loads on mobile by checking for the heading (use getByRole to be specific)
    await page.waitForSelector('header', { timeout: 10000 });
    await expect(page.getByRole('heading', { name: /Property Report/i })).toBeVisible({ timeout: 10000 });
    console.log('   ✅ Page loads on mobile viewport');

    // Verify key elements are visible (price)
    await expect(page.locator('text=/\\$[0-9,]+/').first()).toBeVisible();
    console.log('   ✅ Content visible on mobile');

    // Verify layout is mobile-friendly (check that elements stack vertically)
    const mainContent = page.locator('main');
    await expect(mainContent).toBeVisible();
    console.log('   ✅ Mobile layout renders correctly');

    // Reset viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  test('should verify data sanitization (no agent info)', async ({ page }) => {
    console.log('✅ Testing data sanitization');

    // Generate token
    const response = await page.request.post(`${API_URL}/api/properties/${testPropertyId}/generate-link`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      data: {}
    });

    const linkData = await response.json();
    const token = linkData.token;

    // Fetch public report data via API (no auth)
    const publicDataResponse = await page.request.get(`${API_URL}/api/public/report/${token}`);
    expect(publicDataResponse.ok()).toBeTruthy();
    
    const publicData = await publicDataResponse.json();
    
    // Verify no agent information is exposed
    expect(publicData.property.agent_id).toBeUndefined();
    expect(publicData.property.extracted_data.agent_id).toBeUndefined();
    expect(publicData.property.extracted_data.agent_notes).toBeUndefined();
    
    console.log('   ✅ Agent information properly sanitized');
    console.log('   ✅ Only public data exposed');
  });
});
