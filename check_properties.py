#!/usr/bin/env python3
"""
Check properties and their data status
"""

import requests
import json

API_BASE = "http://localhost:5000"
EMAIL = "jane.smith@realestate.com"
PASSWORD = "securepass123"

def check_properties():
    """Check what properties exist and their status"""
    
    print("=" * 80)
    print("              PROPERTY DATA STATUS CHECK")
    print("=" * 80)
    print()
    
    # Step 1: Login
    print("📍 Step 1: Login")
    print("-" * 80)
    try:
        response = requests.post(f"{API_BASE}/auth/login", json={
            "email": EMAIL,
            "password": PASSWORD
        })
        response.raise_for_status()
        data = response.json()
        token = data.get('token')
        print(f"✅ Login successful!")
        print()
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get Properties List
    print("📍 Step 2: Get Properties")
    print("-" * 80)
    try:
        response = requests.get(f"{API_BASE}/api/properties", headers=headers)
        response.raise_for_status()
        data = response.json()
        properties = data.get('properties', [])
        
        print(f"✅ Found {len(properties)} properties")
        print()
        
        if len(properties) == 0:
            print("⚠️  NO PROPERTIES FOUND!")
            print()
            print("ACTION REQUIRED:")
            print("1. Go to http://localhost:5173")
            print("2. Login")
            print("3. Click 'New Property'")
            print("4. Upload a floor plan OR enter an address")
            print("5. Wait for processing to complete (~5-10 seconds)")
            print()
            return False
        
        # Check each property
        for i, prop in enumerate(properties, 1):
            print(f"\n{'=' * 80}")
            print(f"PROPERTY #{i}")
            print(f"{'=' * 80}")
            print(f"ID: {prop.get('id')}")
            print(f"Status: {prop.get('status')}")
            print(f"Created: {prop.get('created_at')}")
            
            extracted = prop.get('extracted_data', {})
            print(f"\n📊 EXTRACTED DATA:")
            print(f"   Address: {extracted.get('address', 'N/A')}")
            print(f"   Bedrooms: {extracted.get('bedrooms', 0)}")
            print(f"   Bathrooms: {extracted.get('bathrooms', 0)}")
            print(f"   Sq Ft: {extracted.get('square_footage', 0)}")
            
            # Check for market insights
            market_insights = extracted.get('market_insights')
            if market_insights:
                print(f"\n💰 MARKET INSIGHTS: ✅ Present")
                comps = market_insights.get('comparable_properties', [])
                print(f"   Comparable Properties: {len(comps)}")
                if comps:
                    print(f"   Example comp: {comps[0].get('address', 'N/A')}")
            else:
                print(f"\n💰 MARKET INSIGHTS: ❌ Missing")
            
            # Check for listing copy
            listing_copy = extracted.get('listing_copy')
            if listing_copy:
                print(f"\n✍️  LISTING COPY: ✅ Present")
                print(f"   Headline: {listing_copy.get('headline', 'N/A')[:60]}...")
                print(f"   Description: {len(listing_copy.get('description', ''))} characters")
            else:
                print(f"\n✍️  LISTING COPY: ❌ Missing")
            
            # Status Analysis
            print(f"\n🔍 STATUS ANALYSIS:")
            status = prop.get('status')
            if status == 'complete':
                print(f"   ✅ Processing COMPLETE - All data should be available")
            elif status == 'processing':
                print(f"   ⏳ Still PROCESSING - Wait for completion")
            elif status == 'parsing_complete':
                print(f"   🔄 Floor plan parsed - Market analysis in progress")
            elif status == 'enrichment_complete':
                print(f"   🔄 Market data complete - Listing copy being generated")
            elif status == 'failed':
                print(f"   ❌ FAILED - Check Celery logs for errors")
            else:
                print(f"   ⚠️  Unknown status: {status}")
        
        print(f"\n{'=' * 80}")
        print("SUMMARY")
        print(f"{'=' * 80}")
        complete_count = sum(1 for p in properties if p.get('status') == 'complete')
        print(f"Total Properties: {len(properties)}")
        print(f"Complete: {complete_count}")
        print(f"Processing: {sum(1 for p in properties if p.get('status') in ['processing', 'parsing_complete', 'enrichment_complete'])}")
        print(f"Failed: {sum(1 for p in properties if 'failed' in p.get('status', ''))}")
        print()
        
        if complete_count == 0:
            print("⚠️  NO COMPLETED PROPERTIES!")
            print()
            print("NEXT STEPS:")
            print("1. Wait for properties to finish processing")
            print("2. Check Celery logs: docker logs ai-floorplan-celery --tail 100")
            print("3. Or upload a new property with a valid floor plan")
            print()
        else:
            print(f"✅ {complete_count} property(ies) ready to view")
            print(f"   Go to: http://localhost:5173")
            print(f"   Click on a completed property to see all data")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to fetch properties: {e}")
        return False

if __name__ == "__main__":
    check_properties()
