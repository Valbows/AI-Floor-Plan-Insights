#!/usr/bin/env python3
"""Check what data is available for analytics"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from app.utils.supabase_client import get_supabase_client

def main():
    client = get_supabase_client()
    
    # Check all properties
    result = client.table('properties').select('*').execute()
    properties = result.data
    
    print(f"\n{'='*80}")
    print(f"TOTAL PROPERTIES: {len(properties)}")
    print(f"{'='*80}\n")
    
    # Status breakdown
    print("STATUS BREAKDOWN:")
    statuses = {}
    for p in properties:
        status = p.get('status', 'unknown')
        statuses[status] = statuses.get(status, 0) + 1
    
    for status, count in sorted(statuses.items(), key=lambda x: -x[1]):
        print(f"  {status:30s}: {count}")
    
    print(f"\n{'='*80}\n")
    
    # Check properties that would match analytics query
    print("ANALYTICS QUERY SIMULATION:")
    print("Looking for properties with status in ('complete', 'enrichment_complete')...\n")
    
    matching = [p for p in properties if p.get('status') in ('complete', 'enrichment_complete')]
    print(f"Found {len(matching)} properties matching analytics criteria")
    
    if len(matching) > 0:
        print("\nSample properties:")
        for p in matching[:3]:
            ed = p.get('extracted_data', {}) or {}
            print(f"  - ID: {p['id'][:8]}... | Beds: {ed.get('bedrooms')} | Baths: {ed.get('bathrooms')} | SqFt: {ed.get('square_footage')}")
    
    print(f"\n{'='*80}\n")
    
    # Check what statuses have complete data
    print("PROPERTIES WITH PRICE ESTIMATES (by status):")
    status_with_prices = {}
    for p in properties:
        ed = p.get('extracted_data', {}) or {}
        mi = ed.get('market_insights', {}) or {}
        pe = mi.get('price_estimate', {}) or {}
        if pe.get('estimated_value'):
            status = p.get('status', 'unknown')
            status_with_prices[status] = status_with_prices.get(status, 0) + 1
    
    for status, count in sorted(status_with_prices.items(), key=lambda x: -x[1]):
        print(f"  {status:30s}: {count} properties")
    
    print(f"\n{'='*80}\n")
    
    # Recommendations
    print("RECOMMENDATION:")
    if len(matching) < 5:
        most_common_status = max(statuses.items(), key=lambda x: x[1])[0]
        print(f"  Your properties have status '{most_common_status}' ({statuses[most_common_status]} properties)")
        print(f"  But analytics is looking for status 'complete' or 'enrichment_complete'")
        print(f"\n  ✅ FIX: Update the SQL query in regression_models.py line 188")
        print(f"     Change: WHERE p.status IN ('complete', 'enrichment_complete')")
        print(f"     To:     WHERE p.status IN ('{most_common_status}')")
    else:
        print(f"  ✅ You have enough properties ({len(matching)}) with the correct status!")
        print(f"  The issue might be with missing square footage or price data.")

if __name__ == '__main__':
    main()


