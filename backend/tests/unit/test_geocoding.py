import os
import json
import types
from importlib import reload
from unittest.mock import patch, Mock


def _fake_geocode_response():
    return {
        "status": "OK",
        "results": [
            {
                "address_components": [
                    {"long_name": "1-74A", "short_name": "1-74A", "types": ["street_number"]},
                    {"long_name": "Beach 118th Street", "short_name": "Beach 118th St", "types": ["route"]},
                    {"long_name": "Rockaway Park", "short_name": "Rockaway Park", "types": ["neighborhood", "political"]},
                    {"long_name": "Queens", "short_name": "Queens", "types": ["sublocality_level_1", "sublocality", "political"]},
                    {"long_name": "New York", "short_name": "NY", "types": ["administrative_area_level_1", "political"]},
                    {"long_name": "United States", "short_name": "US", "types": ["country", "political"]},
                    {"long_name": "11694", "short_name": "11694", "types": ["postal_code"]}
                ],
                "geometry": {
                    "location": {"lat": 40.5785298, "lng": -73.838068}
                }
            }
        ]
    }


def test_normalize_address_google_prefers_neighborhood_and_queens_fix():
    # Ensure the module reads GOOGLE_MAPS_API_KEY during import
    with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_key"}, clear=False):
        import app.utils.geocoding as geocoding
        reload(geocoding)

        # Mock requests.get to return our fake geocode payload
        with patch("app.utils.geocoding.requests.get") as mock_get:
            mock_resp = Mock()
            mock_resp.json.return_value = _fake_geocode_response()
            mock_resp.raise_for_status = Mock()
            mock_get.return_value = mock_resp

            result = geocoding.normalize_address("174 Beach 118th St Rockaway Park, NY 11694")

            # Queens hyphenated street number should be corrected using raw numeric + route
            assert result["street"] == "174 Beach 118th Street"
            # Prefer neighborhood over borough for NYC
            assert result["city"] in ("Rockaway Park", "Far Rockaway")
            assert result["state"] == "NY"
            assert result["zip"] == "11694"
            assert result["neighborhood"] in ("Rockaway Park", "Far Rockaway")
            assert isinstance(result["lat"], float)
            assert isinstance(result["lng"], float)
