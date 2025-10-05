"""
Unit Tests for CoreLogic API Client
Uses mocked responses to test without hitting real API
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.clients.corelogic_client import CoreLogicClient


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables"""
    monkeypatch.setenv('CORELOGIC_CONSUMER_KEY', 'test_key')
    monkeypatch.setenv('CORELOGIC_CONSUMER_SECRET', 'test_secret')


@pytest.fixture
def client(mock_env):
    """Create CoreLogic client with mocked credentials"""
    return CoreLogicClient()


@pytest.fixture
def mock_token_response():
    """Mock OAuth token response"""
    return {
        'access_token': 'mock_access_token_12345',
        'expires_in': 3600,
        'token_type': 'Bearer'
    }


@pytest.fixture
def mock_property_search_response():
    """Mock property search API response"""
    return {
        'properties': [{
            'clipId': 'CLIP-12345',
            'address': {
                'oneLine': '123 Main St, Miami, FL 33101',
                'locality': 'Miami',
                'countrySubd': 'FL',
                'postal1': '33101',
                'county': 'Miami-Dade'
            },
            'property': {
                'propertyType': 'Single Family'
            },
            'building': {
                'yearBuilt': 2010,
                'rooms': {
                    'beds': 3,
                    'bathsTotal': 2.0
                },
                'size': {
                    'universalSize': 1500
                }
            },
            'lot': {
                'lotSize1': 5000
            },
            'sale': {
                'mostRecentDate': '2020-01-15',
                'mostRecentPrice': 350000
            },
            'assessment': {
                'total': {
                    'assdTtlValue': 320000
                }
            }
        }]
    }


class TestCoreLogicClientInit:
    """Test client initialization"""
    
    def test_init_with_env_vars(self, mock_env):
        """Test initialization with environment variables"""
        client = CoreLogicClient()
        assert client.consumer_key == 'test_key'
        assert client.consumer_secret == 'test_secret'
        assert client.access_token is None
        assert client.token_expires_at is None
    
    def test_init_with_explicit_credentials(self):
        """Test initialization with explicit credentials"""
        client = CoreLogicClient(consumer_key='key123', consumer_secret='secret456')
        assert client.consumer_key == 'key123'
        assert client.consumer_secret == 'secret456'
    
    def test_init_without_credentials(self, monkeypatch):
        """Test initialization fails without credentials"""
        monkeypatch.delenv('CORELOGIC_CONSUMER_KEY', raising=False)
        monkeypatch.delenv('CORELOGIC_CONSUMER_SECRET', raising=False)
        
        with pytest.raises(ValueError, match="CoreLogic credentials not found"):
            CoreLogicClient()


class TestOAuth2TokenManagement:
    """Test OAuth2 token retrieval and caching"""
    
    @patch('app.clients.corelogic_client.requests.post')
    def test_get_access_token_success(self, mock_post, client, mock_token_response):
        """Test successful token retrieval"""
        mock_post.return_value.json.return_value = mock_token_response
        mock_post.return_value.raise_for_status = Mock()
        
        token = client._get_access_token()
        
        assert token == 'mock_access_token_12345'
        assert client.access_token == 'mock_access_token_12345'
        assert client.token_expires_at is not None
        
        # Verify correct auth request
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs['auth'] == ('test_key', 'test_secret')
        assert call_kwargs['data'] == {'grant_type': 'client_credentials'}
    
    @patch('app.clients.corelogic_client.requests.post')
    def test_token_caching(self, mock_post, client, mock_token_response):
        """Test token is cached and not re-requested"""
        mock_post.return_value.json.return_value = mock_token_response
        mock_post.return_value.raise_for_status = Mock()
        
        # First call - should request token
        token1 = client._get_access_token()
        assert mock_post.call_count == 1
        
        # Second call - should use cached token
        token2 = client._get_access_token()
        assert mock_post.call_count == 1  # No additional call
        assert token1 == token2
    
    @patch('app.clients.corelogic_client.requests.post')
    def test_token_refresh_when_expired(self, mock_post, client, mock_token_response):
        """Test token is refreshed when expired"""
        mock_post.return_value.json.return_value = mock_token_response
        mock_post.return_value.raise_for_status = Mock()
        
        # First call
        token1 = client._get_access_token()
        
        # Manually expire token
        client.token_expires_at = datetime.now() - timedelta(minutes=10)
        
        # Second call - should request new token
        token2 = client._get_access_token()
        assert mock_post.call_count == 2


