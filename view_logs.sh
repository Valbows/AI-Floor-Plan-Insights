#!/bin/bash
# Quick Log Viewer Script

echo "================================"
echo "   LOG VIEWER - Select Option"
echo "================================"
echo ""
echo "1. Backend logs (Flask API)"
echo "2. Frontend logs (React/Vite)"
echo "3. Celery logs (Background tasks - MARKET INSIGHTS HERE)"
echo "4. Redis logs"
echo "5. All logs (combined)"
echo "6. Follow Celery logs LIVE (best for debugging)"
echo "7. Search Celery for 'market_insights'"
echo "8. Search Celery for 'CoreLogic'"
echo ""
echo "================================"
read -p "Enter option (1-8): " choice

case $choice in
  1)
    echo "📋 BACKEND LOGS (last 100 lines):"
    echo "================================"
    docker logs ai-floorplan-backend --tail 100
    ;;
  2)
    echo "📋 FRONTEND LOGS (last 100 lines):"
    echo "================================"
    docker logs ai-floorplan-frontend --tail 100
    ;;
  3)
    echo "📋 CELERY LOGS (last 100 lines):"
    echo "================================"
    docker logs ai-floorplan-celery --tail 100
    ;;
  4)
    echo "📋 REDIS LOGS (last 100 lines):"
    echo "================================"
    docker logs ai-floorplan-redis --tail 100
    ;;
  5)
    echo "📋 ALL LOGS (last 50 lines each):"
    echo "================================"
    echo ""
    echo ">>> BACKEND:"
    docker logs ai-floorplan-backend --tail 50
    echo ""
    echo ">>> FRONTEND:"
    docker logs ai-floorplan-frontend --tail 50
    echo ""
    echo ">>> CELERY:"
    docker logs ai-floorplan-celery --tail 50
    ;;
  6)
    echo "📋 FOLLOWING CELERY LOGS LIVE:"
    echo "================================"
    echo "Press Ctrl+C to stop"
    echo ""
    docker logs ai-floorplan-celery --follow
    ;;
  7)
    echo "🔍 SEARCHING CELERY FOR 'market_insights':"
    echo "================================"
    docker logs ai-floorplan-celery --tail 500 | grep -i "market_insights"
    ;;
  8)
    echo "🔍 SEARCHING CELERY FOR 'CoreLogic':"
    echo "================================"
    docker logs ai-floorplan-celery --tail 500 | grep -i "corelogic"
    ;;
  *)
    echo "Invalid option"
    ;;
esac
