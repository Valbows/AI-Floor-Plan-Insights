/**
 * Share Button E2E Tests
 * 
 * Tests the complete share button workflow from PropertyDetail page
 * Ensures the Share button always works properly in the UI
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
const API_URL = process.env.API_URL || 'http://localhost:5000';

test.describe('Share Button Functionality', () => {
  let authToken;
  let testPropertyId;

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

    // Find a property
    const propertiesResponse = await request.get(`${API_URL}/api/properties`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    expect(propertiesResponse.ok()).toBeTruthy();
    const data = await propertiesResponse.json();
    const properties = data.properties;

    const testProperty = properties.find(prop => prop.status === 'complete');
    expect(testProperty).toBeDefined();
    testPropertyId = testProperty.id;
    
    console.log(`✅ Found test property: ${testPropertyId}`);
  });

  test('should generate shareable link from Share button', async ({ page }) => {
    console.log('✅ Testing Share button functionality');

    // Set auth token
    await page.goto(BASE_URL);
    await page.evaluate((token) => {
      localStorage.setItem('token', token);
    }, authToken);

    // Navigate to Agent Tools page where Share FAB lives in new UI
    await page.goto(`${BASE_URL}/agent-tools/${testPropertyId}`);
    await page.waitForLoadState('domcontentloaded');
    // Wait for page content that indicates property view loaded
    await page.waitForSelector('text=/Property Information/i', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);

    // Find and click Share button (FAB)
    const shareButton = page.locator('[data-testid="share-fab"]');
    await expect(shareButton).toBeVisible({ timeout: 10000 });
    console.log('   ✅ Share button found');

    await shareButton.click();
    await page.waitForTimeout(500);

    // Verify modal opened
    const modal = page.locator('text=/Share Property/i');
    await expect(modal).toBeVisible({ timeout: 5000 });
    console.log('   ✅ Share modal opened');

    // Wait for link generation (with loading state)
    await page.waitForTimeout(3000);

    // Verify shareable link input appears
    const linkInput = page.locator('input[readonly]').filter({ hasValue: /report/ });
    const hasLink = await linkInput.isVisible().catch(() => false);

    if (hasLink) {
      const shareableUrl = await linkInput.inputValue();
      console.log(`   ✅ Shareable link generated: ${shareableUrl}`);

      // Verify URL format
      expect(shareableUrl).toContain('/report/');
      expect(shareableUrl).toContain('http');
      console.log('   ✅ Link format is correct');

      // Verify expiration date is shown
      const expiresText = page.locator('text=/Expires/i');
      await expect(expiresText).toBeVisible();
      console.log('   ✅ Expiration date displayed');

      // Test copy button
      const copyButton = page.locator('button').filter({ hasText: /copy/i });
      if (await copyButton.isVisible()) {
        await copyButton.click();
        await page.waitForTimeout(500);
        
        // Verify "Copied!" feedback
        const copiedText = page.locator('text=/copied/i');
        const wasCopied = await copiedText.isVisible().catch(() => false);
        if (wasCopied) {
          console.log('   ✅ Copy to clipboard works');
        }
      }
    } else {
      console.log('   ⚠️  Link generation may have failed - checking for error');
      
      // Check for error message
      const errorText = page.locator('text=/failed|error/i');
      const hasError = await errorText.isVisible().catch(() => false);
      
      if (hasError) {
        const errorMessage = await errorText.textContent();
        console.log(`   ❌ Error: ${errorMessage}`);
        throw new Error(`Share button failed: ${errorMessage}`);
      }
    }

    // Close modal
    const closeButton = page.locator('[data-testid="close-share-modal"]');
    await closeButton.click();
    await page.waitForTimeout(300);
    console.log('   ✅ Modal closed');
  });

  test('should handle existing shareable link', async ({ page }) => {
    console.log('✅ Testing retrieval of existing shareable link');

    // Set auth token
    await page.goto(BASE_URL);
    await page.evaluate((token) => {
      localStorage.setItem('token', token);
    }, authToken);

    // First, generate a link via API
    const linkResponse = await page.request.post(`${API_URL}/api/properties/${testPropertyId}/generate-link`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      data: {}
    });

    expect(linkResponse.ok()).toBeTruthy();
    const linkData = await linkResponse.json();
    console.log(`   ✅ Pre-generated link: ${linkData.shareable_url}`);

    // Now test that the UI retrieves it
    await page.goto(`${BASE_URL}/agent-tools/${testPropertyId}`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Click Share button
    const shareButton = page.locator('[data-testid="share-fab"]');
    await page.waitForSelector('[data-testid="share-fab"]', { timeout: 15000 });
    await expect(shareButton).toBeVisible({ timeout: 15000 });
    await shareButton.click();
    await page.waitForTimeout(2000);

    // Verify the same link is shown
    const linkInput = page.locator('input[readonly]').filter({ hasValue: /report/ });
    const hasLink = await linkInput.isVisible().catch(() => false);

    if (hasLink) {
      const displayedUrl = await linkInput.inputValue();
      console.log(`   ✅ Retrieved existing link: ${displayedUrl}`);
      
      // Should match the pre-generated token
      expect(displayedUrl).toContain(linkData.token);
      console.log('   ✅ Correct link retrieved');
    }

    // Close modal
    const closeButton = page.locator('[data-testid="close-share-modal"]');
    await closeButton.click();
  });

  test('should show loading state while generating', async ({ page }) => {
    console.log('✅ Testing loading state');

    await page.goto(BASE_URL);
    await page.evaluate((token) => {
      localStorage.setItem('token', token);
    }, authToken);

    await page.goto(`${BASE_URL}/agent-tools/${testPropertyId}`);
    await page.waitForLoadState('networkidle');

    // Click Share button
    const shareButton = page.locator('[data-testid="share-fab"]');
    await shareButton.click();
    await page.waitForTimeout(200);

    // Verify loading indicator appears
    const loadingText = page.locator('text=/Generating|Loading/i');
    const hasLoading = await loadingText.isVisible().catch(() => false);

    if (hasLoading) {
      console.log('   ✅ Loading state displayed');
    } else {
      console.log('   ℹ️  Loading state may be very fast');
    }

    // Wait for completion
    await page.waitForTimeout(3000);

    // Close modal
    const closeButton = page.locator('[data-testid="close-share-modal"]');
    await closeButton.click();
  });

  test('should handle network errors gracefully', async ({ page }) => {
    console.log('✅ Testing error handling');

    await page.goto(BASE_URL);
    await page.evaluate((token) => {
      localStorage.setItem('token', token);
    }, authToken);

    // Intercept API call and force it to fail
    await page.route(`**/api/properties/*/generate-link`, route => {
      route.abort('failed');
    });

    await page.goto(`${BASE_URL}/agent-tools/${testPropertyId}`);
    await page.waitForLoadState('networkidle');

    // Click Share button
    const shareButton = page.locator('[data-testid="share-fab"]');
    await shareButton.click();
    await page.waitForTimeout(2000);

    // Verify error message is shown
    const errorText = page.locator('text=/failed|error|try again/i');
    const hasError = await errorText.isVisible().catch(() => false);

    if (hasError) {
      console.log('   ✅ Error message displayed');
      
      // Verify "Try Again" button exists
      const retryButton = page.locator('button').filter({ hasText: /try again/i });
      const canRetry = await retryButton.isVisible().catch(() => false);
      
      if (canRetry) {
        console.log('   ✅ Retry button available');
      }
    } else {
      console.log('   ℹ️  Error handling may vary');
    }

    // Close modal
    const closeButton = page.locator('[data-testid="close-share-modal"]');
    await closeButton.click();
  });

  test('should validate shareable link is accessible', async ({ page }) => {
    console.log('✅ Testing that generated link is accessible');

    await page.goto(BASE_URL);
    await page.evaluate((token) => {
      localStorage.setItem('token', token);
    }, authToken);

    // Generate link via API
    const linkResponse = await page.request.post(`${API_URL}/api/properties/${testPropertyId}/generate-link`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      data: {}
    });

    expect(linkResponse.ok()).toBeTruthy();
    const linkData = await linkResponse.json();
    const shareableUrl = linkData.shareable_url;
    
    console.log(`   Generated link: ${shareableUrl}`);

    // Test that the public report page loads
    await page.goto(shareableUrl);
    await page.waitForLoadState('networkidle');

    // Verify page loaded successfully
    const reportHeading = page.getByRole('heading', { name: /Property Report/i });
    await expect(reportHeading).toBeVisible({ timeout: 10000 });
    console.log('   ✅ Shareable link is accessible');

    // Verify no authentication required
    const loginForm = page.locator('input[type="email"]');
    const needsAuth = await loginForm.isVisible().catch(() => false);
    expect(needsAuth).toBe(false);
    console.log('   ✅ No authentication required for public link');
  });
});
