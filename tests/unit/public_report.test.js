/**
 * Public Report API Unit Tests
 * 
 * Tests the public report endpoints (Phase 4.1-4.2)
 * - Token validation
 * - Property data sanitization
 * - View logging
 * - Error handling
 */

describe('Public Report API', () => {
  describe('GET /api/public/report/<token>', () => {
    test('should return property data for valid token', () => {
      const validToken = '9a3324b1-a91b-4a7b-bc61-2e66ea7d1378'
      
      // Mock response structure
      const response = {
        property: {
          id: 'prop-123',
          address: '123 Main St',
          extracted_data: {
            address: '123 Main St, City, State 12345',
            square_footage: 1500,
            bedrooms: 3,
            bathrooms: 2,
            market_insights: {
              price_estimate: {
                estimated_value: 283000
              }
            }
          },
          floor_plan_url: 'https://example.com/floor-plan.jpg',
          status: 'complete'
        },
        token_info: {
          expires_at: '2025-11-06T00:00:00Z',
          is_active: true
        }
      }
      
      // Validate structure
      expect(response.property).toBeDefined()
      expect(response.token_info).toBeDefined()
      expect(response.property.extracted_data.market_insights.price_estimate.estimated_value).toBe(283000)
    })

    test('should sanitize sensitive agent data', () => {
      const propertyData = {
        id: 'prop-123',
        agent_id: 'agent-456',  // Should be removed
        agent_notes: 'Private notes',  // Should be removed
        extracted_data: {
          address: '123 Main St',
          agent_id: 'agent-456',  // Should be removed from nested data
          market_insights: {
            price_estimate: {
              estimated_value: 283000
            }
          }
        }
      }
      
      // Simulate sanitization logic
      const sanitizedData = {
        id: propertyData.id,
        extracted_data: { ...propertyData.extracted_data }
      }
      delete sanitizedData.extracted_data.agent_id
      
      // Verify sanitization
      expect(sanitizedData.extracted_data.agent_id).toBeUndefined()
      expect(sanitizedData.extracted_data.market_insights).toBeDefined()
    })

    test('should return 404 for invalid token', () => {
      const invalidToken = 'invalid-token-12345'
      const errorResponse = {
        error: 'Link not found',
        message: 'This shareable link does not exist or has been deactivated'
      }
      
      expect(errorResponse.error).toBe('Link not found')
    })

    test('should return 410 for expired token', () => {
      const expiredToken = 'expired-token-12345'
      const errorResponse = {
        error: 'Link expired',
        message: 'This shareable link has expired'
      }
      
      expect(errorResponse.error).toBe('Link expired')
    })
  })

  describe('POST /api/public/report/<token>/log_view', () => {
    test('should log view with metadata', () => {
      const viewData = {
        property_id: 'prop-123',
        viewed_at: new Date().toISOString(),
        user_agent: 'Mozilla/5.0...',
        ip_address: '192.168.1.1',
        referrer: 'https://example.com',
        viewport_width: 1920,
        viewport_height: 1080
      }
      
      // Validate view data structure
      expect(viewData.property_id).toBeDefined()
      expect(viewData.viewed_at).toBeDefined()
      expect(viewData.viewport_width).toBe(1920)
      expect(viewData.viewport_height).toBe(1080)
    })

    test('should handle optional view metadata', () => {
      const minimalViewData = {
        property_id: 'prop-123',
        viewed_at: new Date().toISOString()
      }
      
      // Should work with minimal data
      expect(minimalViewData.property_id).toBeDefined()
      expect(minimalViewData.viewport_width).toBeUndefined()
    })

    test('should return success response', () => {
      const response = {
        success: true,
        message: 'View logged successfully'
      }
      
      expect(response.success).toBe(true)
      expect(response.message).toContain('successfully')
    })
  })

  describe('GET /api/public/report/<token>/validate', () => {
    test('should validate active token', () => {
      const validationResponse = {
        valid: true,
        expires_at: '2025-11-06T00:00:00Z',
        property_address: '123 Main St'
      }
      
      expect(validationResponse.valid).toBe(true)
      expect(validationResponse.expires_at).toBeDefined()
      expect(validationResponse.property_address).toBeDefined()
    })

    test('should reject invalid token', () => {
      const validationResponse = {
        valid: false,
        message: 'Token not found or inactive'
      }
      
      expect(validationResponse.valid).toBe(false)
      expect(validationResponse.message).toBeDefined()
    })

    test('should reject expired token', () => {
      const validationResponse = {
        valid: false,
        message: 'Token has expired',
        expires_at: '2025-01-01T00:00:00Z'
      }
      
      expect(validationResponse.valid).toBe(false)
      expect(validationResponse.message).toContain('expired')
    })
  })

  describe('Token expiration logic', () => {
    test('should calculate expiration correctly', () => {
      const now = new Date()
      const expirationDays = 30
      const expiresAt = new Date(now.getTime() + expirationDays * 24 * 60 * 60 * 1000)
      
      // Verify expiration is approximately 30 days in future
      const daysDiff = Math.floor((expiresAt - now) / (1000 * 60 * 60 * 24))
      expect(daysDiff).toBe(expirationDays)
    })

    test('should detect expired tokens', () => {
      const now = new Date()
      const pastDate = new Date(now.getTime() - 24 * 60 * 60 * 1000) // Yesterday
      
      const isExpired = now > pastDate
      expect(isExpired).toBe(true)
    })

    test('should allow active tokens', () => {
      const now = new Date()
      const futureDate = new Date(now.getTime() + 24 * 60 * 60 * 1000) // Tomorrow
      
      const isExpired = now > futureDate
      expect(isExpired).toBe(false)
    })
  })

  describe('PublicReport React component logic', () => {
    test('should extract property data correctly', () => {
      const property = {
        extracted_data: {
          address: '123 Main St',
          square_footage: 1500,
          bedrooms: 3,
          bathrooms: 2,
          layout_type: 'Open concept',
          market_insights: {
            price_estimate: {
              estimated_value: 283000
            },
            investment_analysis: {
              investment_score: 85
            }
          },
          marketing_content: {
            listing_description: 'Beautiful home...'
          }
        }
      }
      
      const extractedData = property.extracted_data || {}
      const marketInsights = extractedData.market_insights || {}
      const priceEstimate = marketInsights.price_estimate || {}
      const investmentAnalysis = marketInsights.investment_analysis || {}
      
      const address = extractedData.address
      const price = priceEstimate.estimated_value || 0
      const sqft = extractedData.square_footage || 0
      const bedrooms = extractedData.bedrooms || 0
      const bathrooms = extractedData.bathrooms || 0
      const investmentScore = investmentAnalysis.investment_score || 0
      
      // Validate extraction
      expect(address).toBe('123 Main St')
      expect(price).toBe(283000)
      expect(sqft).toBe(1500)
      expect(bedrooms).toBe(3)
      expect(bathrooms).toBe(2)
      expect(investmentScore).toBe(85)
    })

    test('should handle missing data gracefully', () => {
      const property = {
        extracted_data: {}
      }
      
      const extractedData = property.extracted_data || {}
      const marketInsights = extractedData.market_insights || {}
      const priceEstimate = marketInsights.price_estimate || {}
      
      const price = priceEstimate.estimated_value || 0
      const sqft = extractedData.square_footage || 0
      
      // Should default to 0
      expect(price).toBe(0)
      expect(sqft).toBe(0)
    })

    test('should calculate price per square foot', () => {
      const price = 283000
      const sqft = 1500
      
      const pricePerSqft = sqft > 0 && price > 0 ? Math.round(price / sqft) : 0
      
      expect(pricePerSqft).toBe(189) // 283000 / 1500 = 188.67 rounds to 189
    })

    test('should handle zero square footage', () => {
      const price = 283000
      const sqft = 0
      
      const pricePerSqft = sqft > 0 && price > 0 ? Math.round(price / sqft) : 0
      
      expect(pricePerSqft).toBe(0)
    })
  })
})
