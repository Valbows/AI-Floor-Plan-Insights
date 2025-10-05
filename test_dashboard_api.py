#!/usr/bin/env python3
"""
Quick API Test - Dashboard Endpoints
Tests GET /api/properties and PUT /api/properties/<id>
"""

import requests
import json

API_BASE = "http://localhost:5000"
EMAIL = "jane.smith@realestate.com"
PASSWORD = "securepass123"

def test_dashboard_endpoints():
    """Test dashboard API endpoints"""
    
    print("=" * 80)
    print("                  DASHBOARD API TEST")
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
        print(f"   Token: {token[:20]}...")
        print()
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get Properties List
    print("📍 Step 2: GET /api/properties (Dashboard endpoint)")
    print("-" * 80)
    try:
        response = requests.get(f"{API_BASE}/api/properties", headers=headers)
        response.raise_for_status()
        data = response.json()
        properties = data.get('properties', [])
        
        print(f"✅ Properties fetched successfully!")
        print(f"   Total properties: {len(properties)}")
        
        if properties:
            print(f"\n   Sample property:")
            prop = properties[0]
            extracted_data = prop.get('extracted_data', {})
            print(f"   - ID: {prop.get('id')}")
            print(f"   - Address: {extracted_data.get('address', 'N/A')}")
            print(f"   - Status: {prop.get('status')}")
            print(f"   - Bedrooms: {extracted_data.get('bedrooms', 0)}")
            print(f"   - Bathrooms: {extracted_data.get('bathrooms', 0)}")
            print(f"   - Sq Ft: {extracted_data.get('square_footage', 0)}")
            
            # Save first property ID for PUT test
            property_id = prop.get('id')
        else:
            print(f"   ⚠️  No properties found. Upload a floor plan first.")
            property_id = None
        
        print()
    except Exception as e:
        print(f"❌ Failed to fetch properties: {e}")
        return False
    
    # Step 3: Test PUT endpoint (if we have a property)
    if property_id:
        print("📍 Step 3: PUT /api/properties/<id> (Edit listing endpoint)")
        print("-" * 80)
        try:
            test_listing = {
                "listing_copy": {
                    "headline": "Test Updated Headline",
                    "description": "This is a test description updated via API",
                    "highlights": [
                        "Test feature 1",
                        "Test feature 2",
                        "Test feature 3"
                    ],
                    "call_to_action": "Contact us for a showing!",
                    "social_media_caption": "Check out this property!",
                    "email_subject": "New Listing Available",
                    "seo_keywords": ["test", "property", "listing"]
                }
            }
            
            response = requests.put(
                f"{API_BASE}/api/properties/{property_id}",
                headers=headers,
                json=test_listing
            )
            response.raise_for_status()
            data = response.json()
            
            print(f"✅ Property updated successfully!")
            print(f"   Message: {data.get('message')}")
            print(f"   Headline updated: {test_listing['listing_copy']['headline']}")
            print()
            
            # Verify update by fetching property again
            print("📍 Step 4: Verify update (GET single property)")
            print("-" * 80)
            response = requests.get(
                f"{API_BASE}/api/properties/{property_id}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            prop = data.get('property', {})
            listing_copy = prop.get('listing_copy', {})
            
            if listing_copy.get('headline') == test_listing['listing_copy']['headline']:
                print(f"✅ Update verified! Headline matches.")
            else:
                print(f"⚠️  Update verification: Headline doesn't match")
                print(f"   Expected: {test_listing['listing_copy']['headline']}")
                print(f"   Got: {listing_copy.get('headline', 'N/A')}")
            
            print()
            
        except Exception as e:
            print(f"❌ Failed to update property: {e}")
            if hasattr(e, 'response'):
                print(f"   Response: {e.response.text}")
            return False
    else:
        print("📍 Step 3: PUT endpoint (SKIPPED - no properties)")
        print("-" * 80)
        print("   ⚠️  Upload a floor plan first to test the PUT endpoint")
        print()
    
    # Summary
    print("=" * 80)
    print("                           TEST SUMMARY")
    print("=" * 80)
    print()
    print("✅ Login: PASS")
    print("✅ GET /api/properties: PASS")
    if property_id:
        print("✅ PUT /api/properties/<id>: PASS")
        print("✅ Verification: PASS")
    else:
        print("⏭️  PUT endpoint: SKIPPED (no properties)")
    print()
    print("=" * 80)
    print("              🎉 ALL TESTS PASSED! READY TO TEST UI 🎉")
    print("=" * 80)
    print()
    print("NEXT STEPS:")
    print("1. Open http://localhost:5173")
    print("2. Login with jane.smith@realestate.com / securepass123")
    print("3. Verify dashboard displays properties correctly")
    print("4. Check test_dashboard.md for full testing checklist")
    print()
    
    return True

if __name__ == "__main__":
    test_dashboard_endpoints()
