"""
Unit tests for Web Scrapers
Tests Zillow, Redfin, StreetEasy, and MultiSourceScraper
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.zillow_scraper import ZillowScraper
from app.scrapers.redfin_scraper import RedfinScraper
from app.scrapers.streeteasy_scraper import StreetEasyScraper
from app.scrapers.multi_source_scraper import MultiSourceScraper


class TestBaseScraper:
    """Test suite for BaseScraper"""
    
    def test_clean_text(self):
        """Test text cleaning"""
        scraper = ZillowScraper()  # Use concrete implementation
        
        assert scraper.clean_text("  Hello   World  ") == "Hello World"
        assert scraper.clean_text("\n\nTest\n\n") == "Test"
        assert scraper.clean_text("") is None
        assert scraper.clean_text(None) is None
    
    def test_parse_price(self):
        """Test price parsing"""
        scraper = ZillowScraper()
        
        assert scraper.parse_price("$450,000") == 450000
        assert scraper.parse_price("$2.5M") == 2500000
        assert scraper.parse_price("$750K") == 750000
        assert scraper.parse_price("$1,234,567") == 1234567
        assert scraper.parse_price(None) is None
        assert scraper.parse_price("N/A") is None
    
    def test_parse_bedrooms(self):
        """Test bedrooms parsing"""
        scraper = ZillowScraper()
        
        assert scraper.parse_bedrooms("3 bd") == 3
        assert scraper.parse_bedrooms("3") == 3
        assert scraper.parse_bedrooms("Studio") is None
        assert scraper.parse_bedrooms(None) is None
    
    def test_parse_bathrooms(self):
        """Test bathrooms parsing"""
        scraper = ZillowScraper()
        
        assert scraper.parse_bathrooms("2.5 ba") == 2.5
        assert scraper.parse_bathrooms("2") == 2.0
        assert scraper.parse_bathrooms("3.0") == 3.0
        assert scraper.parse_bathrooms(None) is None
    
    def test_parse_sqft(self):
        """Test square footage parsing"""
        scraper = ZillowScraper()
        
        assert scraper.parse_sqft("1,500 sqft") == 1500
        assert scraper.parse_sqft("1500") == 1500
        assert scraper.parse_sqft("2,345 sq ft") == 2345
        assert scraper.parse_sqft(None) is None
    
    def test_normalize_property_data(self):
        """Test data normalization"""
        scraper = ZillowScraper()
        
        raw_data = {
            'address': '123 Main St',
            'price': '$450,000',
            'bedrooms': '3 bd',
            'bathrooms': '2.5 ba',
            'square_feet': '1,500 sqft',
            'listing_url': 'https://zillow.com/...'
        }
        
        normalized = scraper.normalize_property_data(raw_data)
        
        assert normalized['source'] == 'Zillow'
        assert normalized['address'] == '123 Main St'
        assert normalized['price'] == 450000
        assert normalized['bedrooms'] == 3
        assert normalized['bathrooms'] == 2.5
        assert normalized['square_feet'] == 1500


class TestZillowScraper:
    """Test suite for ZillowScraper"""
    
    @pytest.mark.asyncio
    async def test_search_property_success(self):
        """Test successful Zillow property search"""
        mock_client = AsyncMock()
        mock_html = """
        <article data-test="property-card">
            <span data-test="property-card-price">$450,000</span>
            <address data-test="property-card-addr">123 Main St, Los Angeles, CA 90001</address>
            <ul>
                <li>3 bd</li>
                <li>2 ba</li>
                <li>1,500 sqft</li>
            </ul>
            <a data-test="property-card-link" href="/homedetails/123-main-st/123456_zpid/"></a>
        </article>
        """
        mock_client.scrape_page.return_value = mock_html
        
        scraper = ZillowScraper(brightdata_client=mock_client)
        result = await scraper.search_property('123 Main St', 'Los Angeles', 'CA')
        
        assert result['price'] == 450000
        assert result['bedrooms'] == 3
        assert result['bathrooms'] == 2.0
        assert result['square_feet'] == 1500
    
    @pytest.mark.asyncio
    async def test_search_property_not_found(self):
        """Test Zillow search when property not found"""
        mock_client = AsyncMock()
        mock_client.scrape_page.return_value = "<html><body>No results</body></html>"
        
        scraper = ZillowScraper(brightdata_client=mock_client)
        result = await scraper.search_property('999 Fake St', 'Nowhere', 'XX')
        
        # Should return empty data
        assert result['price'] is None


class TestRedfinScraper:
    """Test suite for RedfinScraper"""
    
    @pytest.mark.asyncio
    async def test_search_property_success(self):
        """Test successful Redfin property search"""
        mock_client = AsyncMock()
        mock_html = """
        <div class="HomeCard">
            <span class="price">$460,000</span>
            <div class="address">123 Main St, Los Angeles, CA</div>
        </div>
        """
        mock_client.scrape_page.return_value = mock_html
        
        scraper = RedfinScraper(brightdata_client=mock_client)
        result = await scraper.search_property('123 Main St', 'Los Angeles', 'CA')
        
        assert result['source'] == 'Redfin'
        assert 'address' in result


class TestStreetEasyScraper:
    """Test suite for StreetEasyScraper"""
    
    @pytest.mark.asyncio
    async def test_search_property_success(self):
        """Test successful StreetEasy property search"""
        mock_client = AsyncMock()
        mock_html = """
        <div class="listingCard">
            <span class="price">$750,000</span>
            <a class="address">123 Main St, New York, NY</a>
            <span class="detail">2 bed</span>
            <span class="detail">1 bath</span>
        </div>
        """
        mock_client.scrape_page.return_value = mock_html
        
        scraper = StreetEasyScraper(brightdata_client=mock_client)
        result = await scraper.search_property('123 Main St', 'New York', 'NY')
        
        assert result['source'] == 'StreetEasy'


class TestMultiSourceScraper:
    """Test suite for MultiSourceScraper"""
    
    @pytest.mark.asyncio
    async def test_scrape_property_all_sources_success(self):
        """Test scraping from all sources successfully"""
        mock_client = AsyncMock()
        
        scraper = MultiSourceScraper()
        scraper.client = mock_client
        
        # Mock individual scrapers
        scraper.zillow = AsyncMock()
        scraper.redfin = AsyncMock()
        scraper.streeteasy = AsyncMock()
        
        # Mock responses
        scraper.zillow.search_property.return_value = {
            'source': 'Zillow',
            'price': 450000,
            'bedrooms': 3,
            'bathrooms': 2.0,
            'square_feet': 1500,
            'address': '123 Main St'
        }
        
        scraper.redfin.search_property.return_value = {
            'source': 'Redfin',
            'price': 460000,
            'bedrooms': 3,
            'bathrooms': 2.0,
            'square_feet': 1500,
            'address': '123 Main St'
        }
        
        scraper.streeteasy.search_property.return_value = {
            'source': 'StreetEasy',
            'price': 455000,
            'bedrooms': 3,
            'bathrooms': 2.0,
            'square_feet': 1500,
            'address': '123 Main St'
        }
        
        result = await scraper.scrape_property('123 Main St', 'New York', 'NY')
        
        # Check consensus pricing
        assert result['sources_count'] == 3
        assert result['price_consensus'] == 455000  # Median
        assert result['price_low'] == 450000
        assert result['price_high'] == 460000
        assert result['price_average'] == 455000  # (450k + 460k + 455k) / 3
        assert result['data_quality_score'] > 0
        assert len(result['sources_available']) == 3
    
    @pytest.mark.asyncio
    async def test_scrape_property_partial_success(self):
        """Test scraping when only some sources succeed"""
        mock_client = AsyncMock()
        
        scraper = MultiSourceScraper()
        scraper.client = mock_client
        
        # Mock individual scrapers
        scraper.zillow = AsyncMock()
        scraper.redfin = AsyncMock()
        scraper.streeteasy = AsyncMock()
        
        # Zillow succeeds
        scraper.zillow.search_property.return_value = {
            'source': 'Zillow',
            'price': 450000,
            'bedrooms': 3,
            'bathrooms': 2.0,
            'square_feet': 1500
        }
        
        # Redfin fails
        scraper.redfin.search_property.side_effect = Exception("Scraping failed")
        
        # StreetEasy returns no data
        scraper.streeteasy.search_property.return_value = {
            'source': 'StreetEasy',
            'price': None
        }
        
        result = await scraper.scrape_property('123 Main St', 'Los Angeles', 'CA')
        
        # Should have 1 valid source
        assert result['sources_count'] == 1
        assert result['price_consensus'] == 450000
        assert 'Zillow' in result['sources_available']
    
    def test_calculate_median(self):
        """Test median calculation"""
        scraper = MultiSourceScraper()
        
        # Odd number of values
        assert scraper._calculate_median([1, 2, 3, 4, 5]) == 3
        
        # Even number of values
        assert scraper._calculate_median([1, 2, 3, 4]) == 2.5
        
        # Single value
        assert scraper._calculate_median([100]) == 100
        
        # Empty list
        assert scraper._calculate_median([]) is None
    
    def test_get_consensus_value(self):
        """Test consensus value selection"""
        scraper = MultiSourceScraper()
        
        # Most common value
        assert scraper._get_consensus_value([1, 2, 2, 3]) == 2
        
        # All same
        assert scraper._get_consensus_value([5, 5, 5]) == 5
        
        # All None
        assert scraper._get_consensus_value([None, None]) is None
        
        # Mixed with None
        assert scraper._get_consensus_value([1, None, 1, None]) == 1
    
    def test_calculate_quality_score(self):
        """Test data quality scoring"""
        scraper = MultiSourceScraper()
        
        # Complete data from 3 sources
        sources = [
            {'price': 450000, 'bedrooms': 3, 'bathrooms': 2.0, 'square_feet': 1500},
            {'price': 460000, 'bedrooms': 3, 'bathrooms': 2.0, 'square_feet': 1500},
            {'price': 455000, 'bedrooms': 3, 'bathrooms': 2.0, 'square_feet': 1500}
        ]
        score = scraper._calculate_quality_score(sources)
        assert score >= 99  # 3 sources (60) + complete data (40), allowing for rounding
        
        # Incomplete data
        sources = [
            {'price': 450000, 'bedrooms': None, 'bathrooms': None, 'square_feet': None}
        ]
        score = scraper._calculate_quality_score(sources)
        assert score == 30  # 1 source (20) + 25% complete (10)
        
        # No sources
        score = scraper._calculate_quality_score([])
        assert score == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
