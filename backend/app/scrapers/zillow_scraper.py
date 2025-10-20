"""
Zillow Property Scraper
Scrapes property data from Zillow.com using Bright Data
"""

import re
import logging
import json
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
    STREET_ABBR = {
        'street': 'St', 'st': 'St',
        'avenue': 'Ave', 'ave': 'Ave',
        'road': 'Rd', 'rd': 'Rd',
        'drive': 'Dr', 'dr': 'Dr',
        'court': 'Ct', 'ct': 'Ct',
        'boulevard': 'Blvd', 'blvd': 'Blvd',
        'place': 'Pl', 'pl': 'Pl',
        'lane': 'Ln', 'ln': 'Ln',
        'terrace': 'Ter', 'ter': 'Ter',
        'parkway': 'Pkwy', 'pkwy': 'Pkwy'
    }

    def _to_ordinal(self, n_str: str) -> str:
        try:
            n = int(re.sub(r"[^0-9]", "", n_str))
        except Exception:
            return n_str
        if 10 <= (n % 100) <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"

    def _queens_detail_candidates(self, address: str, city: str, state: str, zip_code: str | None = None) -> list[str]:
        """Build likely Zillow homedetails paths for Queens-style addresses.
        Example: '43-52 169 Street' -> '4352-169th-St'
        """
        addr = address.strip()
        # Match 'xx-yy <num> <type>'
        m = re.match(r"^(\d+)-(\d+)\s+(\d+)\s+([A-Za-z]+)", addr)
        candidates = []
        if m:
            part1, part2, street_num, street_type = m.groups()
            house = f"{part1}{part2}"  # 43-52 -> 4352
            ordinal = self._to_ordinal(street_num)  # 169 -> 169th
            abbr = self.STREET_ABBR.get(street_type.lower(), street_type.title())
            city_slug = city.replace(' ', '-')
            core = f"{house}-{ordinal}-{abbr}-{city_slug}-{state}"
            if zip_code:
                candidates.append(f"{self.BASE_URL}/homedetails/{core}-{zip_code}/")
            candidates.append(f"{self.BASE_URL}/homedetails/{core}/")
        return candidates

    def _get_canonical_or_self(self, html: str, page_url: str) -> str:
        try:
            soup = self.parse_html(html)
            link = soup.find('link', rel='canonical')
            href = (link and link.get('href')) or None
            if href and href.startswith('http'):
                return href
        except Exception:
            pass
        return page_url
    
    async def search_property(self, address: str, city: str, state: str, zip_code: Optional[str] = None) -> Dict[str, Any]:
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

            # 1) Try Queens/NYC homedetails candidates first (more reliable for these addresses)
            candidates = self._queens_detail_candidates(address, city, state, zip_code=zip_code)
            for cand in candidates:
                try:
                    resp = await self.client.fetch(
                        cand,
                        wait_for='div[data-test="home-details"]',
                        wait_timeout=30000,
                        extra_params={
                            'transparent_status_code': 'true',
                            'stealth_proxy': 'true',
                            'premium_proxy': None,
                            'block_resources': 'false',
                            'device': 'desktop'
                        },
                        allow_failure=True
                    )
                    html = (resp.text or '')
                    # Follow canonical if present
                    canon = self._get_canonical_or_self(html, cand)
                    if canon != cand:
                        resp2 = await self.client.fetch(
                            canon,
                            wait_for='div[data-test="home-details"]',
                            wait_timeout=30000,
                            extra_params={
                                'transparent_status_code': 'true',
                                'stealth_proxy': 'true',
                                'premium_proxy': None,
                                'block_resources': 'false',
                                'device': 'desktop'
                            },
                            allow_failure=True
                        )
                        html = (resp2.text or '')
                    soup = self.parse_html(html)
                    property_data = self._parse_property_details(soup)
                    property_data['listing_url'] = canon
                    if property_data:
                        return self.normalize_property_data(property_data)
                except Exception:
                    continue
            
            # 2) Try structured extraction on search page
            if not self.client:
                raise Exception("Scraping client not initialized")
            try:
                data = await self.client.extract_json(
                    search_url,
                    extract_rules={
                        'price': "span[data-test='property-card-price']",
                        'address': "address[data-test='property-card-addr']",
                        'listing_url': "a[data-test='property-card-link']::attr(href)"
                    },
                    wait_for='article[data-test="property-card"]',
                    wait_timeout=15000
                )
                price = (data or {}).get('price')
                addr = (data or {}).get('address')
                link = (data or {}).get('listing_url')
                if link and link.startswith('/'):
                    link = f"{self.BASE_URL}{link}"
                if price or addr or link:
                    property_data = {
                        'price': price,
                        'address': addr,
                        'listing_url': link
                    }
                    # If any field present, return normalized quickly
                    return self.normalize_property_data(property_data)
            except Exception:
                # Fall through to tolerant HTML parsing
                pass

            # Use ScrapingBee tolerant fetch to retrieve body even on non-2xx as fallback
            resp = await self.client.fetch(
                search_url,
                wait_for='article[data-test="property-card"]',
                wait_timeout=30000,
                extra_params={
                    'transparent_status_code': 'true',
                    'stealth_proxy': 'true',
                    'premium_proxy': None,
                    'block_resources': 'false',
                    'device': 'desktop'
                },
                allow_failure=True
            )
            html = (resp.text or '')
            
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
                raise Exception("Scraping client not initialized")
            
            resp = await self.client.fetch(
                property_url,
                wait_for='div[data-test="home-details"]',
                wait_timeout=15000,
                extra_params={'transparent_status_code': 'true'},
                allow_failure=True
            )
            html = (resp.text or '')
            
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
            
            # Try parsing JSON-LD structured data for robust fields
            try:
                scripts = soup.find_all('script', type='application/ld+json')
                def absorb(obj):
                    if not isinstance(obj, dict):
                        return
                    # Address
                    addr = obj.get('address')
                    if isinstance(addr, dict) and not data.get('address'):
                        parts = [addr.get('streetAddress'), addr.get('addressLocality'), addr.get('addressRegion'), addr.get('postalCode')]
                        data['address'] = ' '.join([p for p in parts if p])
                    # Offers/price
                    offers = obj.get('offers')
                    if isinstance(offers, dict) and not data.get('price'):
                        price = offers.get('price') or offers.get('lowPrice') or offers.get('highPrice')
                        if price:
                            data['price'] = str(price)
                    # Beds/Baths/Sqft if available
                    if not data.get('bedrooms') and isinstance(obj.get('numberOfRooms'), (int, float)):
                        data['bedrooms'] = str(int(obj['numberOfRooms']))
                    if not data.get('bathrooms') and isinstance(obj.get('numberOfBathroomsTotal'), (int, float)):
                        data['bathrooms'] = str(obj['numberOfBathroomsTotal'])
                    if not data.get('square_feet'):
                        sqft = obj.get('floorSize')
                        if isinstance(sqft, dict):
                            val = sqft.get('value')
                            if val:
                                data['square_feet'] = str(val)
                for s in scripts:
                    try:
                        raw = s.string or s.text or ''
                        if not raw:
                            continue
                        obj = json.loads(raw)
                        if isinstance(obj, list):
                            for o in obj:
                                absorb(o)
                        elif isinstance(obj, dict):
                            absorb(obj)
                    except Exception:
                        continue
            except Exception:
                pass
            
            # Fallback: Parse __NEXT_DATA__ (Zillow Next.js embedded JSON)
            try:
                def deep_get_any(o, keys):
                    if isinstance(o, dict):
                        for k in keys:
                            if k in o and o.get(k) not in (None, ''):
                                return o.get(k)
                        for v in o.values():
                            r = deep_get_any(v, keys)
                            if r is not None:
                                return r
                    elif isinstance(o, list):
                        for v in o:
                            r = deep_get_any(v, keys)
                            if r is not None:
                                return r
                    return None
                next_script = soup.find('script', id='__NEXT_DATA__')
                if next_script and (next_script.string or next_script.text):
                    obj = json.loads(next_script.string or next_script.text)
                    # Price-related
                    price_val = deep_get_any(obj, ['price', 'priceRaw', 'unformattedPrice', 'zestimate', 'homePrice', 'priceValue'])
                    if price_val and not data.get('price'):
                        data['price'] = str(price_val)
                    # Beds
                    beds_val = deep_get_any(obj, ['bedrooms', 'beds', 'bedroomsMax', 'bedroomsMin'])
                    if beds_val and not data.get('bedrooms'):
                        try:
                            data['bedrooms'] = str(int(float(beds_val)))
                        except Exception:
                            data['bedrooms'] = str(beds_val)
                    # Baths
                    baths_val = deep_get_any(obj, ['bathrooms', 'baths', 'numberOfBathroomsTotal', 'bathroomsMax', 'bathroomsMin'])
                    if baths_val and not data.get('bathrooms'):
                        data['bathrooms'] = str(baths_val)
                    # Sqft
                    sqft_val = deep_get_any(obj, ['livingArea', 'livingAreaValue', 'sqft', 'homeSize', 'area', 'universalsize'])
                    if sqft_val and not data.get('square_feet'):
                        data['square_feet'] = str(sqft_val)
                    # Address
                    street = deep_get_any(obj, ['streetAddress', 'street'])
                    city = deep_get_any(obj, ['city', 'addressLocality'])
                    state = deep_get_any(obj, ['state', 'addressRegion'])
                    zipcode = deep_get_any(obj, ['zipcode', 'postalCode', 'zip'])
                    if not data.get('address') and (street or city or state or zipcode):
                        parts = [street, city, state, zipcode]
                        data['address'] = ' '.join([str(p) for p in parts if p])
            except Exception:
                pass

            try:
                full_text = soup.get_text(" ", strip=True)
            except Exception:
                full_text = ""
            if data.get('zestimate') and not data.get('price'):
                # Extract numeric from zestimate like 'Zestimate: $354,200'
                m = re.search(r"\$\s*([\d,]+)", str(data.get('zestimate')))
                if m:
                    data['price'] = m.group(1)
                else:
                    # Fallback to any $number in page text
                    m2 = re.search(r"\$\s*([\d,]+)", full_text)
                    if m2:
                        data['price'] = m2.group(1)
            if not data.get('bedrooms'):
                m = re.search(r"(\d+)\s*bd\b", full_text, re.IGNORECASE)
                if m:
                    data['bedrooms'] = m.group(1)
            if not data.get('bathrooms'):
                m = re.search(r"(\d+\.?\d*)\s*ba\b", full_text, re.IGNORECASE)
                if m:
                    data['bathrooms'] = m.group(1)
            if not data.get('square_feet'):
                m = re.search(r"([\d,]+)\s*sq\s*ft\b", full_text, re.IGNORECASE)
                if m:
                    data['square_feet'] = m.group(1)
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
