#!/usr/bin/env python3
"""
Test ATTOM Sales Trends API
Verify the new /salestrend endpoint works correctly
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.clients.attom_client import AttomAPIClient


def test_sales_trends():
    """Test ATTOM sales trends for NYC market"""
    print("=" * 70)
    print("TESTING ATTOM SALES TRENDS API")
    print("=" * 70)
    
    try:
        client = AttomAPIClient()
        print(f"✅ ATTOM client initialized")
        print(f"   API Key: {client.api_key[:10]}...")
        
        # Test with Manhattan ZIP (10022 - Midtown East)
        zip_code = "10022"
        print(f"\n📊 Fetching sales trends for ZIP {zip_code}...")
        
        trends = client.get_sales_trends(zip_code, interval='monthly')
        
        print(f"\n✅ Sales Trends Retrieved Successfully!")
        print(f"   ZIP Code: {trends['zip_code']}")
        print(f"   Current Median Price: ${trends['current_median_price']:,}" if trends['current_median_price'] else "   Current Median Price: N/A")
        print(f"   Current Avg Price: ${trends['current_avg_price']:,}" if trends['current_avg_price'] else "   Current Avg Price: N/A")
        print(f"   Price per Sq Ft: ${trends['price_per_sqft']:.2f}" if trends['price_per_sqft'] else "   Price per Sq Ft: N/A")
        print(f"   Sales (12 months): {trends['sale_count_12mo']}")
        print(f"   YoY Change: {trends['yoy_change_pct']:.1f}%" if trends['yoy_change_pct'] else "   YoY Change: N/A")
        print(f"   Market Velocity: {trends['market_velocity']}")
        
        print(f"\n📈 Historical Trends (last 12 months):")
        for i, trend in enumerate(trends['trends'][:12]):
            period = trend['period']
            median = trend['median_price']
            count = trend['sale_count']
            if median and count:
                print(f"   {i+1}. {period}: ${median:,} (n={count})")
            else:
                print(f"   {i+1}. {period}: Data unavailable")
        
        print(f"\n✅ TEST PASSED - Sales trends data is working!")
        print(f"\n💡 This data provides:")
        print(f"   - Real median/average prices for comp analysis")
        print(f"   - Price per sqft for regression models")
        print(f"   - Market velocity for investment analysis")
        print(f"   - Historical trends for predictive modeling")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_sales_trends()
    sys.exit(0 if success else 1)
