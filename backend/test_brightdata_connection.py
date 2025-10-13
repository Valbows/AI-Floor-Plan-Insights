#!/usr/bin/env python3
"""
Test Bright Data Browser API Connection
Simple script to verify WebSocket connection works
"""

import asyncio
import os
import sys
from playwright.async_api import async_playwright

# Configuration from .env
BRIGHTDATA_USERNAME = "brd-customer-hl_85d26a60-zone-ai_floor_plan_scraper"
BRIGHTDATA_PASSWORD = "zr8l1vlqm7bi"
WS_ENDPOINT = f"wss://{BRIGHTDATA_USERNAME}:{BRIGHTDATA_PASSWORD}@brd.superproxy.io:9222"


async def test_connection():
    """Test connection to Bright Data Browser API"""
    
    print("=" * 60)
    print("Bright Data Browser API Connection Test")
    print("=" * 60)
    print()
    
    print(f"Username: {BRIGHTDATA_USERNAME}")
    print(f"Endpoint: wss://brd.superproxy.io:9222")
    print()
    print("Connecting to Bright Data...")
    
    try:
        async with async_playwright() as playwright:
            # Connect to Bright Data browser
            browser = await playwright.chromium.connect_over_cdp(
                WS_ENDPOINT,
                timeout=30000  # 30 seconds
            )
            
            print("✅ Connected to Bright Data Browser API!")
            print()
            
            # Create a new page
            context = await browser.new_context()
            page = await context.new_page()
            
            print("Testing with a simple web request...")
            
            # Test with a simple website
            await page.goto("https://www.example.com", wait_until="domcontentloaded", timeout=30000)
            
            title = await page.title()
            url = page.url
            
            print(f"✅ Successfully loaded page!")
            print(f"   URL: {url}")
            print(f"   Title: {title}")
            print()
            
            # Clean up
            await page.close()
            await context.close()
            await browser.close()
            
            print("=" * 60)
            print("✅ TEST PASSED - Bright Data is working!")
            print("=" * 60)
            print()
            print("You can now use the scrapers to collect property data.")
            
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Verify your zone is 'Active' in the dashboard")
        print("2. Check that free credits haven't expired (6 days left)")
        print("3. Ensure username matches exactly:")
        print(f"   Expected: {BRIGHTDATA_USERNAME}")
        print("4. Wait 1-2 minutes if zone was just created")
        print()
        return False


if __name__ == '__main__':
    print()
    result = asyncio.run(test_connection())
    sys.exit(0 if result else 1)
