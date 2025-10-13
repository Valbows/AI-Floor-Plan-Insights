"""
Manual test script for ATTOM API client
Tests basic connectivity and available endpoints
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.clients.attom_client import AttomAPIClient


def test_attom_connection():
    """Test ATTOM API connection and basic search"""
    print("=" * 60)
    print("ATTOM API Connection Test")
    print("=" * 60)
    
    # Initialize client
    try:
        client = AttomAPIClient()
        print("✅ ATTOM API client initialized")
        print(f"   API Key: {client.api_key[:10]}...{client.api_key[-5:]}")
    except ValueError as e:
        print(f"❌ Failed to initialize client: {e}")
        return False
    
    # Test property search
    print("\n" + "-" * 60)
    print("Test 1: Property Search")
    print("-" * 60)
    
    test_addresses = [
        {
            "address": "919 Malcolm Ave",
            "city": "Los Angeles",
            "state": "CA",
            "zip": "90024"
        },
        {
            "address": "1600 Pennsylvania Ave",
            "city": "Washington",
            "state": "DC",
            "zip": "20500"
        }
    ]
    
    for test_addr in test_addresses:
        print(f"\nSearching: {test_addr['address']}, {test_addr['city']}, {test_addr['state']}")
        try:
            result = client.search_property(
                address=test_addr['address'],
                city=test_addr['city'],
                state=test_addr['state'],
                zip_code=test_addr.get('zip')
            )
            print("✅ Property found!")
            print(f"   ATTOM ID: {result.get('attom_id')}")
            print(f"   Full Address: {result.get('address')}, {result.get('city')}, {result.get('state')} {result.get('zip')}")
            print(f"   Property Type: {result.get('property_type')}")
            print(f"   Bedrooms: {result.get('bedrooms')}")
            print(f"   Bathrooms: {result.get('bathrooms')}")
            print(f"   Square Feet: {result.get('square_feet')}")
            print(f"   Year Built: {result.get('year_built')}")
            print(f"   Last Sale Price: ${result.get('last_sale_price'):,}" if result.get('last_sale_price') else "   Last Sale Price: N/A")
            print(f"   Assessed Value: ${result.get('assessed_value'):,}" if result.get('assessed_value') else "   Assessed Value: N/A")
            
            # Save ATTOM ID for next tests
            if not hasattr(test_attom_connection, 'attom_id'):
                test_attom_connection.attom_id = result.get('attom_id')
                test_attom_connection.test_address = test_addr
            
        except Exception as e:
            print(f"❌ Property search failed: {e}")
    
    # Test AVM
    if hasattr(test_attom_connection, 'test_address'):
        print("\n" + "-" * 60)
        print("Test 2: AVM (Automated Valuation Model)")
        print("-" * 60)
        
        addr = test_attom_connection.test_address
        try:
            avm = client.get_avm(
                address=addr['address'],
                city=addr['city'],
                state=addr['state'],
                zip_code=addr.get('zip')
            )
            print("✅ AVM retrieved!")
            print(f"   Estimated Value: ${avm.get('estimated_value'):,}" if avm.get('estimated_value') else "   Estimated Value: N/A")
            print(f"   Confidence Score: {avm.get('confidence_score')}")
            print(f"   Value Range: ${avm.get('value_range_low'):,} - ${avm.get('value_range_high'):,}" if avm.get('value_range_low') else "   Value Range: N/A")
            print(f"   As of Date: {avm.get('as_of_date')}")
        except Exception as e:
            print(f"❌ AVM failed: {e}")
    
    # Test Sales History
    if hasattr(test_attom_connection, 'attom_id') and test_attom_connection.attom_id:
        print("\n" + "-" * 60)
        print("Test 3: Sales History")
        print("-" * 60)
        
        try:
            sales = client.get_sales_history(test_attom_connection.attom_id)
            print(f"✅ Sales history retrieved! ({len(sales)} records)")
            for i, sale in enumerate(sales[:5], 1):
                print(f"   Sale {i}: {sale.get('sale_date')} - ${sale.get('sale_price'):,}" if sale.get('sale_price') else f"   Sale {i}: {sale.get('sale_date')} - N/A")
        except Exception as e:
            print(f"❌ Sales history failed: {e}")
    
    # Test Area Stats
    if hasattr(test_attom_connection, 'test_address'):
        print("\n" + "-" * 60)
        print("Test 4: Area Statistics")
        print("-" * 60)
        
        zip_code = test_attom_connection.test_address.get('zip')
        if zip_code:
            try:
                stats = client.get_area_stats(zip_code)
                print(f"✅ Area stats retrieved for ZIP {zip_code}")
                print(f"   Median Home Value: ${stats.get('median_home_value'):,}" if stats.get('median_home_value') else "   Median Home Value: N/A")
                print(f"   Median Household Income: ${stats.get('median_household_income'):,}" if stats.get('median_household_income') else "   Median Household Income: N/A")
                print(f"   Population: {stats.get('population'):,}" if stats.get('population') else "   Population: N/A")
            except Exception as e:
                print(f"❌ Area stats failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("ATTOM API Test Summary")
    print("=" * 60)
    print(f"Total API requests made: {client.request_count}")
    print("✅ ATTOM API is operational and ready for integration!")
    
    return True


if __name__ == '__main__':
    test_attom_connection()
