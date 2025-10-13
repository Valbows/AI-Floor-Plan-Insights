#!/bin/bash
# Test ATTOM API endpoints with curl

echo "=========================================="
echo "ATTOM API Test Suite"
echo "=========================================="
echo ""

ATTOM_API_KEY="19139ecb49c2aa4f74e2e68868edf452"
BASE_URL="https://api.gateway.attomdata.com/propertyapi/v1.0.0"

# Test 1: Property Search by Address
echo "Test 1: Property Search by Address"
echo "-------------------------------------------"
echo "Endpoint: /property/address"
echo "Address: 4529 Winona Ct, Denver, CO 80212"
echo ""

curl -s -X GET \
  "${BASE_URL}/property/address?address1=4529%20Winona%20Ct&address2=Denver,%20CO&postalcode=80212" \
  -H "apikey: ${ATTOM_API_KEY}" \
  -H "Accept: application/json" | jq '.'

echo ""
echo ""

# Test 2: Property Detail (requires property ID from search)
echo "Test 2: Property Detail"
echo "-------------------------------------------"
echo "Note: This test requires an ATTOM ID from a successful search"
echo ""

# Test 3: Property AVM (Automated Valuation Model)
echo "Test 3: AVM - Automated Valuation Model"
echo "-------------------------------------------"
echo "Endpoint: /property/avm"
echo "Address: 4529 Winona Ct, Denver, CO 80212"
echo ""

curl -s -X GET \
  "${BASE_URL}/property/avm?address1=4529%20Winona%20Ct&address2=Denver,%20CO&postalcode=80212" \
  -H "apikey: ${ATTOM_API_KEY}" \
  -H "Accept: application/json" | jq '.'

echo ""
echo ""

# Test 4: Area Statistics
echo "Test 4: Area Statistics by ZIP Code"
echo "-------------------------------------------"
echo "Endpoint: /area/full"
echo "ZIP Code: 80212"
echo ""

curl -s -X GET \
  "${BASE_URL}/area/full?postalcode=80212" \
  -H "apikey: ${ATTOM_API_KEY}" \
  -H "Accept: application/json" | jq '.'

echo ""
echo ""

# Test 5: Property Expanded Profile (comprehensive data)
echo "Test 5: Property Expanded Profile"
echo "-------------------------------------------"
echo "Endpoint: /property/expandedprofile"
echo "Address: 4529 Winona Ct, Denver, CO 80212"
echo ""

curl -s -X GET \
  "${BASE_URL}/property/expandedprofile?address1=4529%20Winona%20Ct&address2=Denver,%20CO&postalcode=80212" \
  -H "apikey: ${ATTOM_API_KEY}" \
  -H "Accept: application/json" | jq '.'

echo ""
echo ""

# Test 6: Alternative Address (NYC example)
echo "Test 6: Alternative Address Test (NYC)"
echo "-------------------------------------------"
echo "Endpoint: /property/address"
echo "Address: 350 5th Ave, New York, NY 10118"
echo ""

curl -s -X GET \
  "${BASE_URL}/property/address?address1=350%205th%20Ave&address2=New%20York,%20NY&postalcode=10118" \
  -H "apikey: ${ATTOM_API_KEY}" \
  -H "Accept: application/json" | jq '.'

echo ""
echo ""

echo "=========================================="
echo "ATTOM API Test Complete"
echo "=========================================="
echo ""
echo "Summary:"
echo "- If you see 'status.code: 0' - API call was successful"
echo "- If you see 'status.code: 1' - Error occurred (check msg)"
echo "- Free trial may have limited coverage"
echo ""
