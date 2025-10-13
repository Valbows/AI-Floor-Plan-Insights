"""
Zillow Property Scraper
Scrapes property data from Zillow.com using Bright Data
"""

import re
import logging
from typing import Dict, Any, List, Optional
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class ZillowScraper(BaseScraper):
    """
    Zillow.com property data scraper
    
    Extracts:
    - Property details (beds, baths, sqft)
    - Zestimate (Zillow's price estimate)
    - Price history
    - Comparable properties
    - Rent estimate
    - Neighborhood data
    """
    
    BASE_URL = "https://www.zillow.com"
    
    async def search_property(self, address: str, city: str, state: str) -> Dict[str, Any]:
        """
        Search for a property on Zillow
        
        Args:
            address: Street address
            city: City name
            state: State abbreviation
        
        Returns:
            Property data dictionary
        """
        # Build search URL
        search_address = f"{address}, {city}, {state}".replace(' ', '-')
        search_url = f"{self.BASE_URL}/homes/{search_address}_rb/"
        
        try:
            self.log_scraping_result(True, f"Searching Zillow for {address}, {city}, {state}")
            
            # Use Bright Data to scrape the page
            if not self.client:
                raise Exception("Bright Data client not initialized")
            
            html = await self.client.scrape_page(
                search_url,
                wait_for='article[data-test="property-card"]',
                wait_timeout=30000
            )
            
            soup = self.parse_html(html)
            
            # Parse property data from search results
            property_data = self._parse_search_results(soup)
            
            if property_data:
                self.log_scraping_result(True, f"Found property on Zillow")
                return self.normalize_property_data(property_data)
            else:
                raise Exception("Property not found in search results")
        
        except Exception as e:
            self.log_scraping_result(False, f"Search failed: {str(e)}")
            return self._empty_property_data()
    
    async def get_property_details(self, property_url: str) -> Dict[str, Any]:
        """
        Get detailed property information from Zillow listing page
        
        Args:
            property_url: Zillow property URL
        
        Returns:
            Detailed property data
        """
        try:
            self.log_scraping_result(True, f"Fetching details from {property_url}")
            
            if not self.client:
                raise Exception("Bright Data client not initialized")
            
            html = await self.client.scrape_page(
                property_url,
                wait_for='div[data-test="home-details"]',
                wait_timeout=30000
            )
            
            soup = self.parse_html(html)
            
            # Parse detailed property data
            property_data = self._parse_property_details(soup)
            property_data['listing_url'] = property_url
            
            self.log_scraping_result(True, "Property details fetched successfully")
            return self.normalize_property_data(property_data)
        
        except Exception as e:
            self.log_scraping_result(False, f"Failed to fetch details: {str(e)}")
            return self._empty_property_data()
    
    def _parse_search_results(self, soup) -> Dict[str, Any]:
        """
        Parse property data from Zillow search results
        
        Args:
            soup: BeautifulSoup object
        
        Returns:
            Property data dictionary
        """
        try:
            # Find first property card
            property_card = soup.find('article', {'data-test': 'property-card'})
            if not property_card:
                return {}
            
            # Extract basic info
            price_elem = property_card.find('span', {'data-test': 'property-card-price'})
            address_elem = property_card.find('address', {'data-test': 'property-card-addr'})
            
            # Extract beds/baths/sqft
            details = property_card.find_all('li')
            beds, baths, sqft = None, None, None
            
            for detail in details:
                text = detail.text.lower()
                if 'bd' in text:
                    beds = detail.text
                elif 'ba' in text:
                    baths = detail.text
                elif 'sqft' in text:
                    sqft = detail.text
            
            # Get property URL
            link_elem = property_card.find('a', {'data-test': 'property-card-link'})
            listing_url = f"{self.BASE_URL}{link_elem['href']}" if link_elem else None
            
            return {
                'price': price_elem.text if price_elem else None,
                'address': address_elem.text if address_elem else None,
                'bedrooms': beds,
                'bathrooms': baths,
                'square_feet': sqft,
                'listing_url': listing_url
            }
        
        except Exception as e:
            logger.error(f"Failed to parse Zillow search results: {e}")
            return {}
    
    def _parse_property_details(self, soup) -> Dict[str, Any]:
        """
        Parse detailed property data from Zillow listing page
        
        Args:
            soup: BeautifulSoup object
        
        Returns:
            Detailed property data
        """
        try:
            data = {}
            
            # Zestimate
            zestimate_elem = soup.find('span', {'data-test': 'zestimate-text'})
            if zestimate_elem:
                data['zestimate'] = zestimate_elem.text
            
            # Price history
            price_history_section = soup.find('div', {'data-test': 'price-history'})
            if price_history_section:
                data['price_history'] = self._parse_price_history(price_history_section)
            
            # Rent estimate
            rent_elem = soup.find('span', {'data-test': 'rent-estimate'})
            if rent_elem:
                data['rent_estimate'] = rent_elem.text
            
            # Property details
            details_section = soup.find('div', {'data-test': 'home-details'})
            if details_section:
                data.update(self._parse_details_section(details_section))
            
            return data
        
        except Exception as e:
            logger.error(f"Failed to parse Zillow property details: {e}")
            return {}
    
    def _parse_price_history(self, price_history_section) -> List[Dict[str, Any]]:
        """Parse price history from Zillow"""
        history = []
        try:
            rows = price_history_section.find_all('tr')
            for row in rows[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) >= 3:
                    history.append({
                        'date': cols[0].text.strip(),
                        'event': cols[1].text.strip(),
                        'price': cols[2].text.strip()
                    })
        except Exception as e:
            logger.error(f"Failed to parse price history: {e}")
        
        return history
    
    def _parse_details_section(self, details_section) -> Dict[str, Any]:
        """Parse property details section"""
        details = {}
        try:
            # Find all detail rows
            rows = details_section.find_all('div', class_='Text-c11n-8-84-3__sc')
            for row in rows:
                text = row.text.strip()
                if ':' in text:
                    key, value = text.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    details[key] = value.strip()
        except Exception as e:
            logger.error(f"Failed to parse details section: {e}")
        
        return details
    
    def _empty_property_data(self) -> Dict[str, Any]:
        """Return empty property data structure"""
        return self.normalize_property_data({
            'source': 'Zillow',
            'address': None,
            'price': None,
            'bedrooms': None,
            'bathrooms': None,
            'square_feet': None
        })
