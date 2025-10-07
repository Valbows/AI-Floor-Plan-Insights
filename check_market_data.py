#!/usr/bin/env python3
"""Check if market insights data exists in database"""
import os
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv()

# Initialize Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

# Get all properties
result = supabase.table('properties').select('id, status, extracted_data').execute()

print("="*80)
print("CHECKING MARKET INSIGHTS DATA")
print("="*80)

for prop in result.data:
    extracted_data = prop.get('extracted_data', {})
    address = extracted_data.get('address', 'No address')
    print(f"\n📍 Property: {address}")
    print(f"   ID: {prop['id']}")
    print(f"   Status: {prop.get('status', 'unknown')}")
    
    # Check for market_insights
    if 'market_insights' in extracted_data:
        mi = extracted_data['market_insights']
        print(f"   ✅ Market Insights: PRESENT")
        
        # Check price estimate
        if 'price_estimate' in mi:
            pe = mi['price_estimate']
            print(f"      - Price Estimate: ${pe.get('estimated_value', 0):,}")
            print(f"      - Confidence: {pe.get('confidence', 'unknown')}")
        else:
            print(f"      - Price Estimate: MISSING")
        
        # Check market trend
        if 'market_trend' in mi:
            mt = mi['market_trend']
            print(f"      - Market Trend: {mt.get('trend_direction', 'unknown')}")
        else:
            print(f"      - Market Trend: MISSING")
        
        # Check investment analysis
        if 'investment_analysis' in mi:
            ia = mi['investment_analysis']
            print(f"      - Investment Score: {ia.get('investment_score', 0)}/100")
        else:
            print(f"      - Investment Analysis: MISSING")
    else:
        print(f"   ❌ Market Insights: NOT FOUND")
        print(f"   📋 Available keys: {list(extracted_data.keys())}")
    
    # Check for listing_copy
    if 'listing_copy' in extracted_data:
        lc = extracted_data['listing_copy']
        print(f"   ✅ Listing Copy: PRESENT")
        print(f"      - Headline: {lc.get('headline', 'missing')[:50]}...")
    else:
        print(f"   ❌ Listing Copy: NOT FOUND")

print("\n" + "="*80)