class TestPropertySearch:
    """Test property search functionality"""
    
    @patch.object(CoreLogicClient, '_make_request')
    def test_search_property_success(self, mock_request, client, mock_property_search_response):
        """Test successful property search"""
        mock_request.return_value = mock_property_search_response
        
        result = client.search_property("123 Main St, Miami, FL 33101")
        
        assert result['clip_id'] == 'CLIP-12345'
        assert result['address'] == '123 Main St, Miami, FL 33101'
        assert result['city'] == 'Miami'
        assert result['state'] == 'FL'
        assert result['zip'] == '33101'
        assert result['bedrooms'] == 3
        assert result['bathrooms'] == 2.0
        assert result['square_feet'] == 1500
        assert result['last_sale_price'] == 350000
    
    @patch.object(CoreLogicClient, '_make_request')
    def test_search_property_not_found(self, mock_request, client):
        """Test property search with no results"""
        mock_request.return_value = {'properties': []}
        
        with pytest.raises(Exception, match="No property found"):
            client.search_property("999 Nonexistent St")
    
    @patch.object(CoreLogicClient, '_make_request')
    def test_search_with_optional_params(self, mock_request, client, mock_property_search_response):
        """Test property search with optional parameters"""
        mock_request.return_value = mock_property_search_response
        
        client.search_property(
            address="123 Main St",
            city="Miami",
            state="FL",
            zip_code="33101"
        )
        
        # Verify params were passed correctly
        call_args = mock_request.call_args
        assert call_args[0][0] == 'search'
        assert call_args[1]['params']['address'] == "123 Main St"
        assert call_args[1]['params']['city'] == "Miami"
        assert call_args[1]['params']['state'] == "FL"
        assert call_args[1]['params']['zip'] == "33101"


class TestPropertyDetails:
    """Test property details retrieval"""
    
    @patch.object(CoreLogicClient, '_make_request')
    def test_get_property_details(self, mock_request, client):
        """Test getting detailed property information"""
        mock_response = {
            'property': {'propertyType': 'Single Family'},
            'building': {'yearBuilt': 2010},
            'lot': {'lotSize1': 5000},
            'owner': {'name': 'John Doe'},
            'assessment': {'total': {'assdTtlValue': 320000}},
            'sale': {'mostRecentPrice': 350000},
            'mortgage': {},
            'tax': {}
        }
        mock_request.return_value = mock_response
        
        result = client.get_property_details('CLIP-12345')
        
        assert result['clip_id'] == 'CLIP-12345'
        assert result['property'] == {'propertyType': 'Single Family'}
        assert result['building'] == {'yearBuilt': 2010}
        assert result['owner'] == {'name': 'John Doe'}
        
        # Verify correct endpoint called
        mock_request.assert_called_once_with('property/CLIP-12345')


