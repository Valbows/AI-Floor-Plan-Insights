#!/bin/bash

# CoreLogic API Integration Test
# Tests OAuth authentication and basic property search

set -e

echo "=================================="
echo "CoreLogic API Integration Test"
echo "=================================="
echo ""

# Load credentials from .env
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | grep CORELOGIC | xargs)
fi

# Verify credentials are set
if [ -z "$CORELOGIC_CONSUMER_KEY" ] || [ -z "$CORELOGIC_CONSUMER_SECRET" ]; then
    echo "❌ ERROR: CoreLogic credentials not found in .env"
    echo "Please set CORELOGIC_CONSUMER_KEY and CORELOGIC_CONSUMER_SECRET"
    exit 1
fi

API_URL="${CORELOGIC_API_URL:-https://api-prod.corelogic.com}"
AUTH_URL="$API_URL/oauth/token"
PROPERTY_URL="$API_URL/property"

echo "📍 API URL: $API_URL"
echo "🔑 Consumer Key: ${CORELOGIC_CONSUMER_KEY:0:20}..."
echo ""

# Step 1: Get OAuth2 Access Token
echo "Step 1: Requesting OAuth2 access token..."
echo "Auth URL: $AUTH_URL?grant_type=client_credentials"
echo ""

TOKEN_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X POST "$AUTH_URL?grant_type=client_credentials" \
  -u "$CORELOGIC_CONSUMER_KEY:$CORELOGIC_CONSUMER_SECRET" \
  -H "Content-Length: 0")

HTTP_STATUS=$(echo "$TOKEN_RESPONSE" | grep HTTP_STATUS | cut -d: -f2)
TOKEN_BODY=$(echo "$TOKEN_RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" != "200" ]; then
    echo "❌ OAuth2 Authentication FAILED"
    echo "HTTP Status: $HTTP_STATUS"
    echo "Response: $TOKEN_BODY"
    exit 1
fi

echo "✅ OAuth2 Authentication SUCCESS"
ACCESS_TOKEN=$(echo "$TOKEN_BODY" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ ERROR: Failed to extract access token"
    echo "Response: $TOKEN_BODY"
    exit 1
fi

echo "🎫 Access Token: ${ACCESS_TOKEN:0:50}..."
echo ""

# Step 2: Test Property Typeahead Search
echo "Step 2: Testing property typeahead search..."
TEST_ADDRESS="919 MALCOLM AVE, LOS ANGELES, CA 90024"
echo "Searching for: $TEST_ADDRESS"
echo ""

SEARCH_URL="$PROPERTY_URL/typeahead"
SEARCH_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X GET "$SEARCH_URL?input=$(echo "$TEST_ADDRESS" | sed 's/ /%20/g')" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Accept: application/json")

HTTP_STATUS=$(echo "$SEARCH_RESPONSE" | grep HTTP_STATUS | cut -d: -f2)
SEARCH_BODY=$(echo "$SEARCH_RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" != "200" ]; then
    echo "❌ Property Search FAILED"
    echo "HTTP Status: $HTTP_STATUS"
    echo "Response: $SEARCH_BODY"
    exit 1
fi

echo "✅ Property Search SUCCESS"
echo ""
echo "Response Preview:"
echo "$SEARCH_BODY" | head -30
echo ""

# Extract property ID from typeahead results (format: fipsCode:universalParcelId)
PROPERTY_ID=$(echo "$SEARCH_BODY" | grep -o '"address":"[^"]*"' | head -1 | cut -d'"' -f4)
# Try alternative JSON parsing
if [ -z "$PROPERTY_ID" ]; then
    PROPERTY_ID=$(echo "$SEARCH_BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['results'][0]['address']) if 'results' in data and len(data['results']) > 0 else ''" 2>/dev/null || echo "")
fi

if [ -n "$PROPERTY_ID" ]; then
    echo "📋 Found Property ID: $PROPERTY_ID"
    echo ""
    
    # Step 3: Test Property Details
    echo "Step 3: Testing property details retrieval..."
    DETAILS_URL="$PROPERTY_URL/$PROPERTY_ID"
    
    DETAILS_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
      -X GET "$DETAILS_URL" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Accept: application/json")
    
    HTTP_STATUS=$(echo "$DETAILS_RESPONSE" | grep HTTP_STATUS | cut -d: -f2)
    DETAILS_BODY=$(echo "$DETAILS_RESPONSE" | sed '/HTTP_STATUS/d')
    
    if [ "$HTTP_STATUS" != "200" ]; then
        echo "❌ Property Details FAILED"
        echo "HTTP Status: $HTTP_STATUS"
        echo "Response: $DETAILS_BODY"
        exit 1
    fi
    
    echo "✅ Property Details SUCCESS"
    echo ""
    echo "Response Preview:"
    echo "$DETAILS_BODY" | head -30
    echo ""
fi

# Summary
echo "=================================="
echo "✅ ALL TESTS PASSED"
echo "=================================="
echo ""
echo "CoreLogic API is accessible and responding correctly."
echo "OAuth2 authentication: ✅"
echo "Property typeahead search: ✅"
[ -n "$PROPERTY_ID" ] && echo "Property details: ✅"
echo ""
echo "The API credentials are working correctly!"
