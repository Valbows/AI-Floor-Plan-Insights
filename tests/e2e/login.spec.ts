import { test, expect } from '@playwright/test'

const EMAIL = process.env.TEST_USER_EMAIL || 'jane.smith@realestate.com'
const PASSWORD = process.env.TEST_USER_PASSWORD || 'Agent2025!'
const LIVE = process.env.E2E_LIVE_BACKEND === '1'

// Utility: wait for a specific network call
async function waitForLoginResponse(page) {
  const resp = await page.waitForResponse(resp => {
    try {
      return resp.url().includes('/auth/login') && resp.status() === 200
    } catch {
      return false
    }
  }, { timeout: 15000 })
  return resp
}

// Utility: wait until token exists in localStorage
async function waitForToken(page) {
  await page.waitForFunction(() => !!localStorage.getItem('token'), undefined, { timeout: 15000 })
}

test.describe('Auth: Login flow', () => {
  test('logs in and stays authenticated', async ({ page, baseURL }) => {
    if (!LIVE) {
      await page.route('**/api/properties', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ properties: [] })
        })
      })
      await page.route('**/auth/login', async route => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              token: 'fake-jwt-token',
              user: { id: 'test-user', email: EMAIL, full_name: 'Jane Smith' }
            })
          })
          return
        }
        await route.fallback()
      })
      await page.route('**/auth/verify', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ user: { id: 'test-user', email: EMAIL, full_name: 'Jane Smith' } })
        })
      })
    }

    // Navigate to login page
    await page.goto(baseURL + '/login')

    // Fill credentials
    await page.getByLabel('Email Address').fill(EMAIL)
    await page.getByLabel('Password').fill(PASSWORD)

    // Submit form and wait for backend response
    const [loginResp] = await Promise.all([
      waitForLoginResponse(page),
      page.getByRole('button', { name: /sign in/i }).click()
    ])

    // Validate backend returned JSON with token
    const bodyText = await loginResp.text()
    let json: any
    try {
      json = JSON.parse(bodyText)
    } catch {
      json = {}
    }
    expect(json.token, 'login response should include token').toBeTruthy()

    // Expect navigation to dashboard
    await page.waitForURL(/\/dashboard(\/?|$)/, { timeout: 15000 })
    // Let requests settle then confirm token exists
    await page.waitForLoadState('networkidle', { timeout: 15000 })
    await waitForToken(page)
    const token = await page.evaluate(() => localStorage.getItem('token'))
    expect(token, 'token should be set in localStorage').toBeTruthy()

    // Ensure we did not bounce back to login
    expect(page.url()).toMatch(/\/dashboard(\/?|$)/)

    // Optional: verify a dashboard element appears
    await expect(page.getByText(/MY\s+PROPERTIES/i)).toBeVisible({ timeout: 15000 })
  })
})
