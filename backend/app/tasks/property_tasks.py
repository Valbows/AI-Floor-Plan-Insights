"""
Celery Tasks for Property Processing
Handles asynchronous floor plan analysis and enrichment
"""

from app import celery
from app.utils.supabase_client import get_admin_db
from app.agents.floor_plan_analyst import FloorPlanAnalyst
import requests


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
        db.table('properties').update({
            'status': 'processing'
        }).eq('id', property_id).execute()
        
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
        
        # Update status to indicate enrichment has started
        db.table('properties').update({
            'status': 'enrichment_complete'  # Will change to enrichment_in_progress in future
        }).eq('id', property_id).execute()
        
        # Initialize Market Insights Analyst (Agent #2)
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
        current_data['market_insights'] = market_insights
        
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
                'status': 'enrichment_failed',
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
                'status': 'listing_failed',
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
