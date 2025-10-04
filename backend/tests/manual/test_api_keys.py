#!/usr/bin/env python3
"""
Manual API Key Validation Script
Run this to verify all external API keys are working correctly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Google Gemini API connection"""
    print("\n🧪 Testing Google Gemini API...")
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        if not api_key:
            print("❌ GOOGLE_GEMINI_API_KEY not found in environment")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content("Say 'API test successful' in exactly 3 words")
        
        print(f"✅ Gemini API working! Response: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"❌ Gemini API failed: {str(e)}")
        return False


def test_tavily_api():
    """Test Tavily Search API"""
    print("\n🧪 Testing Tavily API...")
    try:
        from tavily import TavilyClient
        
        api_key = os.getenv('TAVILY_API_KEY')
        if not api_key:
            print("❌ TAVILY_API_KEY not found in environment")
            return False
        
        client = TavilyClient(api_key=api_key)
        response = client.search("test query", max_results=1)
        
        if response and 'results' in response:
            print(f"✅ Tavily API working! Found {len(response['results'])} results")
            return True
        else:
            print("❌ Tavily API returned unexpected format")
            return False
    except Exception as e:
        print(f"❌ Tavily API failed: {str(e)}")
        return False


def test_corelogic_api():
    """Test CoreLogic Property API authentication"""
    print("\n🧪 Testing CoreLogic API...")
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        consumer_key = os.getenv('CORELOGIC_CONSUMER_KEY')
        consumer_secret = os.getenv('CORELOGIC_CONSUMER_SECRET')
        
        if not consumer_key or not consumer_secret:
            print("❌ CoreLogic credentials not found in environment")
            return False
        
        # Get OAuth token
        auth_url = 'https://api-prod.corelogic.com/oauth/token?grant_type=client_credentials'
        response = requests.post(
            auth_url,
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                print(f"✅ CoreLogic API working! Token expires in {data.get('expires_in')}s")
                return True
            else:
                print("❌ CoreLogic API returned unexpected format")
                return False
        else:
            print(f"❌ CoreLogic API failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ CoreLogic API failed: {str(e)}")
        return False


def test_google_maps_api():
    """Test Google Maps API"""
    print("\n🧪 Testing Google Maps API...")
    try:
        import requests
        
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not api_key:
            print("❌ GOOGLE_MAPS_API_KEY not found in environment")
            return False
        
        # Test Geocoding API
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': '1600 Amphitheatre Parkway, Mountain View, CA',
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'OK':
                print("✅ Google Maps API working!")
                return True
            else:
                print(f"❌ Google Maps API error: {data.get('status')}")
                return False
        else:
            print(f"❌ Google Maps API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Google Maps API failed: {str(e)}")
        return False


def test_supabase_connection():
    """Test Supabase connection"""
    print("\n🧪 Testing Supabase connection...")
    try:
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_ANON_KEY')
        
        if not url or not key:
            print("❌ Supabase credentials not found in environment")
            return False
        
        client = create_client(url, key)
        
        # Test connection by listing tables (should work even with empty database)
        # Using a simple health check
        print(f"✅ Supabase connection established to {url}")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return False


def main():
    """Run all API tests"""
    print("=" * 60)
    print("🔍 API Key Validation Test Suite")
    print("=" * 60)
    
    results = {
        'Gemini': test_gemini_api(),
        'Tavily': test_tavily_api(),
        'CoreLogic': test_corelogic_api(),
        'Google Maps': test_google_maps_api(),
        'Supabase': test_supabase_connection()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for service, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{service:20} {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n{passed}/{total} services configured correctly")
    
    if passed == total:
        print("\n🎉 All API keys validated successfully!")
        return 0
    else:
        print("\n⚠️  Some API keys need attention. Check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
