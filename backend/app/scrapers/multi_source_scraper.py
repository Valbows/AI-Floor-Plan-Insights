"""
Multi-Source Property Scraper
Coordinates scraping from Zillow, Redfin, and StreetEasy
Aggregates and normalizes data from multiple sources
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.clients.brightdata_client import BrightDataClient
from .zillow_scraper import ZillowScraper
from .redfin_scraper import RedfinScraper
from .streeteasy_scraper import StreetEasyScraper

logger = logging.getLogger(__name__)


class MultiSourceScraper:
    """
    Coordinate scraping from multiple real estate sources
    
    Features:
    - Parallel scraping from Zillow, Redfin, StreetEasy
    - Data aggregation and normalization
    - Consensus pricing from multiple sources
    - Error handling with fallbacks
    - Rate limiting awareness
    """
    
    def __init__(self, brightdata_api_key: Optional[str] = None):
        """
        Initialize multi-source scraper
        
        Args:
            brightdata_api_key: Bright Data API key (optional)
        """
        self.api_key = brightdata_api_key
        self.client = None
        
        # Initialize scrapers (will connect client when needed)
        self.zillow = None
        self.redfin = None
        self.streeteasy = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Connect to Bright Data and initialize scrapers"""
        try:
            logger.info("Initializing Multi-Source Scraper...")
            
            # Initialize Bright Data client
            self.client = BrightDataClient(api_key=self.api_key)
            await self.client.connect()
            
            # Initialize scrapers with shared client
            self.zillow = ZillowScraper(brightdata_client=self.client)
            self.redfin = RedfinScraper(brightdata_client=self.client)
            self.streeteasy = StreetEasyScraper(brightdata_client=self.client)
            
            logger.info("✅ Multi-Source Scraper initialized")
        
        except Exception as e:
            logger.error(f"Failed to initialize scrapers: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Bright Data"""
        if self.client:
            await self.client.close()
            self.client = None
    
    async def scrape_property(self, address: str, city: str, state: str) -> Dict[str, Any]:
        """
        Scrape property data from all sources
        
        Args:
            address: Street address
            city: City name
            state: State abbreviation
        
        Returns:
            Aggregated property data from all sources
        """
        logger.info(f"Starting multi-source scrape for {address}, {city}, {state}")
        
        # Run all scrapers in parallel
        tasks = [
            self._safe_scrape(self.zillow.search_property, address, city, state, "Zillow"),
            self._safe_scrape(self.redfin.search_property, address, city, state, "Redfin"),
            self._safe_scrape(self.streeteasy.search_property, address, city, state, "StreetEasy")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        zillow_data, redfin_data, streeteasy_data = results
        
        # Aggregate data
        aggregated = self._aggregate_property_data(
            zillow_data if not isinstance(zillow_data, Exception) else None,
            redfin_data if not isinstance(redfin_data, Exception) else None,
            streeteasy_data if not isinstance(streeteasy_data, Exception) else None
        )
        
        logger.info(f"✅ Multi-source scrape complete. Sources: {aggregated['sources_count']}")
        
        return aggregated
    
    async def _safe_scrape(self, scrape_func, address: str, city: str, state: str, source_name: str) -> Optional[Dict[str, Any]]:
        """
        Safely execute scraping function with error handling
        
        Args:
            scrape_func: Scraping function to execute
            address: Street address
            city: City name
            state: State abbreviation
            source_name: Name of the source (for logging)
        
        Returns:
            Scraped data or None if failed
        """
        try:
            return await scrape_func(address, city, state)
        except Exception as e:
            logger.warning(f"{source_name} scraping failed: {str(e)}")
            return None
    
    def _aggregate_property_data(self, zillow: Optional[Dict], redfin: Optional[Dict], 
                                 streeteasy: Optional[Dict]) -> Dict[str, Any]:
        """
        Aggregate data from multiple sources
        
        Args:
            zillow: Zillow property data
            redfin: Redfin property data
            streeteasy: StreetEasy property data
        
        Returns:
            Aggregated property data with consensus values
        """
        sources = []
        if zillow and zillow.get('price'):
            sources.append(zillow)
        if redfin and redfin.get('price'):
            sources.append(redfin)
        if streeteasy and streeteasy.get('price'):
            sources.append(streeteasy)
        
        if not sources:
            logger.warning("No valid data from any source")
            return self._empty_aggregated_data()
        
        # Calculate consensus values
        prices = [s['price'] for s in sources if s.get('price')]
        sqfts = [s['square_feet'] for s in sources if s.get('square_feet')]
        
        aggregated = {
            'address': self._get_consensus_value([s.get('address') for s in sources]),
            'city': self._get_consensus_value([s.get('city') for s in sources]),
            'state': self._get_consensus_value([s.get('state') for s in sources]),
            'zip_code': self._get_consensus_value([s.get('zip_code') for s in sources]),
            
            # Consensus pricing
            'price_consensus': self._calculate_median(prices) if prices else None,
            'price_low': min(prices) if prices else None,
            'price_high': max(prices) if prices else None,
            'price_average': sum(prices) // len(prices) if prices else None,
            
            # Property details (consensus or first available)
            'bedrooms': self._get_consensus_value([s.get('bedrooms') for s in sources]),
            'bathrooms': self._get_consensus_value([s.get('bathrooms') for s in sources]),
            'square_feet': self._calculate_median(sqfts) if sqfts else None,
            'property_type': self._get_consensus_value([s.get('property_type') for s in sources]),
            'year_built': self._get_consensus_value([s.get('year_built') for s in sources]),
            
            # Source data
            'sources': {
                'zillow': zillow,
                'redfin': redfin,
                'streeteasy': streeteasy
            },
            'sources_count': len(sources),
            'sources_available': [s.get('source') for s in sources],
            
            # Metadata
            'scraped_at': datetime.utcnow().isoformat(),
            'data_quality_score': self._calculate_quality_score(sources)
        }
        
        return aggregated
    
    def _get_consensus_value(self, values: List[Any]) -> Any:
        """
        Get consensus value from list (most common non-None value)
        
        Args:
            values: List of values
        
        Returns:
            Consensus value or None
        """
        # Filter out None values
        valid_values = [v for v in values if v is not None]
        
        if not valid_values:
            return None
        
        # Return most common value
        return max(set(valid_values), key=valid_values.count)
    
    def _calculate_median(self, values: List[float]) -> Optional[float]:
        """Calculate median of values"""
        if not values:
            return None
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]
    
    def _calculate_quality_score(self, sources: List[Dict]) -> int:
        """
        Calculate data quality score (0-100)
        
        Args:
            sources: List of source data dictionaries
        
        Returns:
            Quality score
        """
        score = 0
        
        # Base score for number of sources
        score += len(sources) * 20  # 20 points per source (max 60)
        
        # Points for data completeness
        required_fields = ['price', 'bedrooms', 'bathrooms', 'square_feet']
        for source in sources:
            complete_fields = sum(1 for field in required_fields if source.get(field))
            score += (complete_fields / len(required_fields)) * (40 / len(sources))
        
        return min(int(score), 100)
    
    def _empty_aggregated_data(self) -> Dict[str, Any]:
        """Return empty aggregated data structure"""
        return {
            'address': None,
            'price_consensus': None,
            'sources_count': 0,
            'sources_available': [],
            'data_quality_score': 0,
            'scraped_at': datetime.utcnow().isoformat()
        }
