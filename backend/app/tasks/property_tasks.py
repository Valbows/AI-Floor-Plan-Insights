"""
Celery Tasks for Property Processing
Handles asynchronous floor plan analysis and enrichment
"""

from app import celery
from app.utils.supabase_client import get_admin_db
from app.agents.floor_plan_analyst import FloorPlanAnalyst
import requests
from app.clients.attom_client import AttomAPIClient
from app.utils.geocoding import normalize_address
import re
import os
import asyncio


@celery.task(name='process_floor_plan', bind=True, max_retries=3)
def process_floor_plan_task(self, property_id: str):
    """
    Asynchronous task to analyze a floor plan image
    
    Steps:
    1. Fetch property from database
    2. Download floor plan image from Supabase Storage
    3. Run AI Agent #1 (Floor Plan Analyst)
    4. Update property with extracted data
    5. Update status to 'parsing_complete'
    
    Args:
        property_id: UUID of the property to process
    
    Returns:
        dict: Processing result with status and data
    """
    try:
        print(f"Starting floor plan analysis for property {property_id}")
        
        # Get database client
        db = get_admin_db()
        
        # Fetch property
        result = db.table('properties').select('*').eq('id', property_id).execute()
        
        if not result.data:
            raise ValueError(f"Property {property_id} not found")
        
        property_record = result.data[0]
        
        # Check if image exists
        if not property_record.get('image_url'):
            raise ValueError(f"Property {property_id} has no floor plan image")
        
        # Update status to indicate processing has started
        try:
            db.table('properties').update({
                'status': 'processing'
            }).eq('id', property_id).execute()
        except Exception:
            pass
        
        # Download floor plan image from Storage
        image_path = property_record['image_storage_path']
        print(f"Downloading floor plan from storage: {image_path}")
        
        # Use Supabase client to download from private bucket
        from app.utils.supabase_client import FLOOR_PLAN_BUCKET
        storage = db.storage
        image_bytes = storage.from_(FLOOR_PLAN_BUCKET).download(image_path)
        
        print(f"Downloaded {len(image_bytes)} bytes")
        
        # Initialize Floor Plan Analyst
        analyst = FloorPlanAnalyst()
        
        # Analyze floor plan
        print(f"Analyzing floor plan with AI Agent #1...")
        extracted_data = analyst.analyze_floor_plan(image_bytes=image_bytes)
        
        print(f"Extracted data: {extracted_data}")
        
        # Merge with existing extracted_data, preserving non-empty values from form
        current_data = property_record.get('extracted_data', {})
        
        # Keep address from form if AI didn't extract one
        if 'address' in current_data and current_data['address'] and not extracted_data.get('address'):
            extracted_data['address'] = current_data['address']
        
        merged_data = {**current_data, **extracted_data}
        
        # Update property with extracted data
        db.table('properties').update({
            'extracted_data': merged_data,
            'status': 'parsing_complete'
        }).eq('id', property_id).execute()
        
        print(f"Floor plan analysis complete for property {property_id}")
        
        return {
            'status': 'success',
            'property_id': property_id,
            'extracted_data': extracted_data
        }
        
    except Exception as e:
        print(f"Error processing floor plan for property {property_id}: {str(e)}")
        
        # Update property status to failed
        try:
            db = get_admin_db()
            db.table('properties').update({
                'status': 'failed',
                'extracted_data': {
                    'error': str(e),
                    'task_id': self.request.id
                }
            }).eq('id', property_id).execute()
        except Exception as update_error:
            print(f"Failed to update error status: {update_error}")
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery.task(name='enrich_property_data', bind=True, max_retries=3)
def enrich_property_data_task(self, property_id: str):
    """
    Asynchronous task to enrich property with market insights
    
    Uses AI Agent #2 (Market Insights Analyst) to:
    1. Fetch property data from database
    2. Query CoreLogic API for comps and AVM
    3. Run AI market analysis
    4. Generate price estimate and investment insights
    5. Update property with market_insights
    6. Update status to 'enrichment_complete'
    
    Args:
        property_id: UUID of the property to enrich
    """
    try:
        print(f"Enriching property data for {property_id}")
        
        # Get database client
        db = get_admin_db()
        
        # Fetch property
        result = db.table('properties').select('*').eq('id', property_id).execute()
        
        if not result.data:
            raise ValueError(f"Property {property_id} not found")
        
        property_record = result.data[0]
        
        # Get extracted data from Agent #1
        extracted_data = property_record.get('extracted_data', {})
        address = extracted_data.get('address', '')
        
        if not address:
            raise ValueError(f"Property {property_id} has no address for market analysis")
        
        # Update status to indicate enrichment has started (use allowed status)
        db.table('properties').update({
            'status': 'processing'
        }).eq('id', property_id).execute()

        attom_bundle = {}
        try:
            client = AttomAPIClient()
            # Normalize address for structured ATTOM queries
            norm = normalize_address(address)
            street = (norm.get('street') or address).strip()
            city_norm = (norm.get('city') or '').strip() or None
            state_norm = (norm.get('state') or '').strip() or None
            zip_norm = (norm.get('zip') or '').strip() or None
            print(f"[ATTOM] Normalized address => street='{street}', city='{city_norm}', state='{state_norm}', zip='{zip_norm}'")

            # Use structured search when possible; fallback to unstructured
            try:
                # Strip unit/suite designators from street for ATTOM matching
                street_clean = re.sub(r"\s+(apt|unit|ste|suite|bldg|fl|floor|#)\b.*$", "", street, flags=re.IGNORECASE).strip()
                if city_norm and state_norm:
                    prop_core = client.search_property(street_clean, city=city_norm, state=state_norm, zip_code=zip_norm)
                else:
                    prop_core = client.search_property(street_clean)
            except Exception as e:
                print(f"[ATTOM] Structured search failed ({e}); retrying with raw address string")
                prop_core = None
                try:
                    address_clean = re.sub(r"\s+(apt|unit|ste|suite|bldg|fl|floor|#)\b.*$", "", address, flags=re.IGNORECASE).strip()
                    prop_core = client.search_property(address_clean)
                except Exception as e2:
                    print(f"[ATTOM] Raw address search failed: {e2}")
                    prop_core = None

            # Fallback: proximity search by lat/lng if no property found
            if not prop_core or not prop_core.get('attom_id'):
                lat, lng = norm.get('lat'), norm.get('lng')
                if lat and lng:
                    print("[ATTOM] Attempting proximity fallback via expandedprofile (lat/lng)")
                    nearby = client.get_nearby_properties_by_latlng(lat, lng, radius_miles=0.2, max_results=10)
                    # Prefer a candidate with matching ZIP, else take the closest
                    candidate = None
                    if nearby:
                        if zip_norm:
                            for p in nearby:
                                if str(p.get('zip')).strip() == str(zip_norm):
                                    candidate = p
                                    break
                        candidate = candidate or (nearby[0] if nearby else None)
                    if candidate:
                        prop_core = candidate
                        print(f"[ATTOM] Proximity fallback matched: attom_id={prop_core.get('attom_id')} line1='{prop_core.get('address')}' zip='{prop_core.get('zip')}'")
                    else:
                        print("[ATTOM] Proximity fallback found no candidates")

            attom_id = prop_core.get('attom_id')
            details = None
            if attom_id:
                details = client.get_property_details(attom_id)
            avm = None
            try:
                city = city_norm or prop_core.get('city')
                state = state_norm or prop_core.get('state')
                zip_code = zip_norm or prop_core.get('zip')
                if city and state:
                    avm_street = street_clean if 'street_clean' in locals() else (street or prop_core.get('address') or address)
                    avm = client.get_avm(avm_street, city, state, zip_code=zip_code)
            except Exception:
                avm = None
            area_stats = None
            try:
                zip_for_area = prop_core.get('zip') or zip_norm
                if zip_for_area:
                    area_stats = client.get_area_stats(zip_for_area)
            except Exception:
                area_stats = None
            # Comparables (deterministic) – fetch even if LLM omits
            comps = None
            try:
                city_for_comps = city_norm or prop_core.get('city')
                state_for_comps = state_norm or prop_core.get('state')
                if city_for_comps and state_for_comps:
                    comps_address = street_clean if 'street_clean' in locals() else (street or prop_core.get('address') or address)
                    comps = client.get_comparables(comps_address, city_for_comps, state_for_comps, radius_miles=0.5, max_results=10)
            except Exception:
                comps = None
            # ATTOM sales trends
            # Prefer v4 via geoIdv4; resolve geoIdv4 from city/county when not explicitly provided
            sales_trends_v4 = None
            sales_trends_zip = None
            geoid_v4 = os.getenv('ATTOM_GEOID_V4')
            # Compute ZIP early so we can fallback even if v4 is configured
            zip_for_trends = prop_core.get('zip') or zip_norm
            # Resolve a regional geoIdV4 when not explicitly configured
            city_for_geo = city_norm or prop_core.get('city')
            state_for_geo = state_norm or prop_core.get('state')
            county_for_geo = (prop_core or {}).get('county')
            resolved_geo_v4 = None
            # Prefer per-area resolution; if none found, use env override
            if not resolved_geo_v4:
                try:
                    resolved_geo_v4 = client.find_geo_id_v4_for_area(city_for_geo, state_for_geo, county_for_geo)
                except Exception:
                    resolved_geo_v4 = None
            if not resolved_geo_v4 and geoid_v4:
                resolved_geo_v4 = geoid_v4
            if resolved_geo_v4:
                v4_has_trends = False
                try:
                    sales_trends_v4 = client.get_sales_trends_v4(
                        geo_id_v4=resolved_geo_v4,
                        interval='monthly',
                        property_type='all'
                    )
                    v4_has_trends = bool(sales_trends_v4) and bool(sales_trends_v4.get('trends')) and isinstance(sales_trends_v4.get('trends'), list)
                    print(f"[ATTOM] v4 SalesTrends fetched: {bool(sales_trends_v4)} (has_trends={v4_has_trends}) for geoIdv4={resolved_geo_v4}")
                except Exception as e:
                    print(f"[ATTOM] v4 salestrend error: {e}")
                    sales_trends_v4 = None
                    v4_has_trends = False
                # Fallback to County if city-level v4 produced no usable trends
                if not v4_has_trends and county_for_geo and state_for_geo:
                    try:
                        geos = client.lookup_geo_id_v4(f"{county_for_geo}, {state_for_geo}", geography_type_abbreviation='CO')
                        if geos:
                            alt_geo = geos[0].get('geoIdV4')
                            if alt_geo:
                                sales_trends_v4 = client.get_sales_trends_v4(
                                    geo_id_v4=alt_geo,
                                    interval='monthly', property_type='all'
                                )
                                v4_has_trends = bool(sales_trends_v4) and bool(sales_trends_v4.get('trends')) and isinstance(sales_trends_v4.get('trends'), list)
                                print(f"[ATTOM] v4 County SalesTrends fetched: {bool(sales_trends_v4)} (has_trends={v4_has_trends}) for county={county_for_geo}")
                    except Exception as e:
                        print(f"[ATTOM] v4 county salestrend error: {e}")
                if not v4_has_trends and zip_for_trends:
                    try:
                        print(f"[ATTOM] v4 trends empty or unavailable; attempting legacy ZIP fallback for zip={zip_for_trends}")
                        sales_trends_zip = client.get_sales_trends(str(zip_for_trends), interval='monthly')
                        print(f"[ATTOM] ZIP SalesTrends fetched (fallback): {bool(sales_trends_zip)} for zip={zip_for_trends}")
                    except Exception as e:
                        print(f"[ATTOM] ZIP salestrend error (fallback): {e}")
            else:
                # Resolve geoIdV4 dynamically when no explicit v4 id configured
                try:
                    v4_has_trends = False
                    city_for_geo = city_norm or prop_core.get('city')
                    state_for_geo = state_norm or prop_core.get('state')
                    county_for_geo = (prop_core or {}).get('county')
                    resolved_geo_v4 = None
                    try:
                        resolved_geo_v4 = client.find_geo_id_v4_for_area(city_for_geo, state_for_geo, county_for_geo)
                    except Exception:
                        resolved_geo_v4 = None
                    if resolved_geo_v4:
                        sales_trends_v4 = client.get_sales_trends_v4(
                            geo_id_v4=resolved_geo_v4,
                            interval='monthly', property_type='all'
                        )
                        v4_has_trends = bool(sales_trends_v4) and bool(sales_trends_v4.get('trends')) and isinstance(sales_trends_v4.get('trends'), list)
                        print(f"[ATTOM] v4 SalesTrends fetched: {bool(sales_trends_v4)} (has_trends={v4_has_trends}) for geoIdv4={resolved_geo_v4}")
                    # County fallback
                    if not v4_has_trends and county_for_geo and state_for_geo:
                        try:
                            geos = client.lookup_geo_id_v4(f"{county_for_geo}, {state_for_geo}", geography_type_abbreviation='CO')
                            if geos:
                                alt_geo = geos[0].get('geoIdV4')
                                if alt_geo:
                                    sales_trends_v4 = client.get_sales_trends_v4(
                                        geo_id_v4=alt_geo,
                                        interval='monthly', property_type='all'
                                    )
                                    v4_has_trends = bool(sales_trends_v4) and bool(sales_trends_v4.get('trends')) and isinstance(sales_trends_v4.get('trends'), list)
                                    print(f"[ATTOM] v4 County SalesTrends fetched: {bool(sales_trends_v4)} (has_trends={v4_has_trends}) for county={county_for_geo}")
                        except Exception as e:
                            print(f"[ATTOM] v4 county salestrend error: {e}")
                    # Legacy ZIP fallback
                    if not v4_has_trends and zip_for_trends:
                        try:
                            sales_trends_zip = client.get_sales_trends(str(zip_for_trends), interval='monthly')
                            print(f"[ATTOM] ZIP SalesTrends fetched: {bool(sales_trends_zip)} for zip={zip_for_trends}")
                        except Exception as e:
                            print(f"[ATTOM] ZIP salestrend error: {e}")
                except Exception as e:
                    print(f"[ATTOM] SalesTrends resolution error: {e}")
            # Build parcel summary (non-geometry) from details when available
            parcel = None
            try:
                if details:
                    lot = (details or {}).get('lot', {}) or {}
                    area = (details or {}).get('area', {}) or {}
                    identifier = (details or {}).get('identifier', {}) or {}
                    location = (details or {}).get('location', {}) or {}
                    geo = (location.get('latitude'), location.get('longitude')) if location else (None, None)
                    parcel = {
                        'apn': identifier.get('apn') or prop_core.get('apn'),
                        'fips': identifier.get('fips') or prop_core.get('fips'),
                        'lot_number': lot.get('lotnum'),
                        'lot_depth': lot.get('depth'),
                        'lot_frontage': lot.get('frontage'),
                        'lot_size_acres': lot.get('lotsize1'),
                        'lot_size_sqft': lot.get('lotsize2'),
                        'zoning': area.get('zoning'),
                        'county_use': area.get('countyuse1') or area.get('countyuse2'),
                        'muncode': area.get('muncode'),
                        'geo': {
                            'latitude': location.get('latitude'),
                            'longitude': location.get('longitude')
                        }
                    }
            except Exception:
                parcel = None
            print(f"[ATTOM] Property found: {bool(prop_core)} attom_id={attom_id}")
            print(f"[ATTOM] Details present: {bool(details)} | AVM present: {bool(avm)} | Area present: {bool(area_stats)}")
            print(f"[ATTOM] SalesTrends v4 present: {bool(sales_trends_v4)} | ZIP present: {bool(sales_trends_zip)}")
            attom_bundle = {
                'property': prop_core,
                'details': details,
                'avm': avm,
                'area_stats': area_stats,
                'sales_trends_v4': sales_trends_v4,
                'sales_trends': sales_trends_zip,
                'parcel': parcel,
                'comparables': comps
            }
            current_data = property_record.get('extracted_data', {}) or {}
            ed = current_data
            if not ed.get('square_footage'):
                try:
                    ed['square_footage'] = (
                        (prop_core or {}).get('square_feet')
                        or (((details or {}).get('building') or {}).get('size') or {}).get('universalsize')
                        or ed.get('square_footage')
                    )
                except Exception:
                    pass
            if not ed.get('bedrooms') and (prop_core or {}).get('bedrooms'):
                ed['bedrooms'] = (prop_core or {}).get('bedrooms')
            if not ed.get('bathrooms') and (prop_core or {}).get('bathrooms'):
                ed['bathrooms'] = (prop_core or {}).get('bathrooms')
            if not ed.get('year_built') and (prop_core or {}).get('year_built'):
                ed['year_built'] = (prop_core or {}).get('year_built')
            ed['attom'] = attom_bundle

            # Attempt Multi-Source web scraping (Zillow/Redfin/StreetEasy) and persist aggregated result
            try:
                from app.scrapers.multi_source_scraper import MultiSourceScraper
                ms_result = None
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                async def run_ms():
                    async with MultiSourceScraper() as ms:
                        return await ms.scrape_property(street, city_norm or (prop_core or {}).get('city') or '', state_norm or (prop_core or {}).get('state') or '')
                ms_result = loop.run_until_complete(run_ms())
                loop.close()
                if ms_result:
                    ed['multi_source'] = ms_result
            except Exception as e:
                print(f"[SCRAPE] MultiSource failed: {e}")

            db.table('properties').update({
                'extracted_data': ed
            }).eq('id', property_id).execute()
            # ensure local view reflects latest enriched extracted_data
            extracted_data = ed
        except Exception:
            pass

        from app.agents.market_insights_analyst import MarketInsightsAnalyst
        analyst = MarketInsightsAnalyst()
        
        # Run market analysis
        print(f"Running market analysis with AI Agent #2...")
        market_insights = analyst.analyze_property(
            address=address,
            property_data=extracted_data
        )
        
        print(f"Market insights generated: Price estimate ${market_insights.get('price_estimate', {}).get('estimated_value', 0):,}")

        # Merge market insights into extracted_data
        current_data = property_record.get('extracted_data', {})
        # If LLM omitted comps, attach ATTOM comps we fetched
        try:
            if (not market_insights.get('comparable_properties')) and (current_data.get('attom', {}) or {}).get('comparables'):
                market_insights['comparable_properties'] = current_data['attom']['comparables']
        except Exception:
            pass
        # If still no comps, attach simple comps derived from MultiSource results (as best-effort)
        try:
            if not market_insights.get('comparable_properties'):
                ms = (current_data.get('multi_source') or {})
                srcs = (ms.get('sources') or {})
                comps = []
                for key in ['zillow','redfin','streeteasy']:
                    s = srcs.get(key) or {}
                    if not s:
                        continue
                    comp = {
                        'address': s.get('address') or s.get('listing_url') or key,
                        'bedrooms': s.get('bedrooms'),
                        'bathrooms': s.get('bathrooms'),
                        'square_feet': s.get('square_feet'),
                        'last_sale_price': s.get('price'),
                        'listing_url': s.get('listing_url'),
                        'source': key
                    }
                    if any(v is not None for v in comp.values()):
                        comps.append(comp)
                if comps:
                    market_insights['comparable_properties'] = comps
        except Exception:
            pass
        current_data['market_insights'] = market_insights

        # Compute data sources used for UI badge
        try:
            sources = {
                'attom_property': bool(attom_bundle.get('property')),
                'attom_details': bool(attom_bundle.get('details')),
                'attom_avm': bool(attom_bundle.get('avm')),
                'attom_area': bool(attom_bundle.get('area_stats')),
                'parcel': bool(attom_bundle.get('parcel')),
                # Best-effort flags for fallbacks
                'fallback': False,
                'tavily': False,
                'scraping': bool((current_data.get('multi_source') or {}).get('sources_count')),
            }
            # Detect fallback by reasoning text
            pe = market_insights.get('price_estimate', {}) or {}
            reasoning = str(pe.get('reasoning', '')).lower()
            if 'square footage only' in reasoning or 'external data sources unavailable' in reasoning:
                sources['fallback'] = True

            # Heuristic: if confidence is low and no ATTOM components, consider fallback
            if (not any([sources['attom_property'], sources['attom_details'], sources['attom_avm'], sources['attom_area']])) and (str(pe.get('confidence', '')).lower() == 'low'):
                sources['fallback'] = True

            current_data['data_sources'] = sources
        except Exception:
            pass
        
        # Update property with market insights
        db.table('properties').update({
            'extracted_data': current_data,
            'status': 'enrichment_complete'
        }).eq('id', property_id).execute()
        
        print(f"Property enrichment complete for {property_id}")
        
        return {
            'status': 'success',
            'property_id': property_id,
            'market_insights': market_insights
        }
        
    except Exception as e:
        print(f"Error enriching property {property_id}: {str(e)}")
        
        # Update property status to failed
        try:
            db = get_admin_db()
            current_data = db.table('properties').select('extracted_data').eq('id', property_id).execute().data[0].get('extracted_data', {})
            current_data['enrichment_error'] = str(e)
            db.table('properties').update({
                'status': 'failed',
                'extracted_data': current_data
            }).eq('id', property_id).execute()
        except Exception as update_error:
            print(f"Failed to update error status: {update_error}")
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery.task(name='generate_listing_copy', bind=True, max_retries=3)
def generate_listing_copy_task(self, property_id: str):
    """
    Asynchronous task to generate listing copy
    
    Uses AI Agent #3 (Listing Copywriter) to:
    1. Fetch property data and market insights
    2. Run AI copywriting agent
    3. Generate MLS-ready listing description
    4. Create social media variants
    5. Update property with listing copy
    6. Update status to 'complete'
    
    Args:
        property_id: UUID of the property
    """
    try:
        print(f"Generating listing copy for {property_id}")
        
        # Get database client
        db = get_admin_db()
        
        # Fetch property
        result = db.table('properties').select('*').eq('id', property_id).execute()
        
        if not result.data:
            raise ValueError(f"Property {property_id} not found")
        
        property_record = result.data[0]
        
        # Get extracted data (from Agent #1 and #2)
        extracted_data = property_record.get('extracted_data', {})
        market_insights = extracted_data.get('market_insights', {})
        
        # Initialize Listing Copywriter (Agent #3)
        from app.agents.listing_copywriter import ListingCopywriter
        writer = ListingCopywriter()
        
        # Generate listing copy
        print(f"Generating listing copy with AI Agent #3...")
        listing_copy = writer.generate_listing(
            property_data=extracted_data,
            market_insights=market_insights,
            tone="professional",  # Can be customized based on property type
            target_audience="home_buyers"
        )
        
        print(f"Listing generated: {listing_copy.get('headline', '')}")
        
        # Generate social media variants
        social_variants = writer.generate_social_variants(listing_copy)
        
        # Store listing copy in database
        db.table('properties').update({
            'generated_listing_text': listing_copy.get('description', ''),
            'status': 'complete'
        }).eq('id', property_id).execute()
        
        # Also store full listing data in extracted_data for frontend access
        current_data = property_record.get('extracted_data', {})
        current_data['listing_copy'] = listing_copy
        current_data['social_variants'] = social_variants
        
        db.table('properties').update({
            'extracted_data': current_data
        }).eq('id', property_id).execute()
        
        print(f"Listing copy generation complete for {property_id}")
        
        return {
            'status': 'success',
            'property_id': property_id,
            'listing_copy': listing_copy
        }
        
    except Exception as e:
        print(f"Error generating listing copy for {property_id}: {str(e)}")
        
        # Update property status to failed
        try:
            db = get_admin_db()
            current_data = db.table('properties').select('extracted_data').eq('id', property_id).execute().data[0].get('extracted_data', {})
            current_data['listing_error'] = str(e)
            db.table('properties').update({
                'status': 'failed',
                'extracted_data': current_data
            }).eq('id', property_id).execute()
        except Exception as update_error:
            print(f"Failed to update error status: {update_error}")
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery.task(name='process_property_workflow')
def process_property_workflow(property_id: str):
    """
    Chain all property processing tasks in sequence
    
    Complete 3-Agent Workflow:
    1. Floor plan analysis (Agent #1: Floor Plan Analyst)
       - Extracts rooms, dimensions, features, sq ft
       - Status: processing → parsing_complete
    
    2. Market insights enrichment (Agent #2: Market Insights Analyst)
       - CoreLogic API for comps and AVM
       - Price estimation and investment analysis
       - Status: parsing_complete → enrichment_complete
    
    3. Listing copy generation (Agent #3: Listing Copywriter)
       - MLS-ready description
       - Social media variants
       - Status: enrichment_complete → complete
    
    Args:
        property_id: UUID of the property
    
    Returns:
        AsyncResult: Celery chain result
    """
    from celery import chain
    
    # Create complete 3-agent task chain
    # Use .si() (immutable signature) to prevent passing previous task results
    workflow = chain(
        process_floor_plan_task.si(property_id),
        enrich_property_data_task.si(property_id),
        generate_listing_copy_task.si(property_id)
    )
    
    return workflow.apply_async()
