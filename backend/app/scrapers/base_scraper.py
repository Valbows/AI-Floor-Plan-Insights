"""
Base Scraper Class
Common functionality for all real estate website scrapers
"""

import re
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for real estate scrapers
    
    Provides common functionality:
    - HTML parsing with BeautifulSoup
    - Data normalization
    - Error handling
    - Logging
    """
    
    def __init__(self, brightdata_client=None):
        """
        Initialize base scraper
        
        Args:
            brightdata_client: BrightDataClient instance (optional)
        """
        self.client = brightdata_client
        self.source_name = self.__class__.__name__.replace('Scraper', '')
    
    @abstractmethod
    async def search_property(self, address: str, city: str, state: str) -> Dict[str, Any]:
        """
        Search for a property by address
        
        Args:
            address: Street address
            city: City name
            state: State abbreviation
        
        Returns:
            Property data dictionary
        """
        pass
    
    @abstractmethod
    async def get_property_details(self, property_url: str) -> Dict[str, Any]:
        """
        Get detailed property information
        
        Args:
            property_url: Property listing URL
        
        Returns:
            Detailed property data
        """
        pass
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content with BeautifulSoup
        
        Args:
            html: HTML string
        
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'lxml')
    
    def clean_text(self, text: Optional[str]) -> Optional[str]:
        """
        Clean and normalize text
        
        Args:
            text: Raw text string
        
        Returns:
            Cleaned text or None
        """
        if not text:
            return None
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text if text else None
    
    def parse_price(self, price_str: Optional[str]) -> Optional[int]:
        """
        Parse price string to integer
        
        Args:
            price_str: Price string (e.g., "$450,000", "$2.5M")
        
        Returns:
            Price as integer or None
        """
        if not price_str:
            return None
        
        try:
            # Remove currency symbols and commas
            price_str = re.sub(r'[$,]', '', str(price_str))
            
            # Handle millions/thousands notation
            if 'M' in price_str.upper():
                price_str = price_str.upper().replace('M', '')
                return int(float(price_str) * 1_000_000)
            elif 'K' in price_str.upper():
                price_str = price_str.upper().replace('K', '')
                return int(float(price_str) * 1_000)
            else:
                return int(float(price_str))
        
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse price: {price_str}")
            return None
    
    def parse_bedrooms(self, bed_str: Optional[str]) -> Optional[int]:
        """
        Parse bedrooms string to integer
        
        Args:
            bed_str: Bedrooms string (e.g., "3 bd", "3")
        
        Returns:
            Number of bedrooms or None
        """
        if not bed_str:
            return None
        
        try:
            # Extract first number
            match = re.search(r'(\d+)', str(bed_str))
            if match:
                return int(match.group(1))
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def parse_bathrooms(self, bath_str: Optional[str]) -> Optional[float]:
        """
        Parse bathrooms string to float
        
        Args:
            bath_str: Bathrooms string (e.g., "2.5 ba", "2")
        
        Returns:
            Number of bathrooms or None
        """
        if not bath_str:
            return None
        
        try:
            # Extract number (int or float)
            match = re.search(r'(\d+\.?\d*)', str(bath_str))
            if match:
                return float(match.group(1))
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def parse_sqft(self, sqft_str: Optional[str]) -> Optional[int]:
        """
        Parse square footage string to integer
        
        Args:
            sqft_str: Square footage string (e.g., "1,500 sqft", "1500")
        
        Returns:
            Square footage or None
        """
        if not sqft_str:
            return None
        
        try:
            # Remove commas and extract number
            sqft_str = re.sub(r'[,\s]', '', str(sqft_str))
            match = re.search(r'(\d+)', sqft_str)
            if match:
                return int(match.group(1))
        except (ValueError, AttributeError):
            pass
        
        return None
    
    def normalize_property_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize property data to standard format
        
        Args:
            raw_data: Raw scraped data
        
        Returns:
            Normalized property data
        """
        return {
            'source': self.source_name,
            'address': raw_data.get('address'),
            'city': raw_data.get('city'),
            'state': raw_data.get('state'),
            'zip_code': raw_data.get('zip_code'),
            'price': self.parse_price(raw_data.get('price')),
            'bedrooms': self.parse_bedrooms(raw_data.get('bedrooms')),
            'bathrooms': self.parse_bathrooms(raw_data.get('bathrooms')),
            'square_feet': self.parse_sqft(raw_data.get('square_feet')),
            'property_type': raw_data.get('property_type'),
            'year_built': raw_data.get('year_built'),
            'lot_size': raw_data.get('lot_size'),
            'listing_url': raw_data.get('listing_url'),
            'image_url': raw_data.get('image_url'),
            'description': self.clean_text(raw_data.get('description')),
            'amenities': raw_data.get('amenities', []),
            'price_history': raw_data.get('price_history', []),
            'comparable_properties': raw_data.get('comparable_properties', []),
            'raw_data': raw_data  # Keep original data
        }
    
    def log_scraping_result(self, success: bool, message: str):
        """
        Log scraping result
        
        Args:
            success: Whether scraping was successful
            message: Log message
        """
        if success:
            logger.info(f"✅ {self.source_name}: {message}")
        else:
            logger.error(f"❌ {self.source_name}: {message}")
