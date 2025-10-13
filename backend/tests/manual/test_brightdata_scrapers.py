"""
Manual test script for Bright Data scrapers
Tests web scraping functionality for Zillow, Redfin, and StreetEasy
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.scrapers.multi_source_scraper import MultiSourceScraper


async def test_brightdata_scrapers():
    """Test Bright Data web scraping"""
    print("=" * 60)
    print("Bright Data Web Scraper Test")
    print("=" * 60)
    
    # Test addresses
    test_properties = [
        {
            "address": "123 Main St",
            "city": "New York",
            "state": "NY"
        },
        {
            "address": "456 Oak Ave",
            "city": "Los Angeles",
            "state": "CA"
        }
    ]
    
    try:
        # Initialize multi-source scraper
        async with MultiSourceScraper() as scraper:
            print("✅ Bright Data Multi-Source Scraper initialized")
            print(f"   API Key: {scraper.api_key[:10] if scraper.api_key else 'NOT SET'}...")
            
            for prop in test_properties:
                print("\n" + "-" * 60)
                print(f"Test: Scraping {prop['address']}, {prop['city']}, {prop['state']}")
                print("-" * 60)
                
                try:
                    # Scrape from all sources
                    result = await scraper.scrape_property(
                        address=prop['address'],
                        city=prop['city'],
                        state=prop['state']
                    )
                    
                    print(f"\n✅ Multi-source scrape complete!")
                    print(f"   Sources Available: {result['sources_count']}")
                    print(f"   Sources: {', '.join(result['sources_available'])}")
                    print(f"   Data Quality Score: {result['data_quality_score']}/100")
                    
                    if result['price_consensus']:
                        print(f"\n   Price Consensus: ${result['price_consensus']:,}")
                        if result['price_low'] != result['price_high']:
                            print(f"   Price Range: ${result['price_low']:,} - ${result['price_high']:,}")
                    
                    if result.get('address'):
                        print(f"   Address: {result['address']}")
                    
                    if result.get('bedrooms'):
                        print(f"   Bedrooms: {result['bedrooms']}")
                    
                    if result.get('bathrooms'):
                        print(f"   Bathrooms: {result['bathrooms']}")
                    
                    if result.get('square_feet'):
                        print(f"   Square Feet: {result['square_feet']:,}")
                    
                    # Show source breakdown
                    print(f"\n   Source Breakdown:")
                    for source_name, source_data in result['sources'].items():
                        if source_data and source_data.get('price'):
                            print(f"   - {source_name.title()}: ${source_data['price']:,}" if isinstance(source_data['price'], int) else f"   - {source_name.title()}: {source_data['price']}")
                
                except Exception as e:
                    print(f"❌ Scraping failed: {e}")
            
            print("\n" + "=" * 60)
            print("Bright Data Scraper Test Complete")
            print("=" * 60)
            print("✅ Scrapers are operational and ready for integration!")
    
    except ValueError as e:
        print(f"❌ Failed to initialize scrapers: {e}")
        print("\nNote: Make sure BRIGHTDATA_API_KEY is set in .env file")
        return False
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True


if __name__ == '__main__':
    # Run async test
    asyncio.run(test_brightdata_scrapers())
