"""
Unit tests for ATTOM API Client
Tests property search, AVM, sales history, and area stats
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.clients.attom_client import AttomAPIClient


@pytest.fixture
def attom_client():
    """Fixture for ATTOM API client with mocked API key"""
    with patch.dict('os.environ', {'ATTOM_API_KEY': 'test_api_key'}):
        return AttomAPIClient()


@pytest.fixture
def mock_property_response():
    """Mock property search response from ATTOM API"""
    return {
        'status': {'code': 0, 'msg': 'Success'},
        'property': [{
            'identifier': {
                'attomId': '123456789',
                'apn': '1234-567-890',
                'fips': '06037'
            },
            'address': {
                'line1': '123 MAIN ST',
                'locality': 'LOS ANGELES',
                'countrySubd': 'CA',
                'postal1': '90001',
                'county': 'LOS ANGELES'
            },
            'building': {
                'summary': {'yearbuilt': 2010},
                'rooms': {'beds': 3, 'bathstotal': 2.0},
                'size': {'universalsize': 1500}
            },
            'lot': {'lotsize1': 5000},
            'sale': {
                'saleTransDate': '2020-01-15',
                'saleAmtStndUnit': 350000
            },
            'assessment': {
                'assessed': {'assdttlvalue': 320000}
            },
            'summary': {'proptype': 'Single Family Residence'}
        }]
    }


@pytest.fixture
def mock_avm_response():
    """Mock AVM response from ATTOM API"""
    return {
        'status': {'code': 0, 'msg': 'Success'},
        'property': [{
            'avm': {
                'amount': {'value': 425000, 'low': 400000, 'high': 450000},
                'confidenceScore': {'score': 85.0},
                'fsd': 0.05,
                'eventDate': '2025-10-13'
            }
        }]
    }


class TestAttomAPIClient:
    """Test suite for ATTOM API Client"""
    
    def test_initialization_with_api_key(self):
        """Test client initializes with API key"""
        with patch.dict('os.environ', {'ATTOM_API_KEY': 'test_key'}):
            client = AttomAPIClient()
            assert client.api_key == 'test_key'
            assert client.session.headers['apikey'] == 'test_key'
    
    def test_initialization_without_api_key_raises_error(self):
        """Test client raises error when API key is missing"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="ATTOM API key not found"):
                AttomAPIClient()
    
    @patch('app.clients.attom_client.requests.Session.get')
    def test_search_property_success(self, mock_get, attom_client, mock_property_response):
        """Test successful property search"""
        mock_get.return_value.json.return_value = mock_property_response
        mock_get.return_value.raise_for_status = Mock()
        
        result = attom_client.search_property(
            address='123 Main St',
            city='Los Angeles',
            state='CA',
            zip_code='90001'
        )
        
        assert result['attom_id'] == '123456789'
        assert result['address'] == '123 MAIN ST'
        assert result['city'] == 'LOS ANGELES'
        assert result['state'] == 'CA'
        assert result['zip'] == '90001'
        assert result['bedrooms'] == 3
        assert result['bathrooms'] == 2.0
        assert result['square_feet'] == 1500
        assert result['last_sale_price'] == 350000
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'property/basicprofile' in call_args[0][0]
    
    @patch('app.clients.attom_client.requests.Session.get')
    def test_search_property_not_found(self, mock_get, attom_client):
        """Test property search when property not found"""
        mock_get.return_value.json.return_value = {
            'status': {'code': 0},
            'property': []
        }
        mock_get.return_value.raise_for_status = Mock()
        
        with pytest.raises(Exception, match="No property found"):
            attom_client.search_property('999 Fake St', 'Nowhere', 'XX')
    
    @patch('app.clients.attom_client.requests.Session.get')
    def test_search_property_api_error(self, mock_get, attom_client):
        """Test property search with API error"""
        mock_get.return_value.json.return_value = {
            'status': {'code': 1, 'msg': 'Invalid address'},
            'property': []
        }
        mock_get.return_value.raise_for_status = Mock()
        
        with pytest.raises(Exception, match="ATTOM API error"):
            attom_client.search_property('Invalid', 'Address', 'XX')
    
    @patch('app.clients.attom_client.requests.Session.get')
    def test_get_avm_success(self, mock_get, attom_client, mock_avm_response):
        """Test successful AVM retrieval"""
        mock_get.return_value.json.return_value = mock_avm_response
        mock_get.return_value.raise_for_status = Mock()
        
        result = attom_client.get_avm(
            address='123 Main St',
            city='Los Angeles',
            state='CA',
            zip_code='90001'
        )
        
        assert result['estimated_value'] == 425000
        assert result['confidence_score'] == 85.0
        assert result['value_range_low'] == 400000
        assert result['value_range_high'] == 450000
        assert result['fsd'] == 0.05
        
        # Verify API call
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'property/avm' in call_args[0][0]
    
    @patch('app.clients.attom_client.requests.Session.get')
    def test_get_avm_not_available(self, mock_get, attom_client):
        """Test AVM when not available"""
        mock_get.return_value.json.return_value = {
            'status': {'code': 0},
            'property': []
        }
        mock_get.return_value.raise_for_status = Mock()
        
        with pytest.raises(Exception, match="AVM data not available"):
            attom_client.get_avm('123 Main St', 'Los Angeles', 'CA')
    
    @patch('app.clients.attom_client.requests.Session.get')
    def test_rate_limiting(self, mock_get, attom_client):
        """Test rate limiting is applied between requests"""
        import time
        
        mock_get.return_value.json.return_value = {
            'status': {'code': 0},
            'property': [{'identifier': {'attomId': '123'}}]
        }
        mock_get.return_value.raise_for_status = Mock()
        
        # First request
        start = time.time()
        attom_client._make_request('property/test')
        
        # Second request (should wait at least 500ms)
        attom_client._make_request('property/test')
        elapsed = time.time() - start
        
        # Should take at least 500ms total
        assert elapsed >= 0.5
    
    @patch('app.clients.attom_client.requests.Session.get')
    def test_http_error_handling(self, mock_get, attom_client):
        """Test HTTP error handling"""
        from requests.exceptions import HTTPError
        
        # Test 404
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value.raise_for_status.side_effect = HTTPError(response=mock_response)
        
        with pytest.raises(Exception, match="Property not found in ATTOM database"):
            attom_client._make_request('property/test')
        
        # Test 401
        mock_response.status_code = 401
        with pytest.raises(Exception, match="authentication failed"):
            attom_client._make_request('property/test')
        
        # Test 429
        mock_response.status_code = 429
        with pytest.raises(Exception, match="rate limit exceeded"):
            attom_client._make_request('property/test')
    
    @patch('app.clients.attom_client.requests.Session.get')
    def test_get_sales_history(self, mock_get, attom_client):
        """Test sales history retrieval"""
        mock_get.return_value.json.return_value = {
            'status': {'code': 0},
            'property': [{
                'sale': {
                    'saleshistory': [
                        {
                            'saleTransDate': '2020-01-15',
                            'saleAmtStndUnit': 350000,
                            'saleType': 'Resale',
                            'buyerName': 'John Doe',
                            'sellerName': 'Jane Smith'
                        },
                        {
                            'saleTransDate': '2015-06-20',
                            'saleAmtStndUnit': 280000,
                            'saleType': 'Resale'
                        }
                    ]
                }
            }]
        }
        mock_get.return_value.raise_for_status = Mock()
        
        result = attom_client.get_sales_history('123456789')
        
        assert len(result) == 2
        assert result[0]['sale_date'] == '2020-01-15'
        assert result[0]['sale_price'] == 350000
        assert result[1]['sale_date'] == '2015-06-20'
        assert result[1]['sale_price'] == 280000
    
    @patch('app.clients.attom_client.requests.Session.get')
    def test_get_area_stats(self, mock_get, attom_client):
        """Test area statistics retrieval"""
        mock_get.return_value.json.return_value = {
            'status': {'code': 0},
            'area': [{
                'medianHomeValue': 450000,
                'medianHouseholdIncome': 75000,
                'population': 25000,
                'demographics': {
                    'ageMedian': 35,
                    'educationCollege': 45.5
                }
            }]
        }
        mock_get.return_value.raise_for_status = Mock()
        
        result = attom_client.get_area_stats('90001')
        
        assert result['zip_code'] == '90001'
        assert result['median_home_value'] == 450000
        assert result['median_household_income'] == 75000
        assert result['population'] == 25000
        assert 'demographics' in result

    @patch('app.clients.attom_client.requests.Session.get')
    def test_get_nearby_properties_by_latlng_success(self, mock_get, attom_client):
        """Test nearby properties fallback using expandedprofile"""
        mock_get.return_value.json.return_value = {
            'status': {'code': 0},
            'property': [{
                'identifier': {'attomId': '168834166', 'apn': '123', 'fips': '36081'},
                'address': {
                    'line1': '174A BEACH 118TH ST',
                    'locality': 'ROCKAWAY PARK',
                    'countrySubd': 'NY',
                    'postal1': '11694',
                    'county': 'QUEENS'
                },
                'summary': {'proptype': 'SINGLE FAMILY'},
                'building': {
                    'summary': {'yearbuilt': 1930},
                    'rooms': {'beds': 3, 'bathstotal': 2},
                    'size': {'universalsize': 1500}
                },
                'lot': {'lotsize1': 0.05},
                'sale': {'saleTransDate': '2019-01-01', 'saleAmtStndUnit': 500000},
                'assessment': {'assessed': {'assdttlvalue': 450000}}
            }]
        }
        mock_get.return_value.raise_for_status = Mock()

        result = attom_client.get_nearby_properties_by_latlng(40.57853, -73.83807)
        assert isinstance(result, list)
        assert result and result[0]['attom_id'] == '168834166'
        assert result[0]['zip'] == '11694'
        # Verify endpoint
        call_args = mock_get.call_args
        assert 'property/expandedprofile' in call_args[0][0]

    @patch('app.clients.attom_client.requests.Session.get')
    def test_get_nearby_properties_by_latlng_empty(self, mock_get, attom_client):
        """Test nearby properties when none found"""
        mock_get.return_value.json.return_value = {'status': {'code': 0}, 'property': []}
        mock_get.return_value.raise_for_status = Mock()
        result = attom_client.get_nearby_properties_by_latlng(40.0, -73.0)
        assert result == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
