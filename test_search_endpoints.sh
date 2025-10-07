#!/bin/bash
source .env

TOKEN=$(curl -s -X POST "https://api-prod.corelogic.com/oauth/token?grant_type=client_credentials" \
  -u "$CORELOGIC_CONSUMER_KEY:$CORELOGIC_CONSUMER_SECRET" -H "Content-Length: 0" | \
  python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)

echo "Testing Property Search endpoints..."
echo ""

# Test different endpoint patterns
ENDPOINTS=(
  "/property-search?address=919%20MALCOLM%20AVE&city=LOS%20ANGELES&state=CA&zip=90024"
  "/search?address=919%20MALCOLM%20AVE&city=LOS%20ANGELES&state=CA&zip=90024"
  "/properties/search?address=919%20MALCOLM%20AVE"
  "/property/search?streetAddress=919%20MALCOLM%20AVE&city=LOS%20ANGELES&state=CA"
)

for endpoint in "${ENDPOINTS[@]}"; do
  echo "Testing: $endpoint"
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://api-prod.corelogic.com$endpoint" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Accept: application/json")
  echo "HTTP Status: $HTTP_CODE"
  echo ""
done
