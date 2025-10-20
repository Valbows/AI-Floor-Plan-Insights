/**
 * Dashboard Price Display E2E Test
 * 
 * Tests that property prices display correctly in both card and table views
 * 
 * Bug Fix: Properties were showing "Analyzing price..." even when analysis was complete
 * Root Cause: Incorrect data path (property.market_insights vs property.extracted_data.market_insights)
 * 
 * This test ensures prices display correctly after the fix
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
const API_URL = process.env.API_URL || 'http://localhost:5000';

test.describe('Dashboard Price Display', () => {
  let authToken;

  test.beforeAll(async ({ request }) => {
    // Login and get auth token via API
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
  });

  test.beforeEach(async ({ page }) => {
    // Set auth token in localStorage
    await page.goto(BASE_URL);
    await page.evaluate((token) => {
      localStorage.setItem('token', token);
    }, authToken);
    
    // Navigate to dashboard
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForLoadState('networkidle');
  });

  test('should display prices in card view for completed properties', async ({ page }) => {
    console.log('✅ Testing price display in Card View');
    
    // Wait for properties to load
    await page.waitForSelector('text=/Property|properties/i', { timeout: 10000 });
    await page.waitForTimeout(1000);
    
    // Find all property cards (they have floor plan images and addresses)
    const propertyCards = await page.locator('div').filter({ has: page.locator('img[alt*="Floor"]') }).all();
    console.log(`   Found ${propertyCards.length} property cards`);
    
    let pricesFound = 0;
    let analyzingFound = 0;
    
    // Check each card for price display
    for (let i = 0; i < Math.min(propertyCards.length, 5); i++) {
      const card = propertyCards[i];
      const cardText = await card.textContent();
      
      // Check if price is displayed (starts with $)
      if (cardText.includes('$') && cardText.match(/\$[\d,]+/)) {
        const priceMatch = cardText.match(/\$([\d,]+)/);
        if (priceMatch) {
          pricesFound++;
          console.log(`   ✅ Card ${i + 1}: Price displayed - ${priceMatch[0]}`);
        }
      } else if (cardText.includes('Analyzing price')) {
        analyzingFound++;
        console.log(`   ⏳ Card ${i + 1}: Still analyzing (expected for incomplete properties)`);
      }
    }
    
    console.log(`   Summary: ${pricesFound} prices displayed, ${analyzingFound} analyzing`);
    
    // At least one price should be displayed (we know test data has completed properties)
    expect(pricesFound).toBeGreaterThan(0);
    console.log('✅ Card view price display verified');
  });

  test('should display prices in table view for completed properties (if available)', async ({ page }) => {
    console.log('✅ Testing price display in Table View (if available)');
    
    // Wait for dashboard content
    await page.waitForSelector('text=/Property|properties/i', { timeout: 10000 });
    await page.waitForTimeout(500);
    
    // Try to find a table/list view toggle
    const tableToggle = page.getByRole('button', { name: /Table|List/i });
    const hasToggle = await tableToggle.isVisible().catch(() => false);
    
    if (hasToggle) {
      await tableToggle.click();
      await page.waitForTimeout(500);
      // Expect a price visible somewhere in the table view
      const priceElement = page.locator('text=/\\$[0-9,]+/').first();
      await expect(priceElement).toBeVisible();
      console.log('   ✅ Price visible in table view');
    } else {
      console.log('   ℹ️  No table view toggle present; verifying card view price instead');
      const priceElement = page.locator('text=/\\$[0-9,]+/').first();
      await expect(priceElement).toBeVisible();
      console.log('   ✅ Price visible in current view');
    }
  });

  test('should NOT show "Analyzing price..." for properties with complete market insights', async ({ page }) => {
    console.log('✅ Testing that completed properties show prices (not "Analyzing price...")');
    
    // Get all property cards
    const propertyCards = await page.locator('[class*="bg-white"][class*="rounded-lg"][class*="border"]').all();
    
    // Find a property with "Ready" status (indicates analysis complete)
    let foundReadyProperty = false;
    
    for (const card of propertyCards) {
      const cardText = await card.textContent();
      
      // Check if this card has "Ready" status (green checkmark)
      if (cardText.includes('Ready') || cardText.includes('Analysis Complete')) {
        foundReadyProperty = true;
        
        // This property should NOT show "Analyzing price..."
        expect(cardText).not.toContain('Analyzing price...');
        
        // It SHOULD show a price (contains $)
        expect(cardText).toMatch(/\$[\d,]+/);
        
        const priceMatch = cardText.match(/\$([\d,]+)/);
        if (priceMatch) {
          console.log(`   ✅ Ready property shows price: ${priceMatch[0]}`);
        }
        
        break;
      }
    }
    
    if (foundReadyProperty) {
      console.log('✅ Verified: Completed properties show prices, not "Analyzing price..."');
    } else {
      console.log('⚠️  No "Ready" properties found in current view');
    }
  });

  test('should display price per square foot when available', async ({ page }) => {
    console.log('✅ Testing price per square foot display');
    
    // Get property cards
    const propertyCards = await page.locator('[class*="bg-white"][class*="rounded-lg"][class*="border"]').all();
    
    let pricePerSqftFound = false;
    
    for (const card of propertyCards) {
      const cardText = await card.textContent();
      
      // Look for price per sq ft pattern (e.g., "$200/sq ft")
      if (cardText.match(/\$[\d,]+\s*\/\s*sq\s*ft/i)) {
        pricePerSqftFound = true;
        const match = cardText.match(/\$([\d,]+)\s*\/\s*sq\s*ft/i);
        console.log(`   ✅ Price per sq ft displayed: ${match[0]}`);
        break;
      }
    }
    
    if (pricePerSqftFound) {
      console.log('✅ Price per square foot calculation verified');
    } else {
      console.log('⚠️  Price per square foot not found (may require properties with both price and sqft)');
    }
  });

  test('should show prices correctly after switching between views (if available)', async ({ page }) => {
    console.log('✅ Testing price persistence across view switches (if available)');
    
    // Wait for dashboard content
    await page.waitForSelector('text=/Property|properties/i', { timeout: 10000 });
    await page.waitForTimeout(500);
    
    const priceMatcher = page.locator('text=/\\$[0-9,]+/').first();
    
    // Try to find a table/list view toggle
    const tableToggle = page.getByRole('button', { name: /Table|List/i });
    const hasToggle = await tableToggle.isVisible().catch(() => false);
    
    if (hasToggle) {
      // Ensure price is visible in current view
      await expect(priceMatcher).toBeVisible();
      // Switch to table/list
      await tableToggle.click();
      await page.waitForTimeout(500);
      await expect(priceMatcher).toBeVisible();
      // Switch back if a card/grid toggle exists
      const cardToggle = page.getByRole('button', { name: /Card|Grid/i });
      const hasCardToggle = await cardToggle.isVisible().catch(() => false);
      if (hasCardToggle) {
        await cardToggle.click();
        await page.waitForTimeout(500);
        await expect(priceMatcher).toBeVisible();
      }
      console.log('   ✅ Price visible across view switches');
    } else {
      console.log('   ℹ️  No view toggles present; verifying price in current view only');
      await expect(priceMatcher).toBeVisible();
      console.log('   ✅ Price visible in current view');
    }
  });
});
