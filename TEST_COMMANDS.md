# Phase 2 Testing Commands

## Quick Test with curl

### 1. Login and Get Token

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"jane.smith@realestate.com","password":"Agent2025!"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

echo "Token: $TOKEN"
```

### 2. Upload Floor Plan (with any image)

```bash
# Using a test image (create test.png first or use existing floor plan)
curl -X POST http://localhost:5000/api/properties/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_floorplan.png" \
  -F "address=123 Main Street, Miami, FL 33101" \
  | python3 -m json.tool
```

**Expected Response**:
```json
{
  "property": {
    "id": "uuid-here",
    "floor_plan_url": "https://...",
    "address": "123 Main Street, Miami, FL 33101",
    "status": "processing",
    "created_at": "2025-10-05T..."
  }
}
```

### 3. Monitor Property Status

```bash
# Replace PROPERTY_ID with the ID from upload response
PROPERTY_ID="your-property-id-here"

# Check status (run multiple times)
curl -s -X GET "http://localhost:5000/api/properties/$PROPERTY_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Status Progression**:
- `processing` → Agent #1 running
- `parsing_complete` → Agent #1 done, Agent #2 starting
- `enrichment_complete` → Agent #2 done, Agent #3 starting
- `complete` → All 3 agents done!

### 4. View Complete Results

```bash
# Get full property data with all agent outputs
curl -s -X GET "http://localhost:5000/api/properties/$PROPERTY_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "import sys, json; data = json.load(sys.stdin); print(json.dumps(data['property']['extracted_data'], indent=2))"
```

---

## Python Test Script

### Run Complete Automated Test

```bash
# Install dependencies (if not already installed)
pip3 install requests Pillow

# Run test script
python3 test_phase2_workflow.py
```

**What it does**:
1. ✓ Authenticates with API
2. ✓ Uploads floor plan with address
3. ✓ Monitors workflow execution in real-time
4. ✓ Displays results from all 3 agents
5. ✓ Shows full JSON response

**Expected Output**:
```
================================================================================
                      Phase 2 Workflow Test - 3 AI Agents Pipeline
================================================================================

[00:00:00] processing                (0s elapsed)
[00:00:05] parsing_complete          (5s elapsed)
[00:00:25] enrichment_complete       (25s elapsed)
[00:00:45] complete                  (45s elapsed)

✓ Workflow complete in 45 seconds!

🤖 Agent #1: Floor Plan Analyst
────────────────────────────────────────────────────────────────────────────────
Address:        123 Main Street, Miami, FL 33101
Bedrooms:       3
Bathrooms:      2.0
Square Footage: 1,132
...

🤖 Agent #2: Market Insights Analyst
────────────────────────────────────────────────────────────────────────────────
Estimated Value:    $425,000
Confidence:         high
Investment Score:   78/100
...

🤖 Agent #3: Listing Copywriter
────────────────────────────────────────────────────────────────────────────────
Headline:     Stunning 3BR Home with Modern Upgrades
Description:  Welcome to this beautiful 3-bedroom...
...
```

---

## Monitor Celery Logs (Real-Time)

Watch workflow execution in Celery worker:

```bash
docker logs -f ai-floorplan-celery
```

**What to look for**:
```
[INFO] Analyzing floor plan with AI Agent #1...
[INFO] Extracted data: {...}
[INFO] Floor plan analysis complete

[INFO] Enriching property data...
[INFO] Running market analysis with AI Agent #2...
[INFO] Fetching CoreLogic data for: 123 Main Street, Miami, FL 33101
[INFO] Market insights generated: Price estimate $425,000

[INFO] Generating listing copy with AI Agent #3...
[INFO] Listing generated: Stunning 3BR Home with Modern Upgrades
[INFO] Listing copy generation complete
```

---

## Check Database Directly (Optional)

```bash
# Connect to Supabase dashboard
# Navigate to: Table Editor → properties
# View the `extracted_data` column (JSONB)
```

Should contain:
```json
{
  "address": "123 Main Street, Miami, FL 33101",
  "bedrooms": 3,
  "bathrooms": 2.0,
  "square_footage": 1132,
  "market_insights": {
    "price_estimate": {...},
    "market_trend": {...},
    "investment_analysis": {...}
  },
  "listing_copy": {
    "headline": "...",
    "description": "...",
    "highlights": [...]
  }
}
```

---

## Troubleshooting

### Issue: Address shows "Not specified"
**Solution**: Fixed! Upload form now requires address and preserves it through workflow.

### Issue: Only Agent #1 runs, not #2 and #3
**Solution**: Fixed! Now calling `process_property_workflow` instead of just `process_floor_plan_task`.

### Issue: CoreLogic API errors
**Options**:
1. Add real CoreLogic credentials to `.env`
2. Or let it use fallback logic (basic estimates without API)

### Issue: Workflow times out
- Check Celery logs: `docker logs ai-floorplan-celery --tail 50`
- Check backend logs: `docker logs ai-floorplan-backend --tail 50`
- Verify Gemini API key is valid
- Check Redis is running: `docker ps | grep redis`

---

## Expected Timing

| Agent | Task | Duration |
|-------|------|----------|
| **Agent #1** | Floor plan analysis (Gemini Vision) | ~5-10s |
| **Agent #2** | Market insights (CoreLogic + Gemini) | ~15-30s |
| **Agent #3** | Listing copy (Gemini) | ~10-20s |
| **Total** | Complete workflow | **30-60s** |

*Note: First run may be slower due to model initialization*

---

## Success Criteria

✅ **Phase 2 Complete** when you see:
1. ✓ Address preserved from upload form
2. ✓ Agent #1 extracts floor plan data
3. ✓ Agent #2 generates market insights
4. ✓ Agent #3 creates listing copy
5. ✓ Status reaches `complete`
6. ✓ All data visible in API response

---

## Next Steps After Testing

Once Phase 2 is verified:
- [ ] Update frontend to display Agent #2 data (market insights)
- [ ] Update frontend to display Agent #3 data (listing copy)
- [ ] Add social media sharing features
- [ ] Add listing editor UI

**Ready for Phase 3!** 🚀
