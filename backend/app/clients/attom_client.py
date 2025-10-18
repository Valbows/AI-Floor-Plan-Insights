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
    
    BASE_URL = "https://api.gateway.attomdata.com/propertyapi/v1.0.0"
    
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
            result = self._make_request('property/basicprofile', params=params)
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

    def get_nearby_properties_by_latlng(self, latitude: float, longitude: float,
                                        radius_miles: float = 0.2, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Find nearby properties using latitude/longitude when address matching fails.

        Args:
            latitude: Latitude of target point
            longitude: Longitude of target point
            radius_miles: Search radius in miles (default 0.2)
            max_results: Max properties to return (default 10)

        Returns:
            List of normalized property dicts similar to search_property() output
        """
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'radius': radius_miles,
            'orderby': 'distance'
        }

        try:
            result = self._make_request('property/expandedprofile', params=params)
            status = result.get('status', {})
            if status.get('code') != 0:
                return []

            properties = result.get('property', [])[:max_results]
            normalized: List[Dict[str, Any]] = []
            for prop in properties:
                identifier = prop.get('identifier', {})
                address_data = prop.get('address', {})
                building = prop.get('building', {})
                rooms = building.get('rooms', {})
                size = building.get('size', {})
                lot = prop.get('lot', {})
                sale = prop.get('sale', {})
                assessment = prop.get('assessment', {})

                normalized.append({
                    'attom_id': identifier.get('attomId'),
                    'apn': identifier.get('apn'),
                    'fips': identifier.get('fips'),
                    'address': address_data.get('line1') or address_data.get('oneLine'),
                    'city': address_data.get('locality'),
                    'state': address_data.get('countrySubd'),
                    'zip': address_data.get('postal1'),
                    'county': address_data.get('county'),
                    'property_type': prop.get('summary', {}).get('proptype') or building.get('summary', {}).get('proptype'),
                    'year_built': building.get('summary', {}).get('yearbuilt'),
                    'bedrooms': rooms.get('beds'),
                    'bathrooms': rooms.get('bathstotal'),
                    'square_feet': size.get('universalsize'),
                    'lot_size': lot.get('lotsize1'),
                    'last_sale_date': sale.get('saleTransDate'),
                    'last_sale_price': sale.get('saleAmtStndUnit'),
                    'assessed_value': assessment.get('assessed', {}).get('assdttlvalue') if isinstance(assessment.get('assessed', {}), dict) else None,
                })

            return normalized
        except Exception:
            return []
    
    def get_sales_trends(self, zip_code: str, interval: str = 'monthly') -> Dict[str, Any]:
        """
        Get sales trend data for market analysis and regression modeling
        
        Provides 2 years of historical sales data including:
        - Average/median sale prices
        - Sale counts (market velocity)
        - Price per square foot trends
        - Month-over-month/year-over-year changes
        
        Args:
            zip_code: ZIP code for market area
            interval: 'monthly', 'quarterly', or 'yearly' (default: monthly)
        
        Returns:
            {
                "zip_code": "10022",
                "interval": "monthly",
                "current_median_price": 850000,
                "current_avg_price": 900000,
                "price_per_sqft": 1200,
                "sale_count_12mo": 145,
                "trends": [
                    {
                        "period": "2024-10",
                        "median_price": 850000,
                        "avg_price": 900000,
                        "sale_count": 12,
                        "price_change_pct": 2.5
                    },
                    ...
                ],
                "yoy_change_pct": 8.5,
                "market_velocity": "moderate"
            }
        
        Raises:
            Exception: If sales trend data unavailable or API error
        """
        params = {
            'postalcode': zip_code,
            'interval': interval
        }
        
        try:
            # Try different salestrend endpoint variations
            # Free trial may have limited access to this endpoint
            endpoints_to_try = [
                'salestrend/snapshot',
                'salestrend/detail',
                'area/salestrend'
            ]
            
            result = None
            last_error = None
            
            for endpoint in endpoints_to_try:
                try:
                    result = self._make_request(endpoint, params=params)
                    break  # Success!
                except Exception as e:
                    last_error = e
                    continue
            
            if not result:
                raise last_error or Exception("Sales trend endpoint not available")
            
            status = result.get('status', {})
            if status.get('code') != 0:
                raise Exception(f"ATTOM sales trend error: {status.get('msg')}")
            
            trends = result.get('salestrends', [])
            if not trends:
                raise Exception(f"No sales trend data found for ZIP: {zip_code}")
            
            # Extract most recent data point
            latest = trends[0] if trends else {}
            
            # Calculate year-over-year change if we have 12+ months of data
            yoy_change = None
            if len(trends) >= 12:
                current_price = latest.get('medianSalePrice', 0)
                year_ago_price = trends[11].get('medianSalePrice', 0)
                if current_price and year_ago_price:
                    yoy_change = ((current_price - year_ago_price) / year_ago_price) * 100
            
            # Calculate price per sqft if available
            price_per_sqft = None
            if latest.get('medianSalePrice') and latest.get('medianSquareFeet'):
                price_per_sqft = latest.get('medianSalePrice') / latest.get('medianSquareFeet')
            
            # Determine market velocity based on sale count trends
            market_velocity = "unknown"
            if len(trends) >= 3:
                recent_avg = sum([t.get('saleCount', 0) for t in trends[:3]]) / 3
                older_avg = sum([t.get('saleCount', 0) for t in trends[3:6]]) / 3 if len(trends) >= 6 else recent_avg
                if recent_avg > older_avg * 1.2:
                    market_velocity = "high"
                elif recent_avg < older_avg * 0.8:
                    market_velocity = "low"
                else:
                    market_velocity = "moderate"
            
            return {
                'zip_code': zip_code,
                'interval': interval,
                'current_median_price': latest.get('medianSalePrice'),
                'current_avg_price': latest.get('avgSalePrice'),
                'price_per_sqft': price_per_sqft,
                'sale_count_12mo': sum([t.get('saleCount', 0) for t in trends[:12]]),
                'trends': [
                    {
                        'period': t.get('periodBegin'),
                        'median_price': t.get('medianSalePrice'),
                        'avg_price': t.get('avgSalePrice'),
                        'sale_count': t.get('saleCount'),
                        'median_sqft': t.get('medianSquareFeet')
                    } for t in trends
                ],
                'yoy_change_pct': yoy_change,
                'market_velocity': market_velocity
            }
            
        except Exception as e:
            raise Exception(f"Failed to get sales trends: {str(e)}")

    def get_sales_trends_v4(self, geo_id_v4: Optional[str] = None, interval: str = 'monthly',
                            start_year: Optional[int] = None, end_year: Optional[int] = None,
                            property_type: str = 'all', postal_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Get sales trends using ATTOM v4 transaction endpoint with geoIdv4.

        Docs example:
        https://api.gateway.attomdata.com/v4/transaction/salestrend?geoIdv4=...&interval=monthly&startyear=2020&endyear=2022&propertyType=all

        Args:
            geo_id_v4: Geo identifier (v4) string
            interval: 'monthly'|'quarterly'|'yearly'
            start_year: optional start year (int)
            end_year: optional end year (int)
            property_type: e.g., 'all'

        Returns:
            A dict with normalized trend fields when available, otherwise raw payload.
        """
        url = "https://api.gateway.attomdata.com/v4/transaction/salestrend"
        params: Dict[str, Any] = {
            'interval': interval
        }
        # Prefer explicit geoIdv4 when provided; otherwise try geoType/geoId using ZIP
        if geo_id_v4:
            # Correct v4 parameter name is geoIdV4 (capital V)
            params['geoIdV4'] = geo_id_v4
        elif postal_code:
            params['geoType'] = 'postalcode'
            params['geoId'] = str(postal_code)
        # Default to last 2 calendar years if not provided
        if start_year is None or end_year is None:
            now_year = datetime.utcnow().year
            start_year = now_year - 1
            end_year = now_year
        params['startyear'] = start_year
        params['endyear'] = end_year
        if property_type:
            params['propertyType'] = property_type

        try:
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            # Attempt to normalize common fields if present
            trends = data.get('salestrends') or data.get('trends') or data.get('data') or []
            latest = trends[0] if isinstance(trends, list) and trends else {}

            normalized = {
                'geo_id_v4': geo_id_v4,
                'interval': interval,
                'start_year': start_year,
                'end_year': end_year,
                'property_type': property_type,
                'postal_code': postal_code,
                'trends': trends,
                'latest': latest
            }
            return normalized
        except requests.exceptions.HTTPError as e:
            raise Exception(f"ATTOM v4 salestrend error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Failed to get v4 sales trends: {str(e)}")
    
    def lookup_geo_id_v4(self, name: str, geography_type_abbreviation: Optional[str] = None,
                         state_abbreviation: Optional[str] = None, page_size: int = 10) -> List[Dict[str, Any]]:
        """
        Look up ATTOM v4 geographies and return raw geography entries (including geoIdV4).

        Args:
            name: Free-text name like 'Cranford, NJ' or 'Union County, NJ'.
            geography_type_abbreviation: Optional filter (e.g., 'CI' for Postal City, 'CO' for County).

        Returns:
            List of geography dicts with keys like geoIdV4, geographyName, geographyTypeName, geographyTypeAbbreviation.
        """
        url = "https://api.gateway.attomdata.com/v4/location/lookup"
        params: Dict[str, Any] = {'name': name}
        if geography_type_abbreviation:
            params['geographyTypeAbbreviation'] = geography_type_abbreviation
        if state_abbreviation:
            params['stateAbbreviation'] = state_abbreviation
        if page_size:
            params['pageSize'] = page_size
        try:
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json() or {}
            return data.get('geographies') or []
        except requests.exceptions.HTTPError as e:
            raise Exception(f"ATTOM v4 location lookup error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Failed location lookup: {str(e)}")

    def find_geo_id_v4_for_area(self, city: Optional[str], state: Optional[str], county: Optional[str] = None) -> Optional[str]:
        """
        Derive a usable geoIdV4 for SalesTrends by trying City (Postal City, 'CI') then County ('CO').

        Returns the first matching geoIdV4 or None if none found.
        """
        # Try Postal City first
        try:
            if city and state:
                # Prefer separating stateAbbreviation for better matches
                geos = self.lookup_geo_id_v4(city, geography_type_abbreviation='CI', state_abbreviation=state)
                if geos:
                    return geos[0].get('geoIdV4')
        except Exception:
            pass
        # Then try County if provided
        try:
            if county and state:
                geos = self.lookup_geo_id_v4(county, geography_type_abbreviation='CO', state_abbreviation=state)
                if geos:
                    return geos[0].get('geoIdV4')
        except Exception:
            pass
        return None
    
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
