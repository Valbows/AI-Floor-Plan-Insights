"""
ScrapingBee HTML API Client (Async)

Replaces Bright Data usage for scraping Zillow, Redfin, and StreetEasy pages.
Uses ScrapingBee's HTML API with JavaScript rendering, premium/stealth proxies,
wait_for selector, sessions, and geolocation.

Docs: https://www.scrapingbee.com/documentation/
"""
from __future__ import annotations

import os
import json
import random
import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class ScrapingBeeClient:
    """
    Async client wrapper around ScrapingBee HTML API.

    Key features used:
    - JavaScript rendering (render_js=True by default)
    - wait_for CSS/XPath selector
    - premium_proxy with country_code (US)
    - optional stealth_proxy fallback for hard targets
    - session_id stickiness (5 minutes)
    - device=desktop, block_ads=true, block_resources=true for speed
    - timeout in milliseconds (API range: 1000..140000)

    Methods mirror the small subset we used from BrightDataClient so existing
    scrapers (Zillow/Redfin/StreetEasy) can call `scrape_page()` unchanged.
    """

    BASE_URL = "https://app.scrapingbee.com/api/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        country_code: str = "us",
        premium_proxy: bool = True,
        stealth_proxy_fallback: bool = True,
        device: str = "desktop",
        block_ads: bool = True,
        block_resources: bool = True,
        render_js: bool = True,
        default_timeout_ms: int = 45000,
        session_id: Optional[int] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("SCRAPINGBEE_API_KEY")
        if not self.api_key:
            raise ValueError("SCRAPINGBEE_API_KEY is required")

        self.country_code = country_code
        self.premium_proxy = premium_proxy
        self.stealth_proxy_fallback = stealth_proxy_fallback
        self.device = device
        self.block_ads = block_ads
        self.block_resources = block_resources
        self.render_js = render_js
        self.default_timeout_ms = max(1000, min(default_timeout_ms, 140000))
        self.session_id = (
            session_id if session_id is not None else random.randint(1, 10_000_000)
        )

        self._client: Optional[httpx.AsyncClient] = None

    async def connect(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
            logger.info("✅ ScrapingBee client ready (async)")

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _base_params(self, url: str, wait_for: Optional[str], wait_timeout: int) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "api_key": self.api_key,
            "url": url,
            # JS rendering enabled by default on ScrapingBee; keep explicit for clarity
            "render_js": "true" if self.render_js else "false",
            # Speed-ups and realism
            "block_ads": "true" if self.block_ads else "false",
            "block_resources": "true" if self.block_resources else "false",
            "device": self.device,
            # Geolocation/proxy, sites like Zillow/Redfin/StreetEasy generally require premium proxy
            "premium_proxy": "true" if self.premium_proxy else None,
            "country_code": self.country_code,
            # Stick to same IP for a short sequence (search -> detail)
            "session_id": str(self.session_id),
            # Overall request timeout (ms)
            "timeout": str(max(1000, min(int(wait_timeout or self.default_timeout_ms), 140000))),
        }
        if wait_for:
            params["wait_for"] = wait_for
        # Clean None values to avoid leaking invalid params
        return {k: v for k, v in params.items() if v is not None}

    async def fetch(
        self,
        url: str,
        wait_for: Optional[str] = None,
        wait_timeout: int = 10000,
        extra_params: Optional[Dict[str, Any]] = None,
        allow_failure: bool = False,
    ) -> httpx.Response:
        """
        Low-level fetch with support for custom ScrapingBee params and optional non-raising behavior.
        """
        if self._client is None:
            await self.connect()
        params = self._base_params(url, wait_for, wait_timeout)
        if extra_params:
            params.update({k: v for k, v in extra_params.items() if v is not None})
        try:
            assert self._client is not None
            logger.info(f"ScrapingBee: GET {url} (custom)")
            resp = await self._client.get(self.BASE_URL, params=params)
            if not allow_failure:
                resp.raise_for_status()
            return resp
        except httpx.HTTPError as e:
            # Stealth retry path
            if self.stealth_proxy_fallback:
                try:
                    logger.warning(
                        f"Primary request failed ({e}); retrying with stealth_proxy for {url}"
                    )
                    stealth_params = dict(params)
                    stealth_params.pop("premium_proxy", None)
                    stealth_params["stealth_proxy"] = "true"
                    stealth_params.pop("timeout", None)
                    resp2 = await self._client.get(self.BASE_URL, params=stealth_params)
                    if not allow_failure:
                        resp2.raise_for_status()
                    return resp2
                except Exception as e2:
                    if allow_failure and isinstance(e2, httpx.HTTPError):
                        return e2.response  # return best-effort response
                    raise RuntimeError(
                        f"ScrapingBee failed (primary+stealth): {e2}"
                    ) from e
            if allow_failure and isinstance(e, httpx.HTTPError):
                return e.response
            raise

    async def scrape_page(
        self,
        url: str,
        wait_for: Optional[str] = None,
        wait_timeout: int = 10000,
    ) -> str:
        """
        Fetch rendered HTML for a URL.

        Args:
            url: target URL
            wait_for: CSS/XPath selector to wait for
            wait_timeout: desired overall timeout in ms (ScrapingBee `timeout`)
        """
        if self._client is None:
            await self.connect()

        try:
            assert self._client is not None
            params = self._base_params(url, wait_for, wait_timeout)
            logger.info(f"ScrapingBee: GET {url}")
            resp = await self._client.get(self.BASE_URL, params=params)
            # ScrapingBee returns 500 for many non-2xx target statuses unless we use transparent_status_code
            resp.raise_for_status()
            return resp.text
        except httpx.HTTPError as e:
            # One-shot stealth retry for harder targets
            if self.stealth_proxy_fallback:
                try:
                    logger.warning(
                        f"Primary request failed ({e}); retrying with stealth_proxy for {url}"
                    )
                    stealth_params = dict(params)
                    stealth_params.pop("premium_proxy", None)
                    stealth_params["stealth_proxy"] = "true"
                    # Known limitation: timeout not supported with stealth_proxy
                    stealth_params.pop("timeout", None)
                    resp2 = await self._client.get(self.BASE_URL, params=stealth_params)
                    resp2.raise_for_status()
                    return resp2.text
                except Exception as e2:
                    raise RuntimeError(
                        f"ScrapingBee failed (primary+stealth): {e2}"
                    ) from e
            raise RuntimeError(f"ScrapingBee failed: {e}")

    # Optional helper when we want JSON extraction server-side
    async def extract_json(
        self,
        url: str,
        extract_rules: Dict[str, str],
        wait_for: Optional[str] = None,
        wait_timeout: int = 10000,
    ) -> Dict[str, Any]:
        if self._client is None:
            await self.connect()
        params: Dict[str, Any] = {
            "api_key": self.api_key,
            "url": url,
            "render_js": "true" if self.render_js else "false",
            "json_response": "true",
            "extract_rules": json.dumps(extract_rules),
            "device": self.device,
            "premium_proxy": "true" if self.premium_proxy else None,
            "country_code": self.country_code,
            "session_id": str(self.session_id),
            "timeout": str(max(1000, min(int(wait_timeout or self.default_timeout_ms), 140000))),
        }
        if wait_for:
            params["wait_for"] = wait_for
        params = {k: v for k, v in params.items() if v is not None}
        try:
            assert self._client is not None
            resp = await self._client.get(self.BASE_URL, params=params)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            # Attempt stealth proxy fallback for hard targets
            if self.stealth_proxy_fallback:
                try:
                    stealth_params = dict(params)
                    stealth_params.pop("premium_proxy", None)
                    stealth_params["stealth_proxy"] = "true"
                    # Remove timeout (unsupported with stealth)
                    stealth_params.pop("timeout", None)
                    assert self._client is not None
                    resp2 = await self._client.get(self.BASE_URL, params=stealth_params)
                    resp2.raise_for_status()
                    return resp2.json()
                except Exception as e2:
                    raise RuntimeError(
                        f"ScrapingBee JSON extraction failed (primary+stealth): {e2}"
                    ) from e
            raise RuntimeError(f"ScrapingBee JSON extraction failed: {e}")
