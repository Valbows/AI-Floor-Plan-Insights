"""
CoreLogic API Client
Handles OAuth2 authentication and API requests to CoreLogic Property Data API
"""

import os
import time
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime, timedelta


class CoreLogicClient:
    """
    Client for CoreLogic Property Data API
    
    Features:
    - OAuth2 token management with automatic refresh
    - Property search by address
    - Property details retrieval by CLIP ID
    - Comparable properties (comps) search
    - Comprehensive error handling
    """
    
    # API URLs based on CoreLogic documentation
    def __init__(self, consumer_key: Optional[str] = None, consumer_secret: Optional[str] = None):
        """
        Initialize CoreLogic API client
        
        Args:
            consumer_key: CoreLogic API consumer key (or from CORELOGIC_CONSUMER_KEY env var)
            consumer_secret: CoreLogic API consumer secret (or from CORELOGIC_CONSUMER_SECRET env var)
        """
        self.consumer_key = consumer_key or os.getenv('CORELOGIC_CONSUMER_KEY')
        self.consumer_secret = consumer_secret or os.getenv('CORELOGIC_CONSUMER_SECRET')
        
        # Build URLs based on actual CoreLogic API documentation
        base_url = os.getenv('CORELOGIC_API_URL', 'https://api-prod.corelogic.com')
        self.AUTH_URL = f"{base_url}/oauth/token"
        self.PROPERTY_URL = f"{base_url}/property"  # For typeahead and property details
        self.PROPERTY_V2_URL = "https://property.corelogicapi.com/v2"  # For AVM/RAM endpoints
        
        if not self.consumer_key or not self.consumer_secret:
            raise ValueError("CoreLogic credentials not found. Set CORELOGIC_CONSUMER_KEY and CORELOGIC_CONSUMER_SECRET")
        
        self.access_token = None
        self.token_expires_at = None
        
    def _get_access_token(self) -> str:
        """
        Get OAuth2 access token (with caching and auto-refresh)
        
        Returns:
            Valid access token
        
        Raises:
            requests.HTTPError: If authentication fails
        """
        # Return cached token if still valid
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at - timedelta(minutes=5):
                return self.access_token
        
        # Request new token (grant_type as query parameter per CoreLogic API)
        try:
            response = requests.post(
                f"{self.AUTH_URL}?grant_type=client_credentials",
                auth=(self.consumer_key, self.consumer_secret),
                headers={'Content-Length': '0'},
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Calculate expiry time (usually 3600 seconds)
            # Convert to int in case CoreLogic returns string
            expires_in = int(token_data.get('expires_in', 3600))
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"CoreLogic authentication failed: {str(e)}")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, method: str = 'GET') -> Dict[str, Any]:
        """
        Make authenticated API request to CoreLogic
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            method: HTTP method (GET, POST)
        
        Returns:
            API response as dictionary
        
        Raises:
            requests.HTTPError: If request fails
        """
        token = self._get_access_token()
        url = f"{self.BASE_URL}/{endpoint}"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception("Property not found in CoreLogic database")
            elif e.response.status_code == 401:
                # Token might be invalid, clear cache and retry once
                self.access_token = None
                self.token_expires_at = None
                raise Exception("Authentication failed. Token expired or invalid.")
            elif e.response.status_code == 429:
                raise Exception("CoreLogic API rate limit exceeded")
            else:
                raise Exception(f"CoreLogic API error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.Timeout:
            raise Exception("CoreLogic API request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"CoreLogic API request failed: {str(e)}")
    
    def search_property(self, address: str, city: Optional[str] = None, 
                       state: Optional[str] = None, zip_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for property by address using CoreLogic typeahead endpoint
        
        Args:
            address: Full address string (e.g., "919 MALCOLM AVE, LOS ANGELES, CA 90024")
            city: City name (optional, can be in address)
            state: State abbreviation (optional, can be in address)
            zip_code: ZIP code (optional, can be in address)
        
        Returns:
            {
                "clip_id": "06037:1081685",
                "address": "919 MALCOLM AVE",
                "city": "LOS ANGELES",
                "state": "CA",
                "zip": "90024",
                "county": "LOS ANGELES",
                "property_type": "Single Family",
                "year_built": 2010,
                "bedrooms": 3,
                "bathrooms": 2.0,
                "square_feet": 1500,
                "lot_size": 5000,
                "last_sale_date": "2020-01-15",
                "last_sale_price": 350000,
                "assessed_value": 320000
            }
        
        Raises:
            Exception: If property not found or API error
        """
        # Build full address string for typeahead
        full_address = address
        if city:
            full_address += f", {city}"
        if state:
            full_address += f", {state}"
        if zip_code:
            full_address += f" {zip_code}"
        
        # Use typeahead endpoint per CoreLogic documentation
        token = self._get_access_token()
        try:
            response = requests.get(
                f"{self.PROPERTY_URL}/typeahead",
                params={'input': full_address},
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception(f"No property found for address: {full_address}")
            else:
                raise Exception(f"CoreLogic typeahead error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Property search failed: {str(e)}")
        
        # Extract and normalize property data from typeahead results
        results = result.get('results', [])
        if not results:
            raise Exception(f"No property found for address: {full_address}")
        
        # Return first matching property
        property_data = results[0]
        
        return {
            'clip_id': property_data.get('clipId'),
            'address': property_data.get('address', {}).get('oneLine'),
            'city': property_data.get('address', {}).get('locality'),
            'state': property_data.get('address', {}).get('countrySubd'),
            'zip': property_data.get('address', {}).get('postal1'),
            'county': property_data.get('address', {}).get('county'),
            'property_type': property_data.get('property', {}).get('propertyType'),
            'year_built': property_data.get('building', {}).get('yearBuilt'),
            'bedrooms': property_data.get('building', {}).get('rooms', {}).get('beds'),
            'bathrooms': property_data.get('building', {}).get('rooms', {}).get('bathsTotal'),
            'square_feet': property_data.get('building', {}).get('size', {}).get('universalSize'),
            'lot_size': property_data.get('lot', {}).get('lotSize1'),
            'last_sale_date': property_data.get('sale', {}).get('mostRecentDate'),
            'last_sale_price': property_data.get('sale', {}).get('mostRecentPrice'),
            'assessed_value': property_data.get('assessment', {}).get('total', {}).get('assdTtlValue')
        }
    
    def get_property_details(self, clip_id: str) -> Dict[str, Any]:
        """
        Get comprehensive property details by CLIP ID
        
        Args:
            clip_id: CoreLogic Property ID (from search_property)
        
        Returns:
            Detailed property information including:
            - Full property characteristics
            - Owner information (if available)
            - Tax information
            - Sale history
            - Mortgage information
        
        Raises:
            Exception: If property not found or API error
        """
        result = self._make_request(f'property/{clip_id}')
        
        return {
            'clip_id': clip_id,
            'property': result.get('property', {}),
            'building': result.get('building', {}),
            'lot': result.get('lot', {}),
            'owner': result.get('owner', {}),
            'assessment': result.get('assessment', {}),
            'sale': result.get('sale', {}),
            'mortgage': result.get('mortgage', {}),
            'tax': result.get('tax', {})
        }
    
    def get_comparables(self, clip_id: str, radius_miles: float = 0.5, 
                       max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get comparable properties (comps) for valuation
        
        Args:
            clip_id: Subject property CLIP ID
            radius_miles: Search radius in miles (default 0.5)
            max_results: Maximum number of comps to return (default 10)
        
        Returns:
            List of comparable properties with:
            - Property details
            - Distance from subject property
            - Sold date and price
            - Similarity score
        
        Raises:
            Exception: If no comps found or API error
        """
        params = {
            'radius': radius_miles,
            'limit': max_results,
            'sort': 'distance'  # Sort by proximity
        }
        
        result = self._make_request(f'property/{clip_id}/comps', params=params)
        
        if not result.get('comparables'):
            raise Exception(f"No comparable properties found for CLIP ID: {clip_id}")
        
        # Normalize comp data
        comps = []
        for comp in result['comparables']:
            comps.append({
                'clip_id': comp.get('clipId'),
                'address': comp.get('address', {}).get('oneLine'),
                'distance_miles': comp.get('distance'),
                'bedrooms': comp.get('building', {}).get('rooms', {}).get('beds'),
                'bathrooms': comp.get('building', {}).get('rooms', {}).get('bathsTotal'),
                'square_feet': comp.get('building', {}).get('size', {}).get('universalSize'),
                'year_built': comp.get('building', {}).get('yearBuilt'),
                'last_sale_date': comp.get('sale', {}).get('mostRecentDate'),
                'last_sale_price': comp.get('sale', {}).get('mostRecentPrice'),
                'similarity_score': comp.get('similarityScore', 0)
            })
        
        return comps
    
    def estimate_value(self, clip_id: str) -> Dict[str, Any]:
        """
        Get automated valuation model (AVM) estimate
        
        Args:
            clip_id: Property CLIP ID
        
        Returns:
            {
                "estimated_value": 425000,
                "confidence_score": 85,
                "value_range_low": 400000,
                "value_range_high": 450000,
                "as_of_date": "2025-10-04"
            }
        
        Raises:
            Exception: If AVM unavailable or API error
        """
        result = self._make_request(f'property/{clip_id}/avm')
        
        avm_data = result.get('avm', {})
        
        return {
            'estimated_value': avm_data.get('amount'),
            'confidence_score': avm_data.get('confidenceScore'),
            'value_range_low': avm_data.get('valueLow'),
            'value_range_high': avm_data.get('valueHigh'),
            'as_of_date': avm_data.get('asOfDate')
        }
    
    def get_rent_amount_model(self, clip_id: str) -> Dict[str, Any]:
        """
        Get Rent Amount Model (RAM) - Estimated rental value and investment metrics
        
        Provides property-level estimated rental value including:
        - Estimated monthly rental value
        - Forecast standard deviation
        - Rental value range (high/low)
        - Capitalization (CAP) rate for investment analysis
        
        Args:
            clip_id: Property CLIP ID
        
        Returns:
            {
                "estimated_rental_value": 2500,
                "forecast_std_deviation": 0.1,
                "rental_range_low": 2250,
                "rental_range_high": 2750,
                "cap_rate": 5.5,
                "run_date": "2025-10-04"
            }
        
        Raises:
            Exception: If RAM unavailable or API error
        """
        # CoreLogic RAM endpoint per documentation
        token = self._get_access_token()
        try:
            response = requests.get(
                f"{self.PROPERTY_V2_URL}/avms/ram",
                params={'clip': clip_id},
                headers={
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"RAM API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"RAM request failed: {str(e)}")
        
        data = result.get('data', {})
        model_output = data.get('modelOutput', {})
        value_range = model_output.get('estimatedValueRange', {})
        additional = model_output.get('additionalValues', {})
        
        return {
            'estimated_rental_value': model_output.get('estimatedValue'),
            'forecast_std_deviation': model_output.get('forecastStandardDeviation'),
            'rental_range_low': value_range.get('low'),
            'rental_range_high': value_range.get('high'),
            'cap_rate': additional.get('capRate'),
            'run_date': data.get('runDate')
        }
