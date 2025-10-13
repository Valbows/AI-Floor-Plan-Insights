"""
Bright Data Scrapers Library Client
Uses Bright Data's pre-built scrapers API (simpler than Browser API)

This client uses the Web Scrapers Library API instead of the Browser API,
which is simpler and available in the free/playground tier.

Documentation: https://docs.brightdata.com/datasets/scrapers
"""

import os
import requests
import time
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BrightDataScrapersClient:
    """
    Client for Bright Data's Scrapers Library API
    
    Uses pre-built scrapers for popular sites including:
    - Zillow (properties, price history, full information)
    - Redfin
    - Realtor.com
    - And many others
    
    This is simpler than Browser API and doesn't require WebSocket connections.
    """
    
    BASE_URL = "https://api.brightdata.com/datasets/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Bright Data Scrapers client
        
        Args:
            api_key: Bright Data API key (or from BRIGHTDATA_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('BRIGHTDATA_API_KEY')
        
        if not self.api_key:
            raise ValueError("Bright Data API key required. Set BRIGHTDATA_API_KEY environment variable.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
        logger.info("Bright Data Scrapers client initialized")
    
    def trigger_scrape(
        self,
        dataset_id: str,
        input_data: List[Dict[str, Any]],
        discover_by: Optional[str] = None,
        max_records: Optional[int] = None
    ) -> str:
        """
        Trigger an asynchronous scrape job
        
        Args:
            dataset_id: The scraper ID (e.g., 'gd_l7q7dkf244hwxwzta' for Zillow)
            input_data: List of input parameters (URLs, addresses, etc.)
            discover_by: Discovery method ('search_url', 'filter', etc.)
            max_records: Maximum number of records to collect
            
        Returns:
            snapshot_id: ID to track the scraping job
        """
        url = f"{self.BASE_URL}/trigger"
        
        payload = {
            'dataset_id': dataset_id,
            'endpoint': 'trigger',
            'discover_by': discover_by or 'direct_input',
            'limit_multiple': max_records or 100
        }
        
        # Add input data
        if discover_by == 'search_url':
            payload['url'] = input_data[0].get('url')
        else:
            payload['input'] = input_data
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            snapshot_id = result.get('snapshot_id')
            logger.info(f"Scrape triggered successfully. Snapshot ID: {snapshot_id}")
            return snapshot_id
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to trigger scrape: {e}")
            raise
    
    def get_snapshot_status(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Check the status of a scraping job
        
        Args:
            snapshot_id: The snapshot ID returned from trigger_scrape
            
        Returns:
            Status information including progress and completion
        """
        url = f"{self.BASE_URL}/snapshot/{snapshot_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get snapshot status: {e}")
            raise
    
    def get_snapshot_data(self, snapshot_id: str, format: str = 'json') -> Any:
        """
        Retrieve the scraped data
        
        Args:
            snapshot_id: The snapshot ID
            format: Output format ('json', 'csv', 'ndjson')
            
        Returns:
            The scraped data
        """
        url = f"{self.BASE_URL}/snapshot/{snapshot_id}?format={format}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            if format == 'json':
                return response.json()
            else:
                return response.text
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get snapshot data: {e}")
            raise
    
    def wait_for_completion(
        self,
        snapshot_id: str,
        max_wait_seconds: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Wait for a scraping job to complete
        
        Args:
            snapshot_id: The snapshot ID
            max_wait_seconds: Maximum time to wait
            poll_interval: How often to check status (seconds)
            
        Returns:
            Final status information
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_seconds:
            status = self.get_snapshot_status(snapshot_id)
            
            state = status.get('status')
            logger.info(f"Snapshot {snapshot_id} status: {state}")
            
            if state in ['ready', 'completed']:
                return status
            elif state in ['failed', 'cancelled']:
                raise Exception(f"Scraping job failed with status: {state}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Scraping job did not complete within {max_wait_seconds} seconds")
    
    def scrape_zillow_by_address(
        self,
        address: str,
        city: str,
        state: str,
        zip_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scrape Zillow property data by address
        
        Args:
            address: Street address
            city: City name
            state: State code (e.g., 'CA', 'NY')
            zip_code: ZIP code (optional)
            
        Returns:
            Property data from Zillow
        """
        # Construct search URL for Zillow
        search_address = f"{address}, {city}, {state}"
        if zip_code:
            search_address += f" {zip_code}"
        
        # Replace spaces with dashes for Zillow URL format
        url_address = search_address.replace(' ', '-').replace(',', '')
        zillow_url = f"https://www.zillow.com/homes/{url_address}_rb/"
        
        # Use Zillow Full Properties Information scraper
        # Dataset ID: gd_l7q7dkf244hwxwzta (example - get actual ID from dashboard)
        input_data = [{'url': zillow_url}]
        
        logger.info(f"Scraping Zillow for: {search_address}")
        
        try:
            # Note: Replace 'gd_l7q7dkf244hwxwzta' with actual dataset ID from your dashboard
            snapshot_id = self.trigger_scrape(
                dataset_id='gd_l7q7dkf244hwxwzta',  # Zillow scraper ID
                input_data=input_data,
                discover_by='search_url'
            )
            
            # Wait for completion
            status = self.wait_for_completion(snapshot_id)
            
            # Get the data
            data = self.get_snapshot_data(snapshot_id)
            
            return {
                'source': 'Zillow',
                'data': data,
                'snapshot_id': snapshot_id,
                'status': status
            }
        
        except Exception as e:
            logger.error(f"Zillow scraping failed: {e}")
            return {
                'source': 'Zillow',
                'error': str(e),
                'data': None
            }
    
    def scrape_synchronous(
        self,
        dataset_id: str,
        input_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform synchronous scraping (immediate results)
        Use for simple, small requests
        
        Args:
            dataset_id: The scraper ID
            input_data: Input parameters
            
        Returns:
            Scraped data (immediate)
        """
        url = f"{self.BASE_URL}/scrape"
        
        payload = {
            'dataset_id': dataset_id,
            'input': input_data
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Synchronous scrape failed: {e}")
            raise
    
    def list_available_scrapers(self, category: str = 'real-estate') -> List[Dict[str, Any]]:
        """
        List available scrapers in a category
        
        Args:
            category: Category name ('real-estate', 'e-commerce', etc.)
            
        Returns:
            List of available scrapers
        """
        # Note: This endpoint may need to be updated based on actual API
        url = f"{self.BASE_URL}/scrapers?category={category}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not list scrapers: {e}")
            return []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


# Example usage
if __name__ == '__main__':
    client = BrightDataScrapersClient()
    
    # Scrape a property
    result = client.scrape_zillow_by_address(
        address='123 Main St',
        city='Los Angeles',
        state='CA',
        zip_code='90001'
    )
    
    print(result)
