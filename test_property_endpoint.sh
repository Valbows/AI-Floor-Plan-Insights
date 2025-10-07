#!/bin/bash
# Test different property endpoint patterns

source .env

# Get token
TOKEN_RESPONSE=$(curl -s -X POST "https://api-prod.corelogic.com/oauth/token?grant_type=client_credentials" \
  -u "$CORELOGIC_CONSUMER_KEY:$CORELOGIC_CONSUMER_SECRET" \
  -H "Content-Length: 0")
  
TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

echo "Token: ${TOKEN:0:30}..."
echo ""

# Test 1: Try property ID format from docs (06037:1081685)
echo "Test 1: GET /property/06037:1081685"
curl -s "https://api-prod.corelogic.com/property/06037:1081685" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | head -50
echo ""
echo "---"

# Test 2: Try with known LA address
echo ""
echo "Test 2: Try property search with address params"
curl -s "https://api-prod.corelogic.com/property?streetAddress=919%20MALCOLM%20AVE&city=LOS%20ANGELES&state=CA&zipCode=90024" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" | head -50
echo ""
