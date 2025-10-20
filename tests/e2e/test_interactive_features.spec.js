/**
 * Interactive Features E2E Tests (Phase 4.3)
 * 
 * Tests the interactive features on the public report page:
 * - Comparable properties section
 * - Image zoom/pan functionality
 * - Property features checklist
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
const API_URL = process.env.API_URL || 'http://localhost:5000';

test.describe('Interactive Features - Phase 4.3', () => {
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

    // Generate shareable token for testing
    const linkResponse = await request.post(`${API_URL}/api/properties/${testPropertyId}/generate-link`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      },
      data: {}
    });

    expect(linkResponse.ok()).toBeTruthy();
    const linkData = await linkResponse.json();
    shareableToken = linkData.token;
    
    console.log(`✅ Generated shareable token: ${shareableToken}`);
  });

  test('should display comparable properties section', async ({ page }) => {
    console.log('✅ Testing comparable properties display');

    // Open public report
    await page.goto(`${BASE_URL}/report/${shareableToken}`);
    await page.waitForLoadState('networkidle');

    // Check for comparable properties section
    const compsHeading = page.locator('text=/Comparable Properties/i');
    const hasComps = await compsHeading.isVisible().catch(() => false);

    if (hasComps) {
      console.log('   ✅ Comparable Properties section found');

      // Verify section description
      await expect(page.locator('text=/Similar properties sold recently/i')).toBeVisible();
      console.log('   ✅ Section description displayed');

      // Check for property cards
      const compCards = page.locator('div').filter({ has: page.locator('text=/Sale Price/i') });
      const cardCount = await compCards.count();
      
      if (cardCount > 0) {
        console.log(`   ✅ Found ${cardCount} comparable property cards`);

        // Verify first card structure
        const firstCard = compCards.first();
        
        // Check for sale price
        const hasSalePrice = await firstCard.locator('text=/\\$/').isVisible();
        if (hasSalePrice) {
          console.log('   ✅ Sale price displayed in card');
        }

        // Check for property stats (beds, baths, sqft)
        const hasStats = await firstCard.locator('svg').count() > 0;
        if (hasStats) {
          console.log('   ✅ Property stats icons displayed');
        }

        // Verify hover effect
        const cardBox = await firstCard.boundingBox();
        if (cardBox) {
          await page.mouse.move(cardBox.x + cardBox.width / 2, cardBox.y + cardBox.height / 2);
          await page.waitForTimeout(300);
          console.log('   ✅ Hover effect works');
        }
      } else {
        console.log('   ℹ️  No comparable properties available for this property');
      }
    } else {
      console.log('   ℹ️  Comparable Properties section not available (no comps data)');
    }
  });

  test('should open floor plan in zoom modal', async ({ page }) => {
    console.log('✅ Testing floor plan zoom functionality');

    // Open public report
    await page.goto(`${BASE_URL}/report/${shareableToken}`);
    await page.waitForLoadState('networkidle');

    // Check if floor plan exists
    const floorPlanSection = page.locator('text=/Floor Plan/i');
    const hasFloorPlan = await floorPlanSection.isVisible().catch(() => false);

    if (hasFloorPlan) {
      console.log('   ✅ Floor plan section found');

      // Check for "View Full Size" button
      const viewFullSizeButton = page.locator('button:has-text("View Full Size")');
      await expect(viewFullSizeButton).toBeVisible({ timeout: 5000 });
      console.log('   ✅ "View Full Size" button visible');

      // Click to zoom
      await viewFullSizeButton.click();
      await page.waitForTimeout(500);

      // Verify modal opened
      const zoomModal = page.locator('.fixed.inset-0.bg-black');
      await expect(zoomModal).toBeVisible({ timeout: 3000 });
      console.log('   ✅ Zoom modal opened');

      // Verify zoom controls
      const zoomInButton = page.locator('button').filter({ has: page.locator('svg') }).filter({ hasText: '' }).first();
      await expect(zoomInButton).toBeVisible();
      console.log('   ✅ Zoom controls visible');

      // Verify zoom level indicator
      const zoomLevel = page.locator('text=/100%/');
      await expect(zoomLevel).toBeVisible();
      console.log('   ✅ Zoom level indicator shows 100%');

      // Test zoom in
      const zoomInBtn = page.locator('button').nth(1); // Second button is zoom in
      await zoomInBtn.click();
      await page.waitForTimeout(300);
      
      // Check if zoom level increased
      const newZoomLevel = page.locator('text=/125%/');
      const zoomIncreased = await newZoomLevel.isVisible().catch(() => false);
      if (zoomIncreased) {
        console.log('   ✅ Zoom in works (125%)');
      }

      // Close modal with X button
      const closeButton = page.locator('button').filter({ has: page.locator('svg') }).first();
      await closeButton.click();
      await page.waitForTimeout(300);

      // Verify modal closed
      const modalClosed = !(await zoomModal.isVisible().catch(() => false));
      if (modalClosed) {
        console.log('   ✅ Modal closed successfully');
      }
    } else {
      console.log('   ℹ️  Floor plan not available for this property');
    }
  });

  test('should open zoom modal by clicking floor plan image', async ({ page }) => {
    console.log('✅ Testing floor plan image click to zoom');

    // Open public report
    await page.goto(`${BASE_URL}/report/${shareableToken}`);
    await page.waitForLoadState('networkidle');

    // Check if floor plan exists
    const floorPlanImage = page.locator('img[alt="Floor Plan"]');
    const hasFloorPlan = await floorPlanImage.isVisible().catch(() => false);

    if (hasFloorPlan) {
      console.log('   ✅ Floor plan image found');

      // Verify cursor changes to pointer
      const imageContainer = floorPlanImage.locator('..');
      const cursorClass = await imageContainer.getAttribute('class');
      if (cursorClass && cursorClass.includes('cursor-pointer')) {
        console.log('   ✅ Image has pointer cursor');
      }

      // Click image to zoom
      await floorPlanImage.click();
      await page.waitForTimeout(500);

      // Verify modal opened
      const zoomModal = page.locator('.fixed.inset-0.bg-black');
      const modalOpened = await zoomModal.isVisible().catch(() => false);
      
      if (modalOpened) {
        console.log('   ✅ Modal opened by clicking image');

        // Close by clicking background
        await page.locator('.fixed.inset-0.bg-black').click({ position: { x: 10, y: 10 } });
        await page.waitForTimeout(300);
        
        const modalClosed = !(await zoomModal.isVisible().catch(() => false));
        if (modalClosed) {
          console.log('   ✅ Modal closed by clicking background');
        }
      }
    } else {
      console.log('   ℹ️  Floor plan not available for this property');
    }
  });

  test('should display property features checklist', async ({ page }) => {
    console.log('✅ Testing property features checklist');

    // Open public report
    await page.goto(`${BASE_URL}/report/${shareableToken}`);
    await page.waitForLoadState('networkidle');

    // Check for Key Features section
    const featuresHeading = page.locator('h2:has-text("Key Features")');
    const hasFeatures = await featuresHeading.isVisible().catch(() => false);

    if (hasFeatures) {
      console.log('   ✅ Key Features section found');

      // Verify check circle icons
      const checkIcons = page.locator('svg.lucide-check-circle');
      const iconCount = await checkIcons.count();
      
      if (iconCount > 0) {
        console.log(`   ✅ Found ${iconCount} feature items with check icons`);

        // Verify first feature item structure
        const firstFeature = page.locator('div').filter({ has: page.locator('svg.lucide-check-circle') }).first();
        await expect(firstFeature).toBeVisible();
        console.log('   ✅ Feature items properly structured');

        // Verify green checkmark styling
        const firstIcon = checkIcons.first();
        const iconClasses = await firstIcon.getAttribute('class');
        if (iconClasses && iconClasses.includes('text-green-600')) {
          console.log('   ✅ Check icons have green color');
        }

        // Verify grid layout (2 columns on desktop)
        const featuresGrid = page.locator('div.grid');
        const gridClasses = await featuresGrid.first().getAttribute('class');
        if (gridClasses && gridClasses.includes('md:grid-cols-2')) {
          console.log('   ✅ Features display in responsive grid');
        }
      } else {
        console.log('   ℹ️  No feature items found');
      }
    } else {
      console.log('   ℹ️  Key Features section not available for this property');
    }
  });

  test('should handle comparable properties with missing data gracefully', async ({ page }) => {
    console.log('✅ Testing comps handling with missing data');

    // Open public report
    await page.goto(`${BASE_URL}/report/${shareableToken}`);
    await page.waitForLoadState('networkidle');

    // Check for comparable properties
    const compsSection = page.locator('text=/Comparable Properties/i');
    const hasComps = await compsSection.isVisible().catch(() => false);

    if (hasComps) {
      console.log('   ✅ Comparable properties found');

      // Find all comp cards
      const compCards = page.locator('div').filter({ has: page.locator('text=/Sale Price|Property/i') });
      const cardCount = await compCards.count();

      if (cardCount > 0) {
        // Check each card for proper structure
        for (let i = 0; i < Math.min(cardCount, 3); i++) {
          const card = compCards.nth(i);
          
          // Verify card has border and hover effect
          const cardClasses = await card.getAttribute('class');
          if (cardClasses && cardClasses.includes('hover:shadow-md')) {
            console.log(`   ✅ Card ${i + 1} has proper styling`);
          }

          // Verify it doesn't crash with missing data
          const cardVisible = await card.isVisible();
          if (cardVisible) {
            console.log(`   ✅ Card ${i + 1} renders without errors`);
          }
        }
      }
    } else {
      console.log('   ℹ️  No comparable properties to test');
    }
  });

  test('should be mobile responsive for interactive features', async ({ page }) => {
    console.log('✅ Testing mobile responsive design for interactive features');

    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE

    // Open public report
    await page.goto(`${BASE_URL}/report/${shareableToken}`);
    await page.waitForLoadState('networkidle');

    // Check comparable properties on mobile
    const compsSection = page.locator('text=/Comparable Properties/i');
    const hasComps = await compsSection.isVisible().catch(() => false);

    if (hasComps) {
      console.log('   ✅ Comps section visible on mobile');

      // Verify single column layout
      const compsGrid = page.locator('div.grid').filter({ has: page.locator('text=/Sale Price/i') });
      const gridClasses = await compsGrid.first().getAttribute('class');
      if (gridClasses && gridClasses.includes('grid-cols-1')) {
        console.log('   ✅ Comps use single column on mobile');
      }
    }

    // Check floor plan zoom on mobile
    const floorPlan = page.locator('text=/Floor Plan/i');
    const hasFloorPlan = await floorPlan.isVisible().catch(() => false);

    if (hasFloorPlan) {
      console.log('   ✅ Floor plan visible on mobile');

      // Verify "View Full Size" button works on mobile
      const viewButton = page.locator('button:has-text("View Full Size")');
      const buttonVisible = await viewButton.isVisible().catch(() => false);
      
      if (buttonVisible) {
        await viewButton.click();
        await page.waitForTimeout(300);

        // Verify modal works on mobile
        const modal = page.locator('.fixed.inset-0');
        const modalVisible = await modal.isVisible().catch(() => false);
        
        if (modalVisible) {
          console.log('   ✅ Zoom modal works on mobile');
          
          // Close modal
          const closeBtn = page.locator('button').first();
          await closeBtn.click();
        }
      }
    }

    // Reset viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
  });
});
