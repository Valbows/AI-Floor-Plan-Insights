import { test, expect } from '@playwright/test'
import fs from 'fs'
import path from 'path'

// This test verifies the floor plan upload flow navigates to the property page
// and shows the progress overlay. It mocks backend endpoints so no real server is required.

test('Floor plan upload shows progress overlay and navigates to property page', async ({ page }) => {
  // Set token before any app scripts so AuthContext treats session as authenticated
  await page.addInitScript(() => {
    window.localStorage.setItem('token', 'playwright-test-token')
  })
  // Mock auth verify so ProtectedRoute allows access
  await page.route('**/auth/verify', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ user: { id: 'user-1', email: 'agent@example.com' } }),
    })
  })

  // Mock upload endpoint to return a fake property ID
  await page.route('**/api/properties/upload', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ property: { id: 'test-floorplan-123', image_url: 'http://example.com/floor.png' } }),
    })
  })

  // Mock property fetch to keep status "processing" so overlay remains visible
  await page.route('**/api/properties/test-floorplan-123', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        property: {
          id: 'test-floorplan-123',
          status: 'processing',
          extracted_data: {
            address: '123 Test St, Test City, TS 00000',
            bedrooms: 0,
            bathrooms: 0,
            square_footage: 0,
          },
        },
      }),
    })
  })

  // Navigate to New Property page
  await page.goto('/properties/new')

  // Create a tiny 1x1 PNG to upload
  const tmpDir = process.env.TMPDIR || '/tmp'
  const filePath = path.join(tmpDir, 'sample_floor_plan.png')
  const png1x1 = Buffer.from(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQI12NgYGBgAAAABAABJzQnWQAAAABJRU5ErkJggg==',
    'base64'
  )
  fs.writeFileSync(filePath, png1x1)

  // Upload file and fill address
  await page.setInputFiles('input[type="file"]', filePath)
  await page.fill('#address', '123 Main St, Test City, TS 00000')

  // Submit form
  await page.getByRole('button', { name: /Start AI Analysis/i }).click()

  // Verify navigation to property page with overlay
  await expect(page).toHaveURL(/\/properties\/test-floorplan-123\?showProgress=true/)
  await expect(page.getByText('Analyzing Your Property')).toBeVisible()
  await expect(page.getByText('Uploading floor plan')).toBeVisible()
  await expect(page.getByText('Analyzing layout and rooms')).toBeVisible()
})
