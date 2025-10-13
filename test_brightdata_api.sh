#!/bin/bash
# Test Bright Data Scraping Browser connectivity

echo "=========================================="
echo "Bright Data Scraping Browser Test"
echo "=========================================="
echo ""

BRIGHTDATA_API_KEY="de3475621a753a33c5b8da6a2da5db338841d8684527f1ac30776b038f7cd2c1"

echo "Note: Bright Data Scraping Browser requires a Browser API Zone to be created"
echo "in your dashboard at: https://brightdata.com/cp/zones"
echo ""
echo "The scraping browser uses WebSocket connections (wss://brd.superproxy.io:9222)"
echo "and cannot be easily tested with curl."
echo ""
echo "To test Bright Data:"
echo "1. Go to https://brightdata.com/cp/zones"
echo "2. Click 'Add Zone' -> 'Browser API'"
echo "3. Name it (e.g., 'ai-floor-plan-scraper')"
echo "4. Get your zone credentials"
echo ""
echo "Required format for connection:"
echo "  wss://USERNAME:PASSWORD@brd.superproxy.io:9222"
echo ""
echo "Where:"
echo "  - USERNAME: Your zone username (format: brd-customer-XXXXX-zone-XXXXX)"
echo "  - PASSWORD: Your API key (${BRIGHTDATA_API_KEY:0:20}...)"
echo ""
echo "=========================================="
echo "Checking Bright Data Account Status"
echo "=========================================="
echo ""

# Try to check account via API (if available)
echo "Attempting to verify API key format..."
if [ ${#BRIGHTDATA_API_KEY} -eq 64 ]; then
    echo "✅ API key format looks valid (64 characters)"
else
    echo "⚠️  API key length: ${#BRIGHTDATA_API_KEY} characters (expected 64)"
fi

echo ""
echo "API Key (first 20 chars): ${BRIGHTDATA_API_KEY:0:20}..."
echo "API Key (last 10 chars): ...${BRIGHTDATA_API_KEY: -10}"
echo ""

echo "=========================================="
echo "Next Steps for Bright Data Setup:"
echo "=========================================="
echo ""
echo "1. Visit: https://brightdata.com/cp/zones"
echo "2. Create a Browser API zone if you haven't already"
echo "3. Copy the zone credentials"
echo "4. Update the BrightDataClient username if needed"
echo "5. Run the Python test: docker-compose exec backend python tests/manual/test_brightdata_scrapers.py"
echo ""
echo "The Python test with Playwright will properly test the scraping browser."
echo ""
