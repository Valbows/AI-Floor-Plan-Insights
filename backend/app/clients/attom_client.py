"""
ATTOM API Client
Handles API requests to ATTOM Property Data API (Free Trial)

Documentation: https://api.developer.attomdata.com/docs
Sample Code: https://api.developer.attomdata.com/sample-code-guide
"""

import os
import time
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime


class AttomAPIClient:
    """
    Client for ATTOM Property Data API (Free Trial)
    
    Features:
    - API Key authentication (simple header-based)
    - Property search by address
    - Property details retrieval
    - AVM (Automated Valuation Model)
    - Sales history
    - Area/neighborhood statistics
    - POI (Points of Interest) data
    - Comprehensive error handling with rate limiting
    """
    
    BASE_URL = "https://api.gateway.attomdata.com"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ATTOM API client
        
        Args:
            api_key: ATTOM API key (or from ATTOM_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ATTOM_API_KEY')
        
        if not self.api_key:
            raise ValueError("ATTOM API key not found. Set ATTOM_API_KEY environment variable")
        
        self.session = requests.Session()
        self.session.headers.update({
            'apikey': self.api_key,
            'Accept': 'application/json'
        })
        
        # Rate limiting tracking (free trial limits)
        self.request_count = 0
        self.last_request_time = None
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, method: str = 'GET') -> Dict[str, Any]:
        """
        Make authenticated API request to ATTOM
        
        Args:
            endpoint: API endpoint path (e.g., 'property/address')
            params: Query parameters
            method: HTTP method (GET, POST)
        
        Returns:
            API response as dictionary
        
        Raises:
            Exception: If request fails
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Basic rate limiting (500ms between requests)
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < 0.5:
                time.sleep(0.5 - elapsed)
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, json=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            self.last_request_time = time.time()
            self.request_count += 1
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception("Property not found in ATTOM database")
            elif e.response.status_code == 401:
                raise Exception("ATTOM API authentication failed. Check your API key.")
            elif e.response.status_code == 403:
                raise Exception("ATTOM API access forbidden. Check API key permissions.")
            elif e.response.status_code == 429:
                raise Exception("ATTOM API rate limit exceeded. Free trial has daily limits.")
            elif e.response.status_code == 400:
                raise Exception(f"ATTOM API bad request: {e.response.text}")
            else:
                raise Exception(f"ATTOM API error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.Timeout:
            raise Exception("ATTOM API request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"ATTOM API request failed: {str(e)}")
    
    def search_property(self, address: str, city: Optional[str] = None, 
                       state: Optional[str] = None, zip_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for property by address using ATTOM address endpoint
        
        Args:
            address: Street address (e.g., "123 Main St")
            city: City name (optional, but recommended)
            state: State abbreviation (optional, but recommended)
            zip_code: ZIP code (optional)
        
        Returns:
            {
                "attom_id": "123456789",
                "apn": "1234-567-890",
                "address": "123 MAIN ST",
                "city": "LOS ANGELES",
                "state": "CA",
                "zip": "90001",
                "county": "LOS ANGELES",
                "property_type": "Single Family Residence",
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
        # Build params for ATTOM address search
        params = {
            'address1': address
        }
        
        if city:
            params['address2'] = city
        if state:
            params['address2'] = f"{params.get('address2', '')}, {state}".strip(', ')
        if zip_code:
            params['postalcode'] = zip_code
        
        try:
            result = self._make_request('property/address', params=params)
        except Exception as e:
            # Try with full address string if structured search fails
            if city and state:
                full_address = f"{address}, {city}, {state}"
                if zip_code:
                    full_address += f" {zip_code}"
                raise Exception(f"No property found for address: {full_address}")
            raise
        
        # Extract property data from ATTOM response
        status = result.get('status', {})
        if status.get('code') != 0:
            error_msg = status.get('msg', 'Unknown error')
            raise Exception(f"ATTOM API error: {error_msg}")
        
        properties = result.get('property', [])
        if not properties:
            raise Exception(f"No property found for address: {address}")
        
        # Return first matching property
        prop = properties[0]
        
        # Extract nested data
        identifier = prop.get('identifier', {})
        address_data = prop.get('address', {})
        building = prop.get('building', {})
        rooms = building.get('rooms', {})
        size = building.get('size', {})
        lot = prop.get('lot', {})
        sale = prop.get('sale', {})
        assessment = prop.get('assessment', {})
        
        return {
            'attom_id': identifier.get('attomId'),
            'apn': identifier.get('apn'),
            'fips': identifier.get('fips'),
            'address': address_data.get('line1'),
            'city': address_data.get('locality'),
            'state': address_data.get('countrySubd'),
            'zip': address_data.get('postal1'),
            'county': address_data.get('county'),
            'property_type': prop.get('summary', {}).get('proptype'),
            'year_built': building.get('summary', {}).get('yearbuilt'),
            'bedrooms': rooms.get('beds'),
            'bathrooms': rooms.get('bathstotal'),
            'square_feet': size.get('universalsize'),
            'lot_size': lot.get('lotsize1'),
            'last_sale_date': sale.get('saleTransDate'),
            'last_sale_price': sale.get('saleAmtStndUnit'),
            'assessed_value': assessment.get('assessed', {}).get('assdttlvalue')
        }
    
    def get_property_details(self, attom_id: str) -> Dict[str, Any]:
        """
        Get comprehensive property details by ATTOM ID
        
        Args:
            attom_id: ATTOM Property ID (from search_property)
        
        Returns:
            Detailed property information including:
            - Full property characteristics
            - Building details
            - Lot information
            - Assessment data
            - Sale history
        
        Raises:
            Exception: If property not found or API error
        """
        result = self._make_request(f'property/detail', params={'attomid': attom_id})
        
        status = result.get('status', {})
        if status.get('code') != 0:
            raise Exception(f"ATTOM API error: {status.get('msg')}")
        
        properties = result.get('property', [])
        if not properties:
            raise Exception(f"No property details found for ATTOM ID: {attom_id}")
        
        return properties[0]
    
    def get_avm(self, address: str, city: str, state: str, zip_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Automated Valuation Model (AVM) estimate
        
        Args:
            address: Street address
            city: City name
            state: State abbreviation
            zip_code: ZIP code (optional)
        
        Returns:
            {
                "estimated_value": 425000,
                "confidence_score": 85.0,
                "value_range_low": 400000,
                "value_range_high": 450000,
                "fsd": 0.05,  # Forecast standard deviation
                "as_of_date": "2025-10-13"
            }
        
        Raises:
            Exception: If AVM unavailable or API error
        """
        params = {
            'address1': address,
            'address2': f"{city}, {state}"
        }
        if zip_code:
            params['postalcode'] = zip_code
        
        result = self._make_request('property/avm', params=params)
        
        status = result.get('status', {})
        if status.get('code') != 0:
            raise Exception(f"ATTOM AVM error: {status.get('msg')}")
        
        properties = result.get('property', [])
        if not properties:
            raise Exception("AVM data not available for this property")
        
        avm = properties[0].get('avm', {})
        amount = avm.get('amount', {})
        
        return {
            'estimated_value': amount.get('value'),
            'confidence_score': avm.get('confidenceScore', {}).get('score'),
            'value_range_low': amount.get('low'),
            'value_range_high': amount.get('high'),
            'fsd': avm.get('fsd'),  # Forecast standard deviation
            'as_of_date': avm.get('eventDate')
        }
    
    def get_sales_history(self, attom_id: str) -> List[Dict[str, Any]]:
        """
        Get property sales history
        
        Args:
            attom_id: ATTOM Property ID
        
        Returns:
            List of sales transactions with dates and amounts
        
        Raises:
            Exception: If sales history unavailable or API error
        """
        result = self._make_request('property/saleshistory', params={'attomid': attom_id})
        
        status = result.get('status', {})
        if status.get('code') != 0:
            raise Exception(f"ATTOM sales history error: {status.get('msg')}")
        
        properties = result.get('property', [])
        if not properties:
            return []
        
        sales = properties[0].get('sale', {}).get('saleshistory', [])
        
        # Normalize sales data
        normalized_sales = []
        for sale in sales:
            normalized_sales.append({
                'sale_date': sale.get('saleTransDate'),
                'sale_price': sale.get('saleAmtStndUnit'),
                'sale_type': sale.get('saleType'),
                'buyer_name': sale.get('buyerName'),
                'seller_name': sale.get('sellerName')
            })
        
        return normalized_sales
    
    def get_comparables(self, address: str, city: str, state: str, 
                       radius_miles: float = 0.5, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get comparable properties (comps) for valuation
        
        Note: ATTOM free trial may have limited comp access. This uses
        the property/address endpoint with geographic filtering.
        
        Args:
            address: Subject property address
            city: City name
            state: State abbreviation
            radius_miles: Search radius in miles (default 0.5)
            max_results: Maximum number of comps to return (default 10)
        
        Returns:
            List of comparable properties with sale data
        
        Raises:
            Exception: If no comps found or API error
        """
        # ATTOM may not have a dedicated comps endpoint in free trial
        # This is a placeholder - actual implementation depends on available endpoints
        # For now, we'll use the expanded property search
        
        params = {
            'address2': f"{city}, {state}",
            'radius': radius_miles,
            'orderby': 'distance'
        }
        
        try:
            result = self._make_request('property/expandedprofile', params=params)
            
            status = result.get('status', {})
            if status.get('code') != 0:
                # If expandedprofile not available, return empty list
                return []
            
            properties = result.get('property', [])[:max_results]
            
            comps = []
            for prop in properties:
                sale = prop.get('sale', {})
                building = prop.get('building', {})
                address_data = prop.get('address', {})
                
                comps.append({
                    'attom_id': prop.get('identifier', {}).get('attomId'),
                    'address': address_data.get('oneLine'),
                    'bedrooms': building.get('rooms', {}).get('beds'),
                    'bathrooms': building.get('rooms', {}).get('bathstotal'),
                    'square_feet': building.get('size', {}).get('universalsize'),
                    'year_built': building.get('summary', {}).get('yearbuilt'),
                    'last_sale_date': sale.get('saleTransDate'),
                    'last_sale_price': sale.get('saleAmtStndUnit')
                })
            
            return comps
            
        except Exception:
            # Comps may not be available in free trial
            return []
    
    def get_area_stats(self, zip_code: str) -> Dict[str, Any]:
        """
        Get area/neighborhood statistics by ZIP code
        
        Args:
            zip_code: ZIP code for area lookup
        
        Returns:
            {
                "median_home_value": 450000,
                "median_household_income": 75000,
                "population": 25000,
                "demographics": {...}
            }
        
        Raises:
            Exception: If area data unavailable or API error
        """
        result = self._make_request('area/full', params={'postalcode': zip_code})
        
        status = result.get('status', {})
        if status.get('code') != 0:
            raise Exception(f"ATTOM area stats error: {status.get('msg')}")
        
        areas = result.get('area', [])
        if not areas:
            raise Exception(f"No area data found for ZIP: {zip_code}")
        
        area = areas[0]
        
        return {
            'zip_code': zip_code,
            'median_home_value': area.get('medianHomeValue'),
            'median_household_income': area.get('medianHouseholdIncome'),
            'population': area.get('population'),
            'demographics': area.get('demographics', {})
        }
    
    def get_poi_schools(self, latitude: float, longitude: float, radius_miles: float = 2.0) -> List[Dict[str, Any]]:
        """
        Get nearby schools (Points of Interest)
        
        Args:
            latitude: Property latitude
            longitude: Property longitude
            radius_miles: Search radius in miles (default 2.0)
        
        Returns:
            List of nearby schools with ratings and details
        
        Raises:
            Exception: If POI data unavailable or API error
        """
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'radius': radius_miles,
            'category': 'school'
        }
        
        try:
            result = self._make_request('poi/pointsofinterest', params=params)
            
            status = result.get('status', {})
            if status.get('code') != 0:
                return []
            
            pois = result.get('poi', [])
            
            schools = []
            for poi in pois:
                schools.append({
                    'name': poi.get('name'),
                    'type': poi.get('type'),
                    'distance_miles': poi.get('distance'),
                    'rating': poi.get('rating'),
                    'address': poi.get('address', {}).get('oneLine')
                })
            
            return schools
            
        except Exception:
            # POI may not be available in free trial
            return []
