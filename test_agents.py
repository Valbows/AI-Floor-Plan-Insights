#!/usr/bin/env python3
"""
Test if CrewAI agents work with LiteLLM format
"""

import sys
import os

# Add backend to path
sys.path.insert(0, '/app')

print("=" * 80)
print("   TESTING CREWAI AGENTS WITH LITELLM")
print("=" * 80)
print()

# Test Agent #2 - Market Insights
print("📊 Testing Agent #2: Market Insights Analyst")
print("-" * 80)

try:
    from app.agents.market_insights_analyst import MarketInsightsAnalyst
    
    analyst = MarketInsightsAnalyst()
    print(f"✅ Agent initialized successfully")
    print(f"   LLM Model: {analyst.llm}")
    print(f"   Role: {analyst.role}")
    print()
    
    # Try a simple analysis
    print("🔄 Testing with sample address...")
    result = analyst.analyze_property(
        address="123 Main St, Los Angeles, CA 90001",
        property_data={
            "bedrooms": 3,
            "bathrooms": 2,
            "square_footage": 1500,
            "layout_type": "traditional"
        }
    )
    
    print("✅ Analysis complete!")
    print(f"   Price Estimate: ${result.get('price_estimate', {}).get('estimated_value', 'N/A'):,}")
    print(f"   Market Trend: {result.get('market_trend', {}).get('trend_direction', 'N/A')}")
    print(f"   Comps Found: {len(result.get('comparable_properties', []))}")
    print()
    
except Exception as e:
    print(f"❌ Agent #2 FAILED: {e}")
    import traceback
    traceback.print_exc()
    print()

# Test Agent #3 - Listing Copywriter
print("✍️  Testing Agent #3: Listing Copywriter")
print("-" * 80)

try:
    from app.agents.listing_copywriter import ListingCopywriter
    
    writer = ListingCopywriter()
    print(f"✅ Agent initialized successfully")
    print(f"   LLM Model: {writer.llm}")
    print(f"   Role: {writer.role}")
    print()
    
    # Try a simple listing generation
    print("🔄 Testing listing generation...")
    result = writer.generate_listing(
        property_data={
            "address": "123 Main St, Los Angeles, CA 90001",
            "bedrooms": 3,
            "bathrooms": 2,
            "square_footage": 1500,
            "layout_type": "traditional",
            "features": ["hardwood floors", "granite countertops"]
        },
        market_insights={
            "price_estimate": {"estimated_value": 500000},
            "market_trend": {"trend_direction": "rising"}
        }
    )
    
    print("✅ Listing generated!")
    print(f"   Headline: {result.get('headline', 'N/A')[:60]}...")
    print(f"   Description Length: {len(result.get('description', ''))} chars")
    print(f"   Highlights: {len(result.get('highlights', []))} items")
    print()
    
except Exception as e:
    print(f"❌ Agent #3 FAILED: {e}")
    import traceback
    traceback.print_exc()
    print()

print("=" * 80)
print("   TEST COMPLETE")
print("=" * 80)
