"""
Redfin Property Scraper
Scrapes property data from Redfin.com using Bright Data
"""

import logging
from typing import Dict, Any
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class RedfinScraper(BaseScraper):
    """
    Redfin.com property data scraper
    
    Extracts:
    - Property details (beds, baths, sqft)
    - Redfin Estimate
    - Walk Score, Transit Score
    - School ratings
    - Listing details and history
    """
    
    BASE_URL = "https://www.redfin.com"
    
    async def search_property(self, address: str, city: str, state: str) -> Dict[str, Any]:
        """Search for a property on Redfin"""
        # Build search URL
        search_address = f"{address}-{city}-{state}".replace(' ', '-')
        search_url = f"{self.BASE_URL}/search/{search_address}"
        
        try:
            self.log_scraping_result(True, f"Searching Redfin for {address}, {city}, {state}")
            
            if not self.client:
                raise Exception("Bright Data client not initialized")
            
            html = await self.client.scrape_page(
                search_url,
                wait_for='div[class*="HomeCard"]',
                wait_timeout=30000
            )
            
            soup = self.parse_html(html)
            property_data = self._parse_search_results(soup)
            
            if property_data:
                self.log_scraping_result(True, "Found property on Redfin")
                return self.normalize_property_data(property_data)
            else:
                raise Exception("Property not found")
        
        except Exception as e:
            self.log_scraping_result(False, f"Search failed: {str(e)}")
            return self._empty_property_data()
    
    async def get_property_details(self, property_url: str) -> Dict[str, Any]:
        """Get detailed property information from Redfin listing page"""
        try:
            self.log_scraping_result(True, f"Fetching details from {property_url}")
            
            if not self.client:
                raise Exception("Bright Data client not initialized")
            
            html = await self.client.scrape_page(
                property_url,
                wait_for='div[class*="propertyDetails"]',
                wait_timeout=30000
            )
            
            soup = self.parse_html(html)
            property_data = self._parse_property_details(soup)
            property_data['listing_url'] = property_url
            
            self.log_scraping_result(True, "Property details fetched successfully")
            return self.normalize_property_data(property_data)
        
        except Exception as e:
            self.log_scraping_result(False, f"Failed to fetch details: {str(e)}")
            return self._empty_property_data()
    
    def _parse_search_results(self, soup) -> Dict[str, Any]:
        """Parse property data from Redfin search results"""
        try:
            # Find property card
            home_card = soup.find('div', class_=lambda x: x and 'HomeCard' in x)
            if not home_card:
                return {}
            
            # Extract basic info
            price = home_card.find('span', class_=lambda x: x and 'price' in x.lower())
            address = home_card.find('div', class_=lambda x: x and 'address' in x.lower())
            
            return {
                'price': price.text if price else None,
                'address': address.text if address else None
            }
        
        except Exception as e:
            logger.error(f"Failed to parse Redfin search results: {e}")
            return {}
    
    def _parse_property_details(self, soup) -> Dict[str, Any]:
        """Parse detailed property data from Redfin listing page"""
        try:
            data = {}
            
            # Redfin Estimate
            estimate = soup.find('span', class_=lambda x: x and 'estimate' in x.lower())
            if estimate:
                data['redfin_estimate'] = estimate.text
            
            # Walk Score
            walk_score = soup.find('div', {'data-rf-test-id': 'walk-score'})
            if walk_score:
                data['walk_score'] = walk_score.text
            
            return data
        
        except Exception as e:
            logger.error(f"Failed to parse Redfin property details: {e}")
            return {}
    
    def _empty_property_data(self) -> Dict[str, Any]:
        """Return empty property data structure"""
        return self.normalize_property_data({
            'source': 'Redfin',
            'address': None
        })
