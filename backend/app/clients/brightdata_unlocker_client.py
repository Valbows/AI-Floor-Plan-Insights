"""
Bright Data Web Unlocker API Client
Simple REST API for bypassing anti-bot measures and robots.txt

Documentation: https://docs.brightdata.com/scraping-automation/web-unlocker/introduction

This is SIMPLER and more reliable than Browser API for scraping Zillow, Redfin, etc.
"""

import os
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BrightDataUnlockerClient:
    """
    Client for Bright Data Web Unlocker API
    
    Features:
    - Simple REST API (no WebSocket complexity)
    - Bypasses robots.txt and anti-bot measures
    - Automatic CAPTCHA solving
    - Intelligent proxy rotation
    - Works with KYC or non-KYC accounts
    
    Usage:
        client = BrightDataUnlockerClient()
        html = client.get('https://www.zillow.com/...')
    """
    
    API_ENDPOINT = "https://api.brightdata.com/request"
    
    def __init__(self, api_key: Optional[str] = None, zone_name: Optional[str] = None):
        """
        Initialize Web Unlocker client
        
        Args:
            api_key: Bright Data API key (or from BRIGHTDATA_API_KEY env var)
            zone_name: Web Unlocker zone name (or from BRIGHTDATA_UNLOCKER_ZONE env var)
        """
        self.api_key = api_key or os.getenv('BRIGHTDATA_API_KEY')
        self.zone_name = zone_name or os.getenv('BRIGHTDATA_UNLOCKER_ZONE') or 'ai_floor_plan_unlocker'
        
        if not self.api_key:
            raise ValueError("Bright Data API key required. Set BRIGHTDATA_API_KEY environment variable.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
        logger.info(f"Bright Data Web Unlocker initialized (zone: {self.zone_name})")
    
    def get(
        self,
        url: str,
        format: str = 'raw',
        timeout: int = 60,
        **kwargs
    ) -> str:
        """
        Fetch a URL using Web Unlocker
        
        Args:
            url: Target URL to scrape
            format: Response format ('raw' for HTML, 'json' for structured data)
            timeout: Request timeout in seconds
            **kwargs: Additional parameters for the API
            
        Returns:
            Response content (HTML or JSON)
        """
        payload = {
            'zone': self.zone_name,
            'url': url,
            'format': format,
            **kwargs
        }
        
        try:
            logger.info(f"Fetching {url} via Web Unlocker...")
            
            response = self.session.post(
                self.API_ENDPOINT,
                json=payload,
                timeout=timeout
            )
            
            response.raise_for_status()
            
            # For raw format, return the text
            if format == 'raw':
                content = response.text
                logger.info(f"✅ Successfully fetched {url} ({len(content)} bytes)")
                return content
            else:
                # For JSON format, return the JSON response
                data = response.json()
                logger.info(f"✅ Successfully fetched {url} (JSON response)")
                return data
        
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout fetching {url}")
            raise
        
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            error_msg = e.response.text
            logger.error(f"❌ HTTP {status_code} error fetching {url}: {error_msg}")
            raise
        
        except Exception as e:
            logger.error(f"❌ Failed to fetch {url}: {e}")
            raise
    
    def post(
        self,
        url: str,
        body: Dict[str, Any],
        format: str = 'raw',
        timeout: int = 60,
        **kwargs
    ) -> str:
        """
        POST request using Web Unlocker
        
        Args:
            url: Target URL
            body: POST body data
            format: Response format
            timeout: Request timeout
            **kwargs: Additional parameters
            
        Returns:
            Response content
        """
        payload = {
            'zone': self.zone_name,
            'url': url,
            'format': format,
            'body': body,
            **kwargs
        }
        
        try:
            logger.info(f"POST to {url} via Web Unlocker...")
            
            response = self.session.post(
                self.API_ENDPOINT,
                json=payload,
                timeout=timeout
            )
            
            response.raise_for_status()
            
            if format == 'raw':
                content = response.text
                logger.info(f"✅ Successfully posted to {url} ({len(content)} bytes)")
                return content
            else:
                data = response.json()
                logger.info(f"✅ Successfully posted to {url} (JSON response)")
                return data
        
        except Exception as e:
            logger.error(f"❌ Failed to POST to {url}: {e}")
            raise
    
    def get_json(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch a URL and return JSON response
        
        Args:
            url: Target URL
            **kwargs: Additional parameters
            
        Returns:
            Parsed JSON response
        """
        return self.get(url, format='json', **kwargs)
    
    def get_html(self, url: str, **kwargs) -> str:
        """
        Fetch a URL and return raw HTML
        
        Args:
            url: Target URL
            **kwargs: Additional parameters
            
        Returns:
            Raw HTML content
        """
        return self.get(url, format='raw', **kwargs)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


# Example usage
if __name__ == '__main__':
    # Test with a simple page
    client = BrightDataUnlockerClient()
    
    # Test 1: Simple GET
    html = client.get_html('https://example.com')
    print(f"Fetched {len(html)} bytes from example.com")
    print(html[:200])
    
    # Test 2: Zillow (should work without robots.txt blocking!)
    try:
        zillow_url = 'https://www.zillow.com/homedetails/123-Main-St-Los-Angeles-CA-90001/12345_zpid/'
        html = client.get_html(zillow_url)
        print(f"\\nFetched {len(html)} bytes from Zillow")
        print("✅ Zillow scraping works!")
    except Exception as e:
        print(f"❌ Zillow test failed: {e}")
