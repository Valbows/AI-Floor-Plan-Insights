"""
Bright Data Scraping Browser Client
Handles browser-based web scraping using Bright Data's proxy network

Documentation: https://docs.brightdata.com/scraping-automation/scraping-browser/introduction
"""

import os
import asyncio
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import logging

logger = logging.getLogger(__name__)


class BrightDataClient:
    """
    Client for Bright Data Scraping Browser
    
    Features:
    - WebSocket connection to Bright Data proxy network
    - Automatic CAPTCHA solving
    - Browser automation with Playwright
    - Anti-detection measures
    - Session management
    
    Usage:
        async with BrightDataClient() as client:
            page = await client.new_page()
            await page.goto('https://example.com')
            content = await page.content()
    """
    
    def __init__(self, api_key: Optional[str] = None, username: Optional[str] = None, 
                 password: Optional[str] = None):
        """
        Initialize Bright Data Scraping Browser client
        
        Args:
            api_key: Bright Data API key (or from BRIGHTDATA_API_KEY env var)
            username: Bright Data username (optional, derived from API key)
            password: Bright Data password (optional, same as API key)
        
        Note:
            For Bright Data, the AUTH format is typically USERNAME:PASSWORD
            where PASSWORD is your API key. Username format depends on your zone.
        """
        self.api_key = api_key or os.getenv('BRIGHTDATA_API_KEY')
        
        if not self.api_key:
            raise ValueError("Bright Data API key not found. Set BRIGHTDATA_API_KEY environment variable")
        
        # Bright Data WebSocket endpoint
        # Format: wss://USERNAME:PASSWORD@brd.superproxy.io:9222
        # Username should be from your Browser API zone (format: brd-customer-xxx-zone-xxx)
        self.username = username or os.getenv('BRIGHTDATA_USERNAME') or f"brd-customer-{self.api_key[:10]}"
        self.password = password or os.getenv('BRIGHTDATA_PASSWORD') or self.api_key
        
        self.ws_endpoint = f"wss://{self.username}:{self.password}@brd.superproxy.io:9222"
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        
        # Configuration
        self.timeout = 120000  # 2 minutes
        self.headless = True
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def connect(self):
        """
        Connect to Bright Data Scraping Browser
        
        Raises:
            Exception: If connection fails
        """
        try:
            self.playwright = await async_playwright().start()
            
            logger.info("Connecting to Bright Data Scraping Browser...")
            
            # Connect to Bright Data's browser
            self.browser = await self.playwright.chromium.connect_over_cdp(
                self.ws_endpoint,
                timeout=self.timeout
            )
            
            # Create browser context with anti-detection settings
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36',
                java_script_enabled=True,
                accept_downloads=False
            )
            
            logger.info("✅ Connected to Bright Data Scraping Browser")
            
        except Exception as e:
            logger.error(f"Failed to connect to Bright Data: {e}")
            raise Exception(f"Bright Data connection failed: {str(e)}")
    
    async def new_page(self) -> Page:
        """
        Create a new page in the browser context
        
        Returns:
            Playwright Page object
        
        Raises:
            Exception: If not connected or page creation fails
        """
        if not self.context:
            raise Exception("Not connected to Bright Data. Call connect() first.")
        
        page = await self.context.new_page()
        
        # Set default timeout
        page.set_default_timeout(self.timeout)
        
        return page
    
    async def close(self):
        """Close browser connection and cleanup"""
        try:
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            logger.info("✅ Bright Data connection closed")
            
        except Exception as e:
            logger.error(f"Error closing Bright Data connection: {e}")
    
    async def scrape_page(self, url: str, wait_for: Optional[str] = None,
                         wait_timeout: int = 30000) -> str:
        """
        Scrape a single page and return HTML content
        
        Args:
            url: URL to scrape
            wait_for: CSS selector to wait for before returning (optional)
            wait_timeout: Timeout for wait_for selector (milliseconds)
        
        Returns:
            HTML content of the page
        
        Raises:
            Exception: If scraping fails
        """
        page = await self.new_page()
        
        try:
            logger.info(f"Navigating to {url}...")
            
            # Navigate to URL
            await page.goto(url, wait_until='domcontentloaded', timeout=self.timeout)
            
            # Wait for specific element if specified
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=wait_timeout)
            
            # Get page content
            content = await page.content()
            
            logger.info(f"✅ Successfully scraped {url}")
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            raise Exception(f"Page scraping failed: {str(e)}")
        
        finally:
            await page.close()
    
    async def scrape_with_js(self, url: str, js_code: str) -> Any:
        """
        Scrape a page and execute custom JavaScript
        
        Args:
            url: URL to scrape
            js_code: JavaScript code to execute on the page
        
        Returns:
            Result of JavaScript execution
        
        Raises:
            Exception: If scraping or JS execution fails
        """
        page = await self.new_page()
        
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=self.timeout)
            
            # Execute JavaScript
            result = await page.evaluate(js_code)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute JS on {url}: {e}")
            raise Exception(f"JS execution failed: {str(e)}")
        
        finally:
            await page.close()


# Synchronous wrapper for use in non-async contexts
class BrightDataSyncClient:
    """
    Synchronous wrapper for BrightDataClient
    
    Usage:
        with BrightDataSyncClient() as client:
            content = client.scrape_page('https://example.com')
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = None
        self.loop = None
    
    def __enter__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.client = BrightDataClient(api_key=self.api_key)
        self.loop.run_until_complete(self.client.connect())
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.loop.run_until_complete(self.client.close())
        if self.loop:
            self.loop.close()
    
    def scrape_page(self, url: str, wait_for: Optional[str] = None) -> str:
        """Synchronous scrape_page wrapper"""
        if not self.client:
            raise Exception("Client not initialized")
        return self.loop.run_until_complete(
            self.client.scrape_page(url, wait_for=wait_for)
        )
    
    def scrape_with_js(self, url: str, js_code: str) -> Any:
        """Synchronous scrape_with_js wrapper"""
        if not self.client:
            raise Exception("Client not initialized")
        return self.loop.run_until_complete(
            self.client.scrape_with_js(url, js_code)
        )
