#!/bin/bash
# Real-time performance monitor for floor plan analysis

echo "=========================================="
echo "FLOOR PLAN ANALYSIS PERFORMANCE MONITOR"
echo "=========================================="
echo ""
echo "Monitoring: /tmp/celery_optimized.log"
echo "Press Ctrl+C to stop"
echo ""

tail -f /tmp/celery_optimized.log | grep --line-buffered -E "Task.*process_floor_plan.*succeeded|Task.*enrich_property_data.*succeeded|Task.*generate_listing_copy.*succeeded|Step 1|Step 2|Step 3|ATTOM|Scraping|Tavily|property_id" | while read line; do
    timestamp=$(echo "$line" | grep -oE '\[[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}')
    
    # Extract timing
    if echo "$line" | grep -q "succeeded in"; then
        time=$(echo "$line" | grep -oE '[0-9]+\.[0-9]+s')
        task=$(echo "$line" | grep -oE 'process_floor_plan|enrich_property_data|generate_listing_copy')
        
        case "$task" in
            process_floor_plan)
                echo "✅ Floor Plan Analysis: $time"
                ;;
            enrich_property_data)
                echo "✅ Property Enrichment: $time"
                ;;
            generate_listing_copy)
                echo "✅ Listing Copy: $time"
                echo "=========================================="
                ;;
        esac
    elif echo "$line" | grep -q "Step 1"; then
        echo "🔍 Step 1: Google Vision analysis..."
    elif echo "$line" | grep -q "Step 2"; then
        echo "🔍 Step 2: OCR dimension extraction..."
    elif echo "$line" | grep -q "Step 3"; then
        echo "🔍 Step 3: Merging data..."
    elif echo "$line" | grep -q "ATTOM"; then
        echo "📊 ATTOM API call..."
    elif echo "$line" | grep -q "Scraping"; then
        echo "🌐 Web scraping..."
    fi
done
