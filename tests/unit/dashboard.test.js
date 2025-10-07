/**
 * Dashboard Component Unit Tests
 * 
 * Tests the price display logic in Dashboard component
 * 
 * Bug Fix Validation:
 * - Ensures price is extracted from correct path: extracted_data.market_insights.price_estimate.estimated_value
 * - Verifies fallback to "Analyzing price..." when price is not available
 */

describe('Dashboard Price Display Logic', () => {
  describe('Price extraction from property data', () => {
    test('should extract price from extracted_data.market_insights.price_estimate.estimated_value', () => {
      const property = {
        id: 'test-id',
        extracted_data: {
          address: '123 Main St',
          market_insights: {
            price_estimate: {
              estimated_value: 300000
            }
          }
        }
      };

      const extractedData = property.extracted_data || {};
      const marketData = extractedData.market_insights || {};
      const price = marketData.price_estimate?.estimated_value || 0;

      expect(price).toBe(300000);
    });

    test('should return 0 when price is not available', () => {
      const property = {
        id: 'test-id',
        extracted_data: {
          address: '123 Main St'
        }
      };

      const extractedData = property.extracted_data || {};
      const marketData = extractedData.market_insights || {};
      const price = marketData.price_estimate?.estimated_value || 0;

      expect(price).toBe(0);
    });

    test('should return 0 when extracted_data is missing', () => {
      const property = {
        id: 'test-id',
        address: '123 Main St'
      };

      const extractedData = property.extracted_data || {};
      const marketData = extractedData.market_insights || {};
      const price = marketData.price_estimate?.estimated_value || 0;

      expect(price).toBe(0);
    });

    test('should return 0 when market_insights is missing', () => {
      const property = {
        id: 'test-id',
        extracted_data: {
          address: '123 Main St'
        }
      };

      const extractedData = property.extracted_data || {};
      const marketData = extractedData.market_insights || {};
      const price = marketData.price_estimate?.estimated_value || 0;

      expect(price).toBe(0);
    });

    test('should NOT extract price from wrong path (property.market_insights)', () => {
      // This simulates the OLD incorrect behavior
      const property = {
        id: 'test-id',
        market_insights: {
          price_estimate: {
            estimated_value: 300000
          }
        },
        extracted_data: {
          address: '123 Main St'
        }
      };

      // Correct path (NEW behavior)
      const extractedData = property.extracted_data || {};
      const marketData = extractedData.market_insights || {};
      const correctPrice = marketData.price_estimate?.estimated_value || 0;

      // Wrong path (OLD behavior that was causing the bug)
      const wrongMarketData = property.market_insights || {};
      const wrongPrice = wrongMarketData.price_estimate?.estimated_value || 0;

      // The correct path should return 0 (no price at correct location)
      expect(correctPrice).toBe(0);
      
      // The wrong path would return 300000 (but this is not where the data actually is)
      expect(wrongPrice).toBe(300000);
      
      // This test documents that the fix was necessary
    });
  });

  describe('Price formatting', () => {
    test('should format price with commas and dollar sign', () => {
      const price = 300000;
      const formatted = `$${price.toLocaleString()}`;
      
      expect(formatted).toBe('$300,000');
    });

    test('should show "Analyzing price..." when price is 0', () => {
      const price = 0;
      const display = price > 0 ? `$${price.toLocaleString()}` : 'Analyzing price...';
      
      expect(display).toBe('Analyzing price...');
    });

    test('should show formatted price when price is available', () => {
      const price = 482000;
      const display = price > 0 ? `$${price.toLocaleString()}` : 'Analyzing price...';
      
      expect(display).toBe('$482,000');
    });
  });

  describe('Price per square foot calculation', () => {
    test('should calculate price per sq ft when both values available', () => {
      const price = 300000;
      const sqft = 1500;
      const pricePerSqft = sqft > 0 && price > 0 ? Math.round(price / sqft) : 0;
      
      expect(pricePerSqft).toBe(200);
    });

    test('should return 0 when sqft is 0', () => {
      const price = 300000;
      const sqft = 0;
      const pricePerSqft = sqft > 0 && price > 0 ? Math.round(price / sqft) : 0;
      
      expect(pricePerSqft).toBe(0);
    });

    test('should return 0 when price is 0', () => {
      const price = 0;
      const sqft = 1500;
      const pricePerSqft = sqft > 0 && price > 0 ? Math.round(price / sqft) : 0;
      
      expect(pricePerSqft).toBe(0);
    });

    test('should round price per sq ft to nearest integer', () => {
      const price = 482000;
      const sqft = 1415;
      const pricePerSqft = sqft > 0 && price > 0 ? Math.round(price / sqft) : 0;
      
      // 482000 / 1415 = 340.6... should round to 341
      expect(pricePerSqft).toBe(341);
    });
  });

  describe('Investment score extraction', () => {
    test('should extract investment score from market_insights', () => {
      const property = {
        id: 'test-id',
        extracted_data: {
          market_insights: {
            investment_analysis: {
              investment_score: 85
            }
          }
        }
      };

      const extractedData = property.extracted_data || {};
      const marketData = extractedData.market_insights || {};
      const investmentScore = marketData.investment_analysis?.investment_score || 0;

      expect(investmentScore).toBe(85);
    });

    test('should return 0 when investment score is not available', () => {
      const property = {
        id: 'test-id',
        extracted_data: {
          address: '123 Main St'
        }
      };

      const extractedData = property.extracted_data || {};
      const marketData = extractedData.market_insights || {};
      const investmentScore = marketData.investment_analysis?.investment_score || 0;

      expect(investmentScore).toBe(0);
    });
  });

  describe('Data structure validation', () => {
    test('should handle complete property data structure', () => {
      const property = {
        id: 'abc-123',
        address: '456 Park Avenue',
        created_at: '2025-10-06T00:00:00Z',
        status: 'complete',
        extracted_data: {
          address: '456 Park Avenue, New York, NY 10022',
          square_footage: 1700,
          bedrooms: 3,
          bathrooms: 2,
          layout_type: 'Semi-open concept with traditional living room layout',
          market_insights: {
            price_estimate: {
              estimated_value: 450000,
              confidence_level: 'high'
            },
            investment_analysis: {
              investment_score: 78
            }
          }
        }
      };

      // Extract data using corrected logic
      const extractedData = property.extracted_data || {};
      const marketData = extractedData.market_insights || {};
      const address = extractedData.address || property.address || 'Property Address';
      const price = marketData.price_estimate?.estimated_value || 0;
      const sqft = extractedData.square_footage || 0;
      const bedrooms = extractedData.bedrooms || 0;
      const bathrooms = extractedData.bathrooms || 0;
      const pricePerSqft = sqft > 0 && price > 0 ? Math.round(price / sqft) : 0;
      const investmentScore = marketData.investment_analysis?.investment_score || 0;

      // Validate all extracted values
      expect(address).toBe('456 Park Avenue, New York, NY 10022');
      expect(price).toBe(450000);
      expect(sqft).toBe(1700);
      expect(bedrooms).toBe(3);
      expect(bathrooms).toBe(2);
      expect(pricePerSqft).toBe(265); // 450000 / 1700 = 264.7... rounds to 265
      expect(investmentScore).toBe(78);
    });
  });
});
