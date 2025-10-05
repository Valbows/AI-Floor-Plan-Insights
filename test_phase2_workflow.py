#!/usr/bin/env python3
"""
Phase 2 Workflow Test Script
Tests the complete 3-agent pipeline: Floor Plan → Market Insights → Listing Copy
"""

import requests
import time
import json
import sys
from pathlib import Path

# Configuration
API_BASE = "http://localhost:5000"
TEST_EMAIL = "jane.smith@realestate.com"
TEST_PASSWORD = "Agent2025!"
TEST_ADDRESS = "123 Main Street, Miami, FL 33101"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}→ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def login():
    """Login and get JWT token"""
    print_header("STEP 1: Authentication")
    print_info(f"Logging in as {TEST_EMAIL}...")
    
    response = requests.post(f"{API_BASE}/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json()['token']
        print_success(f"Login successful! Token: {token[:20]}...")
        return token
    else:
        print_error(f"Login failed: {response.text}")
        sys.exit(1)


def upload_property(token, image_path):
    """Upload floor plan and trigger workflow"""
    print_header("STEP 2: Upload Floor Plan")
    print_info(f"Uploading: {image_path}")
    print_info(f"Address: {TEST_ADDRESS}")
    
    # Check if image exists
    if not Path(image_path).exists():
        print_error(f"Image not found: {image_path}")
        print_warning("Using a dummy image for testing...")
        # Create a minimal test image (1x1 PNG)
        import io
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        files = {'file': ('test.png', img_bytes, 'image/png')}
    else:
        files = {'file': open(image_path, 'rb')}
    
    data = {'address': TEST_ADDRESS}
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.post(
        f"{API_BASE}/api/properties/upload",
        files=files,
        data=data,
        headers=headers
    )
    
    if response.status_code == 201:
        property_data = response.json()['property']
        property_id = property_data['id']
        print_success(f"Upload successful!")
        print_info(f"Property ID: {property_id}")
        print_info(f"Status: {property_data['status']}")
        return property_id
    else:
        print_error(f"Upload failed: {response.text}")
        sys.exit(1)


def monitor_workflow(token, property_id, max_wait=120):
    """Monitor property status until complete or timeout"""
    print_header("STEP 3: Monitor Workflow Execution")
    print_info(f"Monitoring property {property_id}...")
    print_info("Expected flow: processing → parsing_complete → enrichment_complete → complete")
    print_info(f"Max wait time: {max_wait} seconds\n")
    
    headers = {'Authorization': f'Bearer {token}'}
    start_time = time.time()
    last_status = None
    
    while True:
        elapsed = int(time.time() - start_time)
        
        # Check timeout
        if elapsed > max_wait:
            print_error(f"Timeout after {max_wait} seconds!")
            return None
        
        # Fetch property
        response = requests.get(
            f"{API_BASE}/api/properties/{property_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            print_error(f"Failed to fetch property: {response.text}")
            time.sleep(5)
            continue
        
        property_data = response.json()['property']
        status = property_data['status']
        
        # Print status change
        if status != last_status:
            timestamp = time.strftime("%H:%M:%S")
            status_color = {
                'processing': Colors.WARNING,
                'parsing_complete': Colors.OKBLUE,
                'enrichment_complete': Colors.OKCYAN,
                'complete': Colors.OKGREEN,
                'failed': Colors.FAIL
            }.get(status, Colors.ENDC)
            
            print(f"[{timestamp}] {status_color}{status:25}{Colors.ENDC} ({elapsed}s elapsed)")
            last_status = status
        
        # Check if complete or failed
        if status == 'complete':
            print_success(f"\n✓ Workflow complete in {elapsed} seconds!")
            return property_data
        elif status in ['failed', 'enrichment_failed', 'listing_failed']:
            print_error(f"\n✗ Workflow failed with status: {status}")
            return property_data
        
        time.sleep(3)


def display_results(property_data):
    """Display all agent outputs"""
    print_header("STEP 4: Results from All 3 Agents")
    
    extracted_data = property_data.get('extracted_data', {})
    
    # Agent #1: Floor Plan Analyst
    print(f"\n{Colors.BOLD}🤖 Agent #1: Floor Plan Analyst{Colors.ENDC}")
    print("─" * 80)
    print(f"Address:        {extracted_data.get('address', 'N/A')}")
    print(f"Bedrooms:       {extracted_data.get('bedrooms', 0)}")
    print(f"Bathrooms:      {extracted_data.get('bathrooms', 0)}")
    print(f"Square Footage: {extracted_data.get('square_footage', 0):,}")
    print(f"Layout Type:    {extracted_data.get('layout_type', 'N/A')}")
    print(f"Features:       {', '.join(extracted_data.get('features', []))}")
    print(f"Rooms Count:    {len(extracted_data.get('rooms', []))}")
    
    # Agent #2: Market Insights Analyst
    market_insights = extracted_data.get('market_insights', {})
    if market_insights:
        print(f"\n{Colors.BOLD}🤖 Agent #2: Market Insights Analyst{Colors.ENDC}")
        print("─" * 80)
        
        price_estimate = market_insights.get('price_estimate', {})
        print(f"Estimated Value:    ${price_estimate.get('estimated_value', 0):,}")
        print(f"Confidence:         {price_estimate.get('confidence', 'N/A')}")
        print(f"Value Range:        ${price_estimate.get('value_range_low', 0):,} - ${price_estimate.get('value_range_high', 0):,}")
        print(f"Reasoning:          {price_estimate.get('reasoning', 'N/A')[:100]}...")
        
        market_trend = market_insights.get('market_trend', {})
        print(f"\nMarket Trend:       {market_trend.get('trend_direction', 'N/A')}")
        print(f"Buyer Demand:       {market_trend.get('buyer_demand', 'N/A')}")
        print(f"Inventory Level:    {market_trend.get('inventory_level', 'N/A')}")
        
        investment = market_insights.get('investment_analysis', {})
        print(f"\nInvestment Score:   {investment.get('investment_score', 0)}/100")
        print(f"Rental Potential:   {investment.get('rental_potential', 'N/A')}")
        if investment.get('estimated_rental_income'):
            print(f"Est. Rental Income: ${investment.get('estimated_rental_income', 0):,}/month")
        
        comps = market_insights.get('comparable_properties', [])
        print(f"\nComparable Properties: {len(comps)} found")
    else:
        print_warning("\n⚠ Agent #2 data not found")
    
    # Agent #3: Listing Copywriter
    listing_copy = extracted_data.get('listing_copy', {})
    if listing_copy:
        print(f"\n{Colors.BOLD}🤖 Agent #3: Listing Copywriter{Colors.ENDC}")
        print("─" * 80)
        print(f"Headline:     {listing_copy.get('headline', 'N/A')}")
        print(f"\nDescription Preview:")
        desc = listing_copy.get('description', 'N/A')
        print(f"  {desc[:200]}...")
        
        print(f"\nHighlights:")
        for i, highlight in enumerate(listing_copy.get('highlights', [])[:5], 1):
            print(f"  {i}. {highlight}")
        
        print(f"\nCall to Action: {listing_copy.get('call_to_action', 'N/A')}")
        print(f"Social Caption:  {listing_copy.get('social_media_caption', 'N/A')}")
        print(f"SEO Keywords:    {len(listing_copy.get('seo_keywords', []))} keywords")
    else:
        print_warning("\n⚠ Agent #3 data not found")
    
    # Summary
    print(f"\n{Colors.BOLD}Summary{Colors.ENDC}")
    print("─" * 80)
    print(f"Property ID:    {property_data['id']}")
    print(f"Final Status:   {property_data['status']}")
    print(f"Created:        {property_data['created_at']}")
    
    # Full JSON output
    print(f"\n{Colors.BOLD}Full JSON Response:{Colors.ENDC}")
    print(json.dumps(extracted_data, indent=2))


def main():
    """Run complete test workflow"""
    print_header("Phase 2 Workflow Test - 3 AI Agents Pipeline")
    print_info("Testing: Agent #1 → Agent #2 → Agent #3")
    print_info("Expected duration: 30-90 seconds\n")
    
    # Get test image path (use any floor plan in the project or create dummy)
    image_path = "test_floorplan.png"  # Adjust if you have a real floor plan
    
    try:
        # Step 1: Login
        token = login()
        
        # Step 2: Upload
        property_id = upload_property(token, image_path)
        
        # Step 3: Monitor
        property_data = monitor_workflow(token, property_id, max_wait=120)
        
        if not property_data:
            print_error("Workflow monitoring failed!")
            sys.exit(1)
        
        # Step 4: Display results
        display_results(property_data)
        
        # Final status
        print_header("Test Complete")
        if property_data['status'] == 'complete':
            print_success("✓ All 3 agents executed successfully!")
            print_success("✓ Phase 2 workflow verified!")
            return 0
        else:
            print_error(f"✗ Workflow ended with status: {property_data['status']}")
            return 1
            
    except KeyboardInterrupt:
        print_error("\n\nTest interrupted by user")
        return 1
    except Exception as e:
        print_error(f"\nTest failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
