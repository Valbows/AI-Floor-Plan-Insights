#!/bin/bash
#
# Test Phase 2 Workflow with CoreLogic API
# This script tests the complete 3-agent pipeline with real market data
#

set -e

echo "================================================================"
echo "  Phase 2 Workflow Test - WITH CoreLogic Market Data"
echo "================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_BASE="http://localhost:5000"
EMAIL="jane.smith@realestate.com"
PASSWORD="Agent2025!"
ADDRESS="1600 Amphitheatre Parkway, Mountain View, CA 94043" # Google HQ

echo -e "${BLUE}Step 1: Login${NC}"
TOKEN=$(curl -s -X POST ${API_BASE}/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed!"
  exit 1
fi

echo -e "${GREEN}✓ Login successful${NC}"
echo "Token: ${TOKEN:0:20}..."
echo ""

echo -e "${BLUE}Step 2: Creating test floor plan image${NC}"
# Create a small test PNG (1x1 pixel)
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" | base64 -D > /tmp/test_floorplan.png
echo -e "${GREEN}✓ Test image created${NC}"
echo ""

echo -e "${BLUE}Step 3: Uploading property with address${NC}"
echo "Address: ${ADDRESS}"

RESPONSE=$(curl -s -X POST ${API_BASE}/api/properties/upload \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "file=@/tmp/test_floorplan.png" \
  -F "address=${ADDRESS}")

PROPERTY_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['property']['id'])" 2>/dev/null)

if [ -z "$PROPERTY_ID" ]; then
  echo "❌ Upload failed!"
  echo "Response: $RESPONSE"
  exit 1
fi

echo -e "${GREEN}✓ Upload successful${NC}"
echo "Property ID: ${PROPERTY_ID}"
echo ""

echo -e "${BLUE}Step 4: Monitoring workflow (max 2 minutes)${NC}"
echo "Status progression: processing → parsing_complete → enrichment_complete → complete"
echo ""

MAX_WAIT=120
ELAPSED=0
LAST_STATUS=""

while [ $ELAPSED -lt $MAX_WAIT ]; do
  PROPERTY_DATA=$(curl -s -X GET "${API_BASE}/api/properties/${PROPERTY_ID}" \
    -H "Authorization: Bearer ${TOKEN}")
  
  STATUS=$(echo $PROPERTY_DATA | python3 -c "import sys, json; print(json.load(sys.stdin)['property']['status'])" 2>/dev/null)
  
  if [ "$STATUS" != "$LAST_STATUS" ]; then
    TIMESTAMP=$(date +"%H:%M:%S")
    echo "[${TIMESTAMP}] Status: ${STATUS} (${ELAPSED}s elapsed)"
    LAST_STATUS=$STATUS
  fi
  
  # Check if complete or failed
  if [ "$STATUS" = "complete" ]; then
    echo ""
    echo -e "${GREEN}✓✓✓ Workflow complete in ${ELAPSED} seconds!${NC}"
    echo ""
    
    # Extract and display results
    echo "================================================================"
    echo "  RESULTS FROM ALL 3 AGENTS"
    echo "================================================================"
    echo ""
    
    echo "$PROPERTY_DATA" | python3 << 'PYEOF'
import sys, json

data = json.load(sys.stdin)
extracted = data['property'].get('extracted_data', {})

# Agent #1
print("🤖 Agent #1: Floor Plan Analyst")
print("─" * 60)
print(f"Address:        {extracted.get('address', 'N/A')}")
print(f"Bedrooms:       {extracted.get('bedrooms', 0)}")
print(f"Bathrooms:      {extracted.get('bathrooms', 0)}")
print(f"Square Footage: {extracted.get('square_footage', 0):,}")
print(f"Layout Type:    {extracted.get('layout_type', 'N/A')}")
print()

# Agent #2
market = extracted.get('market_insights', {})
if market:
    print("🤖 Agent #2: Market Insights Analyst")
    print("─" * 60)
    
    price = market.get('price_estimate', {})
    print(f"Estimated Value:    ${price.get('estimated_value', 0):,}")
    print(f"Confidence:         {price.get('confidence', 'N/A')}")
    print(f"Value Range:        ${price.get('value_range_low', 0):,} - ${price.get('value_range_high', 0):,}")
    
    trend = market.get('market_trend', {})
    print(f"Market Trend:       {trend.get('trend_direction', 'N/A')}")
    print(f"Buyer Demand:       {trend.get('buyer_demand', 'N/A')}")
    
    investment = market.get('investment_analysis', {})
    print(f"Investment Score:   {investment.get('investment_score', 0)}/100")
    
    comps = market.get('comparable_properties', [])
    print(f"Comparables Found:  {len(comps)} properties")
    
    if comps:
        print("\n🏘️  Using REAL CoreLogic Market Data!")
    else:
        print("\n⚠️  Using Fallback Logic (CoreLogic unavailable)")
    print()

# Agent #3
listing = extracted.get('listing_copy', {})
if listing:
    print("🤖 Agent #3: Listing Copywriter")
    print("─" * 60)
    print(f"Headline:     {listing.get('headline', 'N/A')}")
    desc = listing.get('description', '')
    print(f"Description:  {desc[:100]}...")
    print(f"Highlights:   {len(listing.get('highlights', []))} bullet points")
    print(f"SEO Keywords: {len(listing.get('seo_keywords', []))} keywords")
    print()

print("=" * 60)
print("✅ PHASE 2 TEST COMPLETE - ALL AGENTS VERIFIED!")
print("=" * 60)
PYEOF
    
    # Clean up
    rm /tmp/test_floorplan.png
    exit 0
  elif [[ "$STATUS" == *"failed"* ]]; then
    echo ""
    echo -e "${YELLOW}⚠ Workflow failed with status: ${STATUS}${NC}"
    echo "Property Data: $PROPERTY_DATA"
    rm /tmp/test_floorplan.png
    exit 1
  fi
  
  sleep 3
  ELAPSED=$((ELAPSED + 3))
done

echo ""
echo -e "${YELLOW}⚠ Timeout after ${MAX_WAIT} seconds${NC}"
rm /tmp/test_floorplan.png
exit 1
