import os
import time
import pytest

from app.tasks.property_tasks import enrich_property_data_task
from app.utils.supabase_client import get_admin_db

pytestmark = pytest.mark.integration

RUN_E2E = bool(os.getenv("RUN_E2E"))

CRANFORD_ID = "03ba0ff3-62c9-4e18-928b-04cebeecb9d3"
NYC_ID = "c9df9967-2658-47bb-b395-6e7e0a16c3de"


def _get_property(prop_id: str):
    db = get_admin_db()
    res = db.table("properties").select("*").eq("id", prop_id).execute()
    return (res.data or [None])[0]


def _wait_for_status(prop_id: str, target: str, timeout_s: int = 360) -> bool:
    start = time.time()
    while time.time() - start < timeout_s:
        p = _get_property(prop_id)
        if p and p.get("status") == target:
            return True
        time.sleep(5)
    return False


@pytest.mark.skipif(not RUN_E2E, reason="E2E disabled. Set RUN_E2E=1 to run.")
def test_enrich_cranford_v4_trends_present_or_empty_but_structured():
    # Trigger enrichment and wait
    res = enrich_property_data_task.delay(CRANFORD_ID)
    out = res.get(timeout=480)
    assert out and out.get("status") == "success"
    assert _wait_for_status(CRANFORD_ID, "enrichment_complete", timeout_s=120)

    p = _get_property(CRANFORD_ID)
    assert p and p.get("status") == "enrichment_complete"
    ed = p.get("extracted_data") or {}
    att = ed.get("attom") or {}
    v4 = att.get("sales_trends_v4") or {}

    # Ensure v4 structure exists even if trends can be empty depending on coverage
    assert isinstance(v4, dict)
    assert v4.get("interval") in ("monthly", "quarterly", "yearly")
    assert v4.get("start_year") is not None
    assert v4.get("end_year") is not None
    assert "trends" in v4  # may be empty list

    # Ensure we produced a price estimate
    mi = ed.get("market_insights") or {}
    pe = mi.get("price_estimate") or {}
    assert "estimated_value" in pe


@pytest.mark.skipif(not RUN_E2E, reason="E2E disabled. Set RUN_E2E=1 to run.")
def test_enrich_nyc_price_and_trends_structure():
    res = enrich_property_data_task.delay(NYC_ID)
    out = res.get(timeout=480)
    assert out and out.get("status") == "success"
    assert _wait_for_status(NYC_ID, "enrichment_complete", timeout_s=120)

    p = _get_property(NYC_ID)
    assert p and p.get("status") == "enrichment_complete"
    ed = p.get("extracted_data") or {}

    # Price estimate should be present
    mi = ed.get("market_insights") or {}
    pe = mi.get("price_estimate") or {}
    assert "estimated_value" in pe

    # v4 trends structure should exist (may be empty depending on area coverage)
    att = ed.get("attom") or {}
    v4 = att.get("sales_trends_v4") or {}
    assert isinstance(v4, dict)
    assert v4.get("interval") in ("monthly", "quarterly", "yearly")
    assert v4.get("start_year") is not None
    assert v4.get("end_year") is not None
    assert "trends" in v4