class TestComparables:
    """Test comparable properties retrieval"""
    
    @patch.object(CoreLogicClient, '_make_request')
    def test_get_comparables_success(self, mock_request, client):
        """Test getting comparable properties"""
        mock_response = {
            'comparables': [
                {
                    'clipId': 'CLIP-COMP1',
                    'address': {'oneLine': '125 Main St, Miami, FL'},
                    'distance': 0.1,
                    'building': {
                        'rooms': {'beds': 3, 'bathsTotal': 2},
                        'size': {'universalSize': 1520},
                        'yearBuilt': 2012
                    },
                    'sale': {
                        'mostRecentDate': '2024-06-15',
                        'mostRecentPrice': 375000
                    },
                    'similarityScore': 92
                },
                {
                    'clipId': 'CLIP-COMP2',
                    'address': {'oneLine': '127 Main St, Miami, FL'},
                    'distance': 0.15,
                    'building': {
                        'rooms': {'beds': 3, 'bathsTotal': 2},
                        'size': {'universalSize': 1480},
                        'yearBuilt': 2009
                    },
                    'sale': {
                        'mostRecentDate': '2024-08-20',
                        'mostRecentPrice': 365000
                    },
                    'similarityScore': 88
                }
            ]
        }
        mock_request.return_value = mock_response
        
        comps = client.get_comparables('CLIP-12345', radius_miles=0.5, max_results=10)
        
        assert len(comps) == 2
        assert comps[0]['clip_id'] == 'CLIP-COMP1'
        assert comps[0]['distance_miles'] == 0.1
        assert comps[0]['last_sale_price'] == 375000
        assert comps[0]['similarity_score'] == 92
        
        # Verify correct endpoint and params
        call_args = mock_request.call_args
        assert call_args[0][0] == 'property/CLIP-12345/comps'
        assert call_args[1]['params']['radius'] == 0.5
        assert call_args[1]['params']['limit'] == 10
    
    @patch.object(CoreLogicClient, '_make_request')
    def test_get_comparables_none_found(self, mock_request, client):
        """Test when no comparables are found"""
        mock_request.return_value = {'comparables': []}
        
        with pytest.raises(Exception, match="No comparable properties found"):
            client.get_comparables('CLIP-12345')


class TestAVM:
    """Test Automated Valuation Model (AVM)"""
    
    @patch.object(CoreLogicClient, '_make_request')
    def test_estimate_value_success(self, mock_request, client):
        """Test AVM value estimation"""
        mock_response = {
            'avm': {
                'amount': 425000,
                'confidenceScore': 85,
                'valueLow': 400000,
                'valueHigh': 450000,
                'asOfDate': '2025-10-04'
            }
        }
        mock_request.return_value = mock_response
        
        estimate = client.estimate_value('CLIP-12345')
        
        assert estimate['estimated_value'] == 425000
        assert estimate['confidence_score'] == 85
        assert estimate['value_range_low'] == 400000
        assert estimate['value_range_high'] == 450000
        assert estimate['as_of_date'] == '2025-10-04'
        
        # Verify correct endpoint
        mock_request.assert_called_once_with('property/CLIP-12345/avm')


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @patch('app.clients.corelogic_client.requests.post')
    def test_auth_failure(self, mock_post, client):
        """Test handling of authentication failure"""
        mock_post.side_effect = Exception("Network error")
        
        with pytest.raises(Exception, match="CoreLogic authentication failed"):
            client._get_access_token()
    
    @patch('app.clients.corelogic_client.requests.get')
    @patch.object(CoreLogicClient, '_get_access_token')
    def test_404_not_found(self, mock_token, mock_get, client):
        """Test handling of 404 property not found"""
        mock_token.return_value = 'test_token'
        mock_get.return_value.status_code = 404
        mock_get.return_value.raise_for_status.side_effect = requests.HTTPError(response=mock_get.return_value)
        
        with pytest.raises(Exception, match="Property not found in CoreLogic database"):
            client._make_request('property/INVALID')
    
    @patch('app.clients.corelogic_client.requests.get')
    @patch.object(CoreLogicClient, '_get_access_token')
    def test_rate_limit(self, mock_token, mock_get, client):
        """Test handling of rate limit (429)"""
        mock_token.return_value = 'test_token'
        mock_get.return_value.status_code = 429
        mock_get.return_value.raise_for_status.side_effect = requests.HTTPError(response=mock_get.return_value)
        
        with pytest.raises(Exception, match="rate limit exceeded"):
            client._make_request('search')
    
    @patch('app.clients.corelogic_client.requests.get')
    @patch.object(CoreLogicClient, '_get_access_token')
    def test_timeout(self, mock_token, mock_get, client):
        """Test handling of request timeout"""
        mock_token.return_value = 'test_token'
        mock_get.side_effect = requests.Timeout()
        
        with pytest.raises(Exception, match="timed out"):
            client._make_request('search')
