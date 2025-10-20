"""
StreetEasy Property Scraper
Scrapes property data from StreetEasy.com using Bright Data
"""

import logging
from typing import Dict, Any
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class StreetEasyScraper(BaseScraper):
    """
    StreetEasy.com property data scraper (NYC focus)
    
    Extracts:
    - Property details (beds, baths, sqft)
    - Listing price
    - Building amenities
    - Neighborhood data
    - Similar listings
    - NYC-specific data (borough, neighborhood)
    """
    
    BASE_URL = "https://streeteasy.com"
    
    async def search_property(self, address: str, city: str, state: str) -> Dict[str, Any]:
        """Search for a property on StreetEasy"""
        # Build search URL (StreetEasy is NYC-focused)
        search_address = f"{address} {city} NY".replace(' ', '+')
        search_url = f"{self.BASE_URL}/search?search_string={search_address}"
        
        try:
            self.log_scraping_result(True, f"Searching StreetEasy for {address}, {city}, {state}")
            
            if not self.client:
                raise Exception("Scraping client not initialized")
            
            # Tolerant fetch to handle non-2xx with body; transparent to pass target status
            resp = await self.client.fetch(
                search_url,
                wait_for='div[class*="listingCard"]',
                wait_timeout=30000,
                extra_params={
                    'transparent_status_code': 'true',
                    'stealth_proxy': 'true',
                    'premium_proxy': None,
                    'block_resources': 'false'
                },
                allow_failure=True
            )
            html = (resp.text or '')
            soup = self.parse_html(html)
            property_data = self._parse_search_results(soup)
            
            if property_data:
                self.log_scraping_result(True, "Found property on StreetEasy")
                return self.normalize_property_data(property_data)
            else:
                raise Exception("Property not found")
        
        except Exception as e:
            self.log_scraping_result(False, f"Search failed: {str(e)}")
            return self._empty_property_data()
    
    async def get_property_details(self, property_url: str) -> Dict[str, Any]:
        """Get detailed property information from StreetEasy listing page"""
        try:
            self.log_scraping_result(True, f"Fetching details from {property_url}")
            
            if not self.client:
                raise Exception("Scraping client not initialized")
            
            resp = await self.client.fetch(
                property_url,
                wait_for='div[class*="DetailsPage"]',
                wait_timeout=30000,
                extra_params={
                    'transparent_status_code': 'true',
                    'stealth_proxy': 'true',
                    'premium_proxy': None,
                    'block_resources': 'false'
                },
                allow_failure=True
            )
            html = (resp.text or '')
            soup = self.parse_html(html)
            property_data = self._parse_property_details(soup)
            property_data['listing_url'] = property_url
            
            self.log_scraping_result(True, "Property details fetched successfully")
            return self.normalize_property_data(property_data)
        
        except Exception as e:
            self.log_scraping_result(False, f"Failed to fetch details: {str(e)}")
            return self._empty_property_data()
    
    def _parse_search_results(self, soup) -> Dict[str, Any]:
        """Parse property data from StreetEasy search results"""
        try:
            # Find listing card
            listing_card = soup.find('div', class_=lambda x: x and 'listingCard' in x)
            if not listing_card:
                return {}
            
            # Extract basic info
            price = listing_card.find('span', class_=lambda x: x and 'price' in x.lower())
            address = listing_card.find('a', class_=lambda x: x and 'address' in x.lower())
            
            # Extract beds/baths
            details = listing_card.find_all('span', class_=lambda x: x and 'detail' in x.lower())
            beds, baths = None, None
            for detail in details:
                text = detail.text.lower()
                if 'bed' in text:
                    beds = detail.text
                elif 'bath' in text:
                    baths = detail.text
            
            return {
                'price': price.text if price else None,
                'address': address.text if address else None,
                'bedrooms': beds,
                'bathrooms': baths
            }
        
        except Exception as e:
            logger.error(f"Failed to parse StreetEasy search results: {e}")
            return {}
    
    def _parse_property_details(self, soup) -> Dict[str, Any]:
        """Parse detailed property data from StreetEasy listing page"""
        try:
            data = {}
            
            # Building amenities
            amenities_section = soup.find('div', class_=lambda x: x and 'amenities' in x.lower())
            if amenities_section:
                amenities = [
                    a.text.strip()
                    for a in amenities_section.find_all('li')
                ]
                data['amenities'] = amenities
            
            # Neighborhood
            neighborhood = soup.find('a', class_=lambda x: x and 'neighborhood' in x.lower())
            if neighborhood:
                data['neighborhood'] = neighborhood.text
            
            return data
        
        except Exception as e:
            logger.error(f"Failed to parse StreetEasy property details: {e}")
            return {}
    
    def _empty_property_data(self) -> Dict[str, Any]:
        """Return empty property data structure"""
        return self.normalize_property_data({
            'source': 'StreetEasy',
            'address': None
        })
