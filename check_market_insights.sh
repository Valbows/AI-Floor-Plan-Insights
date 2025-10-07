#!/bin/bash
# Check if Market Insights (Agent #2) is working with CoreLogic

echo "============================================================"
echo "   MARKET INSIGHTS (AGENT #2) DIAGNOSTIC CHECK"
echo "============================================================"
echo ""
echo "Checking Celery logs for Agent #2 activity..."
echo ""

# Check if CoreLogic API is being called
echo "1. CoreLogic API Calls:"
echo "------------------------------------------------------------"
docker logs ai-floorplan-celery 2>&1 | grep -i "corelogic" | tail -10

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ CoreLogic API calls detected"
else
    echo "❌ NO CoreLogic API calls found"
fi

echo ""
echo "2. Market Insights Task Status:"
echo "------------------------------------------------------------"
docker logs ai-floorplan-celery 2>&1 | grep -E "market_insights|Agent #2|enrichment" | tail -15

echo ""
echo "3. Recent Task Execution:"
echo "------------------------------------------------------------"
docker logs ai-floorplan-celery 2>&1 | grep -E "Task.*succeeded|Task.*failed" | tail -10

echo ""
echo "4. LiteLLM Errors (if any):"
echo "------------------------------------------------------------"
docker logs ai-floorplan-celery 2>&1 | grep -i "litellm.*error" | tail -5

if [ $? -ne 0 ]; then
    echo "✅ No LiteLLM errors found"
fi

echo ""
echo "============================================================"
echo "   RECOMMENDATION"
echo "============================================================"
echo ""
echo "To verify Market Insights are working:"
echo ""
echo "1. Create a NEW property with a real address"
echo "2. Run this command to watch logs LIVE:"
echo "   docker logs ai-floorplan-celery --follow"
echo ""
echo "3. Look for these patterns:"
echo "   ✅ 'Calling CoreLogic API...'"
echo "   ✅ 'Found X comparable properties'"
echo "   ✅ 'Market analysis complete'"
echo ""
echo "4. If you see mock data warnings:"
echo "   ⚠️  'Using mock data for comparable properties'"
echo "   ⚠️  'CoreLogic API returned no results'"
echo "   → CoreLogic API might not have data for that address"
echo ""
