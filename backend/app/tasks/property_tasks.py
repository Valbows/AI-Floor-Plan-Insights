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
        
        # Download floor plan image
        image_url = property_record['image_url']
        print(f"Downloading floor plan from: {image_url}")
        
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        image_bytes = response.content
        
        # Initialize Floor Plan Analyst
        analyst = FloorPlanAnalyst()
        
        # Analyze floor plan
        print(f"Analyzing floor plan with AI Agent #1...")
        extracted_data = analyst.analyze_floor_plan(image_bytes=image_bytes)
        
        print(f"Extracted data: {extracted_data}")
        
        # Merge with existing extracted_data
        current_data = property_record.get('extracted_data', {})
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
    
    This will be implemented in Phase 2 with AI Agent #2 (Market Insights Analyst)
    
    Steps:
    1. Fetch property data
    2. Query CoreLogic API for property details
    3. Run AI Agent #2 for market analysis
    4. Find comparable properties
    5. Generate price suggestion
    6. Update property status to 'enrichment_complete'
    
    Args:
        property_id: UUID of the property to enrich
    """
    try:
        print(f"Enriching property data for {property_id}")
        
        # Placeholder for Phase 2
        db = get_admin_db()
        
        db.table('properties').update({
            'status': 'enrichment_complete'
        }).eq('id', property_id).execute()
        
        return {
            'status': 'success',
            'property_id': property_id,
            'message': 'Phase 2 - Not yet implemented'
        }
        
    except Exception as e:
        print(f"Error enriching property {property_id}: {str(e)}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery.task(name='generate_listing_copy', bind=True, max_retries=3)
def generate_listing_copy_task(self, property_id: str):
    """
    Asynchronous task to generate listing copy
    
    This will be implemented in Phase 2 with AI Agent #3 (Listing Copywriter)
    
    Steps:
    1. Fetch property data and market insights
    2. Run AI Agent #3 for copywriting
    3. Generate MLS-ready description
    4. Update property status to 'complete'
    
    Args:
        property_id: UUID of the property
    """
    try:
        print(f"Generating listing copy for {property_id}")
        
        # Placeholder for Phase 2
        db = get_admin_db()
        
        db.table('properties').update({
            'status': 'complete'
        }).eq('id', property_id).execute()
        
        return {
            'status': 'success',
            'property_id': property_id,
            'message': 'Phase 2 - Not yet implemented'
        }
        
    except Exception as e:
        print(f"Error generating listing copy for {property_id}: {str(e)}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@celery.task(name='process_property_workflow')
def process_property_workflow(property_id: str):
    """
    Chain all property processing tasks in sequence
    
    Workflow:
    1. Floor plan analysis (Agent #1)
    2. Market insights enrichment (Agent #2) - Phase 2
    3. Listing copy generation (Agent #3) - Phase 2
    
    Args:
        property_id: UUID of the property
    """
    from celery import chain
    
    # Create task chain
    workflow = chain(
        process_floor_plan_task.s(property_id),
        # enrich_property_data_task.s(property_id),  # Phase 2
        # generate_listing_copy_task.s(property_id)  # Phase 2
    )
    
    return workflow.apply_async()
