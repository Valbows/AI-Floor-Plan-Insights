"""
Unit tests for Market Insights Analyst (Agent #2) - Refactored Version
Tests ATTOM API integration and multi-source web scraping
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from app.agents.market_insights_analyst import (
    MarketInsightsAnalyst,
    search_property_data,
    get_comparable_properties,
    get_avm_estimate,
    scrape_property_data,
    PriceEstimate,
    MarketTrend,
    InvestmentAnalysis,
    MarketInsights
)


@pytest.fixture
def mock_attom_property_data():
    """Mock ATTOM property data"""
    return {
        'attom_id': '123456789',
        'address': '123 MAIN ST',
        'city': 'LOS ANGELES',
        'state': 'CA',
        'zip': '90001',
        'bedrooms': 3,
        'bathrooms': 2.0,
        'square_feet': 1500,
        'year_built': 2010,
        'last_sale_price': 350000,
        'assessed_value': 320000
    }


@pytest.fixture
def mock_attom_avm_data():
    """Mock ATTOM AVM data"""
    return {
        'estimated_value': 425000,
        'confidence_score': 85.0,
        'value_range_low': 400000,
        'value_range_high': 450000,
        'fsd': 0.05,
        'as_of_date': '2025-10-13'
    }


@pytest.fixture
def mock_scraped_data():
    """Mock web scraping data"""
    return {
        'price_consensus': 455000,
        'price_low': 450000,
        'price_high': 460000,
        'price_average': 455000,
        'bedrooms': 3,
        'bathrooms': 2.0,
        'square_feet': 1500,
        'sources_count': 3,
        'sources_available': ['Zillow', 'Redfin', 'StreetEasy'],
        'data_quality_score': 95,
        'sources': {
            'zillow': {'price': 450000},
            'redfin': {'price': 460000},
            'streeteasy': {'price': 455000}
        }
    }


@pytest.fixture
def property_data():
    """Mock floor plan data"""
    return {
        'bedrooms': 3,
        'bathrooms': 2.0,
        'square_footage': 1500,
        'layout_type': 'Traditional',
        'features': ['Hardwood Floors', 'Updated Kitchen', 'In-Unit Laundry']
    }


class TestATTOMAPITools:
    """Test suite for ATTOM API CrewAI tools"""
    
    @patch('app.agents.market_insights_analyst.AttomAPIClient')
    def test_search_property_data_success(self, mock_attom_class, mock_attom_property_data):
        """Test ATTOM property search tool"""
        mock_client = Mock()
        mock_client.search_property.return_value = mock_attom_property_data
        mock_attom_class.return_value = mock_client
        
        # Call the underlying function (tools are CrewAI Tool objects)
        result = search_property_data.func('123 Main St', 'Los Angeles', 'CA')
        
        # Should return JSON string
        assert isinstance(result, str)
        data = json.loads(result)
        assert data['attom_id'] == '123456789'
        assert data['bedrooms'] == 3
        assert data['square_feet'] == 1500
    
    @patch('app.agents.market_insights_analyst.AttomAPIClient')
    def test_search_property_data_error(self, mock_attom_class):
        """Test ATTOM property search tool error handling"""
        mock_client = Mock()
        mock_client.search_property.side_effect = Exception("API Error")
        mock_attom_class.return_value = mock_client
        
        result = search_property_data.func('Invalid', 'Address', 'XX')
        
        assert "Error fetching property data" in result
    
    @patch('app.agents.market_insights_analyst.AttomAPIClient')
    def test_get_avm_estimate_success(self, mock_attom_class, mock_attom_avm_data):
        """Test ATTOM AVM tool"""
        mock_client = Mock()
        mock_client.get_avm.return_value = mock_attom_avm_data
        mock_attom_class.return_value = mock_client
        
        result = get_avm_estimate.func('123 Main St', 'Los Angeles', 'CA', '90001')
        
        data = json.loads(result)
        assert data['estimated_value'] == 425000
        assert data['confidence_score'] == 85.0
    
    @patch('app.agents.market_insights_analyst.AttomAPIClient')
    def test_get_comparable_properties(self, mock_attom_class):
        """Test ATTOM comparables tool"""
        mock_client = Mock()
        mock_client.get_comparables.return_value = [
            {'address': 'Comp 1', 'last_sale_price': 440000},
            {'address': 'Comp 2', 'last_sale_price': 460000}
        ]
        mock_attom_class.return_value = mock_client
        
        result = get_comparable_properties.func('123 Main St', 'Los Angeles', 'CA', 0.5)
        
        data = json.loads(result)
        assert len(data) == 2
        assert data[0]['last_sale_price'] == 440000


class TestMultiSourceScrapingTool:
    """Test suite for Multi-Source Property Scraping tool"""
    
    @patch('app.scrapers.multi_source_scraper.MultiSourceScraper')
    @patch('app.agents.market_insights_analyst.asyncio')
    def test_scrape_property_data_success(self, mock_asyncio, mock_scraper_class, mock_scraped_data):
        """Test multi-source scraping tool"""
        # Mock asyncio loop
        mock_loop = Mock()
        mock_asyncio.new_event_loop.return_value = mock_loop
        mock_asyncio.set_event_loop = Mock()
        mock_loop.run_until_complete.return_value = mock_scraped_data
        mock_loop.close = Mock()
        
        result = scrape_property_data.func('123 Main St', 'Los Angeles', 'CA')
        
        # Should return JSON string
        assert isinstance(result, str)
        data = json.loads(result)
        assert data['price_consensus'] == 455000
        assert data['sources_count'] == 3
        assert data['data_quality_score'] == 95
    
    @patch('app.scrapers.multi_source_scraper.MultiSourceScraper')
    @patch('app.agents.market_insights_analyst.asyncio')
    def test_scrape_property_data_error(self, mock_asyncio, mock_scraper_class):
        """Test scraping tool error handling"""
        mock_loop = Mock()
        mock_asyncio.new_event_loop.return_value = mock_loop
        mock_loop.run_until_complete.side_effect = Exception("Scraping failed")
        
        result = scrape_property_data.func('123 Main St', 'Los Angeles', 'CA')
        
        assert "Web scraping unavailable" in result


class TestMarketInsightsAnalyst:
    """Test suite for Market Insights Analyst agent"""
    
    @patch.dict('os.environ', {'ATTOM_API_KEY': 'test_key', 'GEMINI_API_KEY': 'test_key'})
    def test_initialization(self):
        """Test analyst initializes with ATTOM client"""
        with patch('app.agents.market_insights_analyst.AttomAPIClient'):
            analyst = MarketInsightsAnalyst()
            
            assert analyst.attom is not None
            assert analyst.role == "Senior Real Estate Market Analyst"
            assert analyst.agent is not None
            assert len(analyst.agent.tools) >= 4  # ATTOM + Scraping tools
    
    @patch.dict('os.environ', {'ATTOM_API_KEY': 'test_key', 'GEMINI_API_KEY': 'test_key', 'TAVILY_API_KEY': 'test_key'})
    def test_initialization_with_tavily(self):
        """Test analyst includes Tavily when API key present"""
        with patch('app.agents.market_insights_analyst.AttomAPIClient'):
            analyst = MarketInsightsAnalyst()
            
            # Should have 5 tools: ATTOM search, comparables, AVM, scraping, and Tavily
            assert len(analyst.agent.tools) == 5
    
    def test_sanitize_market_data(self):
        """Test data sanitization"""
        with patch.dict('os.environ', {'ATTOM_API_KEY': 'test_key', 'GEMINI_API_KEY': 'test_key'}):
            with patch('app.agents.market_insights_analyst.AttomAPIClient'):
                analyst = MarketInsightsAnalyst()
        
        # Test numeric string conversion
        data = {
            'price_estimate': {
                'estimated_value': '$450,000',
                'value_range_low': '400000',
                'value_range_high': '500,000'
            },
            'market_trend': {
                'appreciation_rate': '3.5%',
                'days_on_market_avg': '45 days'
            },
            'investment_analysis': {
                'estimated_rental_income': '$2,500',
                'cap_rate': '5.5%'
            }
        }
        
        sanitized = analyst._sanitize_market_data(data)
        
        # Check conversions
        assert sanitized['market_trend']['appreciation_rate'] == 3.5
        assert sanitized['market_trend']['days_on_market_avg'] == 45
        assert sanitized['investment_analysis']['estimated_rental_income'] == 2500
        assert sanitized['investment_analysis']['cap_rate'] == 5.5
    
    def test_sanitize_market_data_handles_none(self):
        """Test sanitization handles None and invalid values"""
        with patch.dict('os.environ', {'ATTOM_API_KEY': 'test_key', 'GEMINI_API_KEY': 'test_key'}):
            with patch('app.agents.market_insights_analyst.AttomAPIClient'):
                analyst = MarketInsightsAnalyst()
        
        data = {
            'price_estimate': {
                'estimated_value': None,
                'value_range_low': 'Unknown',
                'value_range_high': 'N/A'
            },
            'market_trend': {
                'appreciation_rate': 'Undeterminable',
                'days_on_market_avg': None
            },
            'investment_analysis': {
                'estimated_rental_income': None,
                'cap_rate': 'null'
            }
        }
        
        sanitized = analyst._sanitize_market_data(data)
        
        # Should handle gracefully
        assert sanitized['price_estimate']['estimated_value'] == 0  # Defaults to 0
        assert sanitized['market_trend']['appreciation_rate'] is None
        assert sanitized['investment_analysis']['cap_rate'] is None
    
    def test_generate_fallback_insights(self, property_data):
        """Test fallback insights generation"""
        with patch.dict('os.environ', {'ATTOM_API_KEY': 'test_key', 'GEMINI_API_KEY': 'test_key'}):
            with patch('app.agents.market_insights_analyst.AttomAPIClient'):
                analyst = MarketInsightsAnalyst()
        
        result = analyst._generate_fallback_insights(property_data, "API unavailable")
        
        # Should return valid MarketInsights structure
        assert 'price_estimate' in result
        assert 'market_trend' in result
        assert 'investment_analysis' in result
        assert result['price_estimate']['estimated_value'] == 300000  # 1500 sqft * $200
        assert result['price_estimate']['confidence'] == 'low'
        assert 'unavailable' in result['price_estimate']['reasoning'].lower()


class TestPydanticSchemas:
    """Test suite for Pydantic data models"""
    
    def test_price_estimate_schema(self):
        """Test PriceEstimate schema validation"""
        data = {
            'estimated_value': 450000,
            'confidence': 'high',
            'value_range_low': 425000,
            'value_range_high': 475000,
            'reasoning': 'Based on comparable sales'
        }
        
        price_estimate = PriceEstimate(**data)
        assert price_estimate.estimated_value == 450000
        assert price_estimate.confidence == 'high'
    
    def test_market_trend_schema(self):
        """Test MarketTrend schema validation"""
        data = {
            'trend_direction': 'rising',
            'appreciation_rate': 3.5,
            'days_on_market_avg': 45,
            'inventory_level': 'balanced',
            'buyer_demand': 'high',
            'insights': 'Strong market conditions'
        }
        
        trend = MarketTrend(**data)
        assert trend.trend_direction == 'rising'
        assert trend.appreciation_rate == 3.5
    
    def test_investment_analysis_schema(self):
        """Test InvestmentAnalysis schema validation"""
        data = {
            'investment_score': 85,
            'rental_potential': 'excellent',
            'estimated_rental_income': 2500,
            'cap_rate': 5.5,
            'appreciation_potential': 'high',
            'risk_factors': ['Market volatility', 'Interest rates'],
            'opportunities': ['Strong rental demand', 'Neighborhood growth']
        }
        
        analysis = InvestmentAnalysis(**data)
        assert analysis.investment_score == 85
        assert len(analysis.risk_factors) == 2
        assert len(analysis.opportunities) == 2
    
    def test_market_insights_complete_schema(self):
        """Test complete MarketInsights schema"""
        data = {
            'price_estimate': {
                'estimated_value': 450000,
                'confidence': 'high',
                'value_range_low': 425000,
                'value_range_high': 475000,
                'reasoning': 'Strong comps'
            },
            'market_trend': {
                'trend_direction': 'rising',
                'appreciation_rate': 3.5,
                'days_on_market_avg': 45,
                'inventory_level': 'balanced',
                'buyer_demand': 'high',
                'insights': 'Strong market'
            },
            'investment_analysis': {
                'investment_score': 85,
                'rental_potential': 'excellent',
                'estimated_rental_income': 2500,
                'cap_rate': 5.5,
                'appreciation_potential': 'high',
                'risk_factors': ['Market volatility'],
                'opportunities': ['Growth potential']
            },
            'comparable_properties': [],
            'summary': 'Excellent investment opportunity'
        }
        
        insights = MarketInsights(**data)
        assert insights.price_estimate.estimated_value == 450000
        assert insights.market_trend.trend_direction == 'rising'
        assert insights.investment_analysis.investment_score == 85
        assert insights.summary == 'Excellent investment opportunity'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
