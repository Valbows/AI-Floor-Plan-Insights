"""
Address normalization via Google Geocoding API

Outputs a best-effort structured address suitable for ATTOM queries.
"""
from __future__ import annotations
import os
import re
import requests
from typing import Dict, Optional

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("VITE_GOOGLE_MAPS_API_KEY")

GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

NYC_BOROUGHS = {"MANHATTAN", "BROOKLYN", "QUEENS", "BRONX", "STATEN ISLAND"}


def _component(components, type_name, use_short=False) -> Optional[str]:
    for c in components:
        if type_name in c.get("types", []):
            return c.get("short_name" if use_short else "long_name")
    return None


def _parse_street(components) -> Optional[str]:
    num = _component(components, "street_number")
    route = _component(components, "route")
    if num and route:
        return f"{num} {route}".strip()
    if route:
        return route
    return None


def _derive_city(components) -> Optional[str]:
    # General preference: locality, then sublocality; neighborhood handled separately for NYC
    locality = _component(components, "locality")
    if locality:
        return locality
    sublocality = _component(components, "sublocality_level_1")
    if sublocality:
        return sublocality
    neighborhood = _component(components, "neighborhood")
    if neighborhood:
        return neighborhood
    # Fallback: sometimes postal_town is present
    postal_town = _component(components, "postal_town")
    if postal_town:
        return postal_town
    # As last resort, use administrative_area_level_2 (county) if it's not just a borough keyword
    county = _component(components, "administrative_area_level_2")
    if county and county.upper() not in NYC_BOROUGHS:
        return county
    return None


def normalize_address(raw_address: str) -> Dict[str, Optional[str]]:
    """
    Normalize a raw address string to {street, city, state, zip, lat, lng}.
    Returns best-effort components; fields may be None if unavailable.
    """
    if not raw_address:
        return {"street": None, "city": None, "state": None, "zip": None, "lat": None, "lng": None, "neighborhood": None}

    # If API key missing, attempt a simple parse fallback
    if not GOOGLE_MAPS_API_KEY:
        # Very naive parse: "street, city, state ZIP"
        m = re.match(r"^(.*?),\s*([^,]+),\s*([A-Z]{2})(?:\s+(\d{5}))?$", raw_address.strip())
        street = m.group(1).strip() if m else raw_address
        city = m.group(2).strip() if m else None
        state = m.group(3).strip() if m else None
        zip_code = m.group(4).strip() if m and m.group(4) else None
        return {"street": street, "city": city, "state": state, "zip": zip_code, "lat": None, "lng": None, "neighborhood": None}

    try:
        resp = requests.get(GEOCODE_URL, params={"address": raw_address, "key": GOOGLE_MAPS_API_KEY}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "OK" or not data.get("results"):
            # Fall back to naive parse
            m = re.match(r"^(.*?),\s*([^,]+),\s*([A-Z]{2})(?:\s+(\d{5}))?$", raw_address.strip())
            street = m.group(1).strip() if m else raw_address
            city = m.group(2).strip() if m else None
            state = m.group(3).strip() if m else None
            zip_code = m.group(4).strip() if m and m.group(4) else None
            return {"street": street, "city": city, "state": state, "zip": zip_code, "lat": None, "lng": None, "neighborhood": None}

        result = data["results"][0]
        comps = result.get("address_components", [])
        street = _parse_street(comps) or raw_address
        city = _derive_city(comps)
        state = _component(comps, "administrative_area_level_1", use_short=True)
        zip_code = _component(comps, "postal_code")
        loc = result.get("geometry", {}).get("location", {})
        lat = loc.get("lat")
        lng = loc.get("lng")
        neighborhood = _component(comps, "neighborhood")

        # NYC improvement: prefer neighborhood name (e.g., Rockaway Park) over borough when available
        if city and city.upper() in NYC_BOROUGHS and neighborhood:
            city = neighborhood

        # Queens hyphenated house numbers: prefer raw leading number + route to avoid mismatches like '1-74A'
        try:
            route = _component(comps, "route")
            raw_num_match = re.match(r"^\s*(\d+)", raw_address.strip())
            if route and raw_num_match:
                raw_num = raw_num_match.group(1)
                # If parsed street number contains hyphen or letters, reconstruct with raw numeric + route
                street_num = _component(comps, "street_number") or ""
                if street_num and ("-" in street_num or re.search(r"[A-Za-z]", street_num)):
                    street = f"{raw_num} {route}"
        except Exception:
            pass

        return {"street": street, "city": city, "state": state, "zip": zip_code, "lat": lat, "lng": lng, "neighborhood": neighborhood}

    except Exception:
        # Graceful fallback
        m = re.match(r"^(.*?),\s*([^,]+),\s*([A-Z]{2})(?:\s+(\d{5}))?$", raw_address.strip())
        street = m.group(1).strip() if m else raw_address
        city = m.group(2).strip() if m else None
        state = m.group(3).strip() if m else None
        zip_code = m.group(4).strip() if m and m.group(4) else None
        return {"street": street, "city": city, "state": state, "zip": zip_code, "lat": None, "lng": None, "neighborhood": None}
