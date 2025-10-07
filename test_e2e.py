#!/usr/bin/env python3
"""
End-to-End Test for AI Floor Plan Insights
Tests the complete workflow: upload → analyze → enrich → generate listing
"""

import requests
import time
import json
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:5000"
LOGIN_EMAIL = "jane.smith@realestate.com"
LOGIN_PASSWORD = "Agent2025!"
TEST_ADDRESS = "888 Lexington Avenue, New York, NY 10065"

def print_step(step_num, message):
    """Print formatted step"""
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {message}")
    print('='*60)

def login():
    """Login and get JWT token"""
    print_step(1, "Logging in")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD}
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    token = data.get('token')
    print(f"✅ Login successful")
    if token:
        print(f"   Token: {token[:30]}...")
    return token

def create_property(token):
    """Create a new property"""
    print_step(2, f"Creating property: {TEST_ADDRESS}")
    
    # Try to use a real floor plan image if available
    floor_plan_path = Path('sample_floor_plan.png')
    if floor_plan_path.exists():
        with open(floor_plan_path, 'rb') as f:
            test_image = f.read()
        print(f"   Using real floor plan: {floor_plan_path}")
    else:
        # Fallback to simple 1x1 pixel PNG
        test_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        print(f"   Using test 1x1 PNG")
    
    files = {
        'file': ('test_floor_plan.png', test_image, 'image/png')
    }
    data = {
        'address': TEST_ADDRESS
    }
    
    response = requests.post(
        f"{BASE_URL}/api/properties/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
        data=data
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Property creation failed: {response.status_code}")
        print(response.text)
        return None
    
    property_data = response.json()
    # Handle nested property object
    if 'property' in property_data:
        prop = property_data['property']
        property_id = prop.get('id')
        address = prop.get('address')
    else:
        property_id = property_data.get('id')
        address = property_data.get('address')
    
    print(f"✅ Property created")
    print(f"   ID: {property_id}")
    print(f"   Address: {address}")
    return property_id

def wait_for_processing(token, property_id, max_wait=120):
    """Wait for property processing to complete"""
    print_step(3, "Waiting for AI processing")
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < max_wait:
        response = requests.get(
            f"{BASE_URL}/api/properties/{property_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get property status: {response.status_code}")
            return None
        
        data = response.json()
        status = data.get('status')
        
        if status != last_status:
            print(f"   Status: {status}")
            last_status = status
        
        if status == 'completed':
            print(f"✅ Processing completed in {int(time.time() - start_time)}s")
            return data
        elif status == 'failed':
            print(f"❌ Processing failed")
            print(f"   Error: {data.get('error_message', 'Unknown error')}")
            return None
        
        time.sleep(3)
    
    print(f"❌ Timeout after {max_wait}s")
    return None

def verify_results(property_data):
    """Verify all components worked correctly"""
    print_step(4, "Verifying Results")
    
    results = {
        'floor_plan_analysis': False,
        'market_insights': False,
        'listing_copy': False,
        'corelogic_used': False
    }
    
    # Check floor plan analysis
    extracted_data = property_data.get('extracted_data', {})
    if extracted_data.get('bedrooms') is not None:
        results['floor_plan_analysis'] = True
        print(f"✅ Floor Plan Analysis: {extracted_data.get('bedrooms')} BR, {extracted_data.get('bathrooms')} BA, {extracted_data.get('square_footage')} sq ft")
    else:
        print(f"❌ Floor Plan Analysis: No data")
    
    # Check market insights
    market_insights = property_data.get('market_insights', {})
    price_estimate = market_insights.get('price_estimate', {})
    if price_estimate.get('estimated_value'):
        results['market_insights'] = True
        print(f"✅ Market Insights: ${price_estimate.get('estimated_value'):,} estimated value")
        print(f"   Confidence: {price_estimate.get('confidence')}")
        
        # Check if CoreLogic was used
        reasoning = price_estimate.get('reasoning', '')
        if 'CoreLogic data unavailable' in reasoning or 'web search' in reasoning.lower():
            results['corelogic_used'] = False
            print(f"⚠️  CoreLogic: Used fallback (web search)")
        else:
            results['corelogic_used'] = True
            print(f"✅ CoreLogic: Successfully retrieved property data")
    else:
        print(f"❌ Market Insights: No data")
    
    # Check listing copy
    listing_copy = property_data.get('listing_copy', {})
    if listing_copy.get('headline'):
        results['listing_copy'] = True
        print(f"✅ Listing Copy: \"{listing_copy.get('headline')}\"")
    else:
        print(f"❌ Listing Copy: No data")
    
    return results

def main():
    """Run E2E test"""
    print("\n" + "="*60)
    print("AI FLOOR PLAN INSIGHTS - END-TO-END TEST")
    print("="*60)
    
    # Login
    token = login()
    if not token:
        sys.exit(1)
    
    # Create property
    property_id = create_property(token)
    if not property_id:
        sys.exit(1)
    
    # Wait for processing
    property_data = wait_for_processing(token, property_id)
    if not property_data:
        sys.exit(1)
    
    # Verify results
    results = verify_results(property_data)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    all_passed = all([
        results['floor_plan_analysis'],
        results['market_insights'],
        results['listing_copy']
    ])
    
    if all_passed:
        print("✅ ALL TESTS PASSED")
        if results['corelogic_used']:
            print("✅ CoreLogic integration working!")
        else:
            print("⚠️  CoreLogic unavailable (using fallback)")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
