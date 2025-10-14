"""
Property Routes
Handles property creation, floor plan upload, and property management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.utils.supabase_client import get_db, get_admin_db, upload_floor_plan, FLOOR_PLAN_BUCKET
import os
import uuid
from datetime import datetime

properties_bp = Blueprint('properties', __name__)

# Allowed file extensions for floor plans
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file_size(file_data):
    """Validate file size is within limits"""
    return len(file_data) <= MAX_FILE_SIZE


@properties_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_floor_plan_endpoint():
    """
    Upload a floor plan image and create a property record
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Form Data:
        file: Floor plan image (PNG, JPG, PDF, max 10MB)
        address: Property address (optional, can be added later)
    
    Returns:
        {
            "property": {
                "id": "uuid",
                "floor_plan_url": "https://...",
                "address": "123 Main St",
                "status": "uploaded",
                "created_at": "2025-10-04T..."
            }
        }
    """
    try:
        # Get current user
        user_id = get_jwt_identity()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'message': 'Please upload a floor plan image'
            }), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a file to upload'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'message': f'Allowed file types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Read file data
        file_data = file.read()
        
        # Validate file size
        if not validate_file_size(file_data):
            return jsonify({
                'error': 'File too large',
                'message': f'Maximum file size is {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{user_id}/{uuid.uuid4()}.{file_ext}"
        
        # Upload to Supabase Storage
        try:
            # Get storage client
            admin_db = get_admin_db()
            storage = admin_db.storage
            
            # Upload file
            storage.from_(FLOOR_PLAN_BUCKET).upload(
                unique_filename,
                file_data,
                file_options={
                    "content-type": file.content_type or f"image/{file_ext}"
                }
            )
            
            # Generate signed URL (valid for 1 year)
            # Note: Using signed URL because bucket is private
            floor_plan_url = storage.from_(FLOOR_PLAN_BUCKET).create_signed_url(
                unique_filename,
                expires_in=31536000  # 1 year in seconds
            )['signedURL']
            
        except Exception as e:
            return jsonify({
                'error': 'Upload failed',
                'message': f'Failed to upload file to storage: {str(e)}'
            }), 500
        
        # Get required address from form data
        address = request.form.get('address', '').strip()
        
        # Validate address is provided
        if not address:
            return jsonify({
                'error': 'Validation error',
                'message': 'Address is required for property analysis'
            }), 400
        
        # Create property record in database
        property_data = {
            'agent_id': user_id,
            'input_type': 'upload',
            'image_url': floor_plan_url,
            'image_storage_path': unique_filename,
            'status': 'processing',  # Status: processing -> parsing_complete -> enrichment_complete -> complete
            'extracted_data': {'address': address}  # Store address from form
        }
        
        db = get_admin_db()
        result = db.table('properties').insert(property_data).execute()
        
        if not result.data:
            return jsonify({
                'error': 'Database error',
                'message': 'Failed to create property record'
            }), 500
        
        property_record = result.data[0]
        
        # Trigger complete 3-agent workflow
        from app.tasks.property_tasks import process_property_workflow
        task = process_property_workflow.delay(property_record['id'])
        
        return jsonify({
            'property': {
                'id': property_record['id'],
                'floor_plan_url': property_record['image_url'],
                'address': property_record.get('extracted_data', {}).get('address'),
                'status': property_record['status'],
                'created_at': property_record['created_at']
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Upload failed',
            'message': str(e)
        }), 500


@properties_bp.route('/search', methods=['POST'])
@jwt_required()
def search_property():
    """
    Create a property record with address only (no floor plan yet)
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Request Body:
        {
            "address": "123 Main St, San Francisco, CA 94102"
        }
    
    Returns:
        {
            "property": {
                "id": "uuid",
                "address": "123 Main St, San Francisco, CA 94102",
                "status": "address_only",
                "created_at": "2025-10-04T..."
            }
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate address
        address = data.get('address', '').strip()
        
        if not address:
            return jsonify({
                'error': 'Missing address',
                'message': 'Please provide a property address'
            }), 400
        
        # Basic address validation (at least 5 characters)
        if len(address) < 5:
            return jsonify({
                'error': 'Invalid address',
                'message': 'Please provide a complete address'
            }), 400
        
        # TODO: Normalize address with Google Maps Geocoding API
        # For now, just use the provided address
        
        # Create property record
        property_data = {
            'agent_id': user_id,
            'input_type': 'search',
            'status': 'processing',
            'extracted_data': {'address': address}
        }
        
        db = get_admin_db()
        result = db.table('properties').insert(property_data).execute()
        
        if not result.data:
            return jsonify({
                'error': 'Database error',
                'message': 'Failed to create property record'
            }), 500
        
        property_record = result.data[0]
        
        return jsonify({
            'property': {
                'id': property_record['id'],
                'address': property_record.get('extracted_data', {}).get('address'),
                'status': property_record['status'],
                'created_at': property_record['created_at']
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to create property',
            'message': str(e)
        }), 500


@properties_bp.route('/', methods=['GET'])
@jwt_required()
def list_properties():
    """
    Get all properties for the authenticated user
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Query Parameters:
        status: Filter by status (optional)
        limit: Number of results (default 50)
        offset: Pagination offset (default 0)
    
    Returns:
        {
            "properties": [
                {
                    "id": "uuid",
                    "address": "123 Main St",
                    "status": "complete",
                    "created_at": "2025-10-04T..."
                }
            ],
            "total": 10
        }
    """
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        db = get_db()
        query = db.table('properties').select('*').eq('agent_id', user_id)
        
        # Filter by status if provided
        if status:
            query = query.eq('status', status)
        
        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        
        result = query.execute()
        
        # Generate public URLs for all properties (fast, no API calls)
        # Note: Changed from signed URLs to public URLs for 95% performance improvement
        # Floor plans are already public via shareable reports, so no additional security risk
        admin_db = get_admin_db()
        storage = admin_db.storage
        for prop in result.data:
            if prop.get('image_storage_path'):
                try:
                    public_url = storage.from_(FLOOR_PLAN_BUCKET).get_public_url(
                        prop['image_storage_path']
                    )
                    prop['image_url'] = public_url
                except Exception as e:
                    print(f"Failed to generate public URL for {prop['id']}: {e}")
        
        return jsonify({
            'properties': result.data,
            'total': len(result.data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch properties',
            'message': str(e)
        }), 500


@properties_bp.route('/<property_id>', methods=['GET'])
@jwt_required()
def get_property(property_id):
    """
    Get a specific property by ID
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Returns:
        {
            "property": {
                "id": "uuid",
                "address": "123 Main St",
                "floor_plan_url": "https://...",
                "status": "complete",
                "floor_plan_data": {...},
                "created_at": "2025-10-04T..."
            }
        }
    """
    try:
        user_id = get_jwt_identity()
        
        # Fetch property
        db = get_db()
        result = db.table('properties').select('*').eq('id', property_id).eq('agent_id', user_id).execute()
        
        if not result.data:
            return jsonify({
                'error': 'Property not found',
                'message': 'Property does not exist or you do not have access'
            }), 404
        
        property_record = result.data[0]
        
        # Generate public URL for image if it exists (fast, no API call)
        if property_record.get('image_storage_path'):
            try:
                admin_db = get_admin_db()
                storage = admin_db.storage
                public_url = storage.from_(FLOOR_PLAN_BUCKET).get_public_url(
                    property_record['image_storage_path']
                )
                property_record['image_url'] = public_url
            except Exception as e:
                print(f"Failed to generate public URL: {e}")
                # Keep existing URL if generation fails
        
        return jsonify({
            'property': property_record
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch property',
            'message': str(e)
        }), 500


@properties_bp.route('/<property_id>', methods=['PUT'])
@jwt_required()
def update_property(property_id):
    """
    Update property listing copy (allows agents to edit AI-generated text)
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Body:
        {
            "listing_copy": {
                "headline": "Updated headline",
                "description": "Updated description",
                "highlights": ["feature1", "feature2"],
                ...
            }
        }
    
    Returns:
        {
            "message": "Property updated successfully",
            "property": {...}
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'listing_copy' not in data:
            return jsonify({
                'error': 'Missing listing_copy',
                'message': 'Request body must include listing_copy object'
            }), 400
        
        # Validate listing_copy structure
        listing_copy = data['listing_copy']
        required_fields = ['headline', 'description']
        missing_fields = [field for field in required_fields if field not in listing_copy]
        
        if missing_fields:
            return jsonify({
                'error': 'Invalid listing_copy',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Update property
        admin_db = get_admin_db()
        result = admin_db.table('properties').update({
            'listing_copy': listing_copy,
            'updated_at': 'now()'
        }).eq('id', property_id).eq('agent_id', user_id).execute()
        
        if not result.data:
            return jsonify({
                'error': 'Property not found',
                'message': 'Property does not exist or you do not have access'
            }), 404
        
        return jsonify({
            'message': 'Property updated successfully',
            'property': result.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to update property',
            'message': str(e)
        }), 500


@properties_bp.route('/<property_id>', methods=['DELETE'])
@jwt_required()
def delete_property(property_id):
    """
    Delete a property and its associated floor plan
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Returns:
        {
            "message": "Property deleted successfully"
        }
    """
    try:
        user_id = get_jwt_identity()
        
        # Fetch property to get floor plan path
        db = get_db()
        result = db.table('properties').select('*').eq('id', property_id).eq('agent_id', user_id).execute()
        
        if not result.data:
            return jsonify({
                'error': 'Property not found',
                'message': 'Property does not exist or you do not have access'
            }), 404
        
        property_record = result.data[0]
        
        # Delete floor plan from storage if exists
        if property_record.get('image_storage_path'):
            try:
                admin_db = get_admin_db()
                storage = admin_db.storage
                storage.from_(FLOOR_PLAN_BUCKET).remove([property_record['image_storage_path']])
            except Exception as e:
                # Log error but continue with deletion
                print(f"Failed to delete floor plan from storage: {e}")
        
        # Delete property record
        admin_db = get_admin_db()
        admin_db.table('properties').delete().eq('id', property_id).eq('agent_id', user_id).execute()
        
        return jsonify({
            'message': 'Property deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to delete property',
            'message': str(e)
        }), 500


@properties_bp.route('/<property_id>/analytics', methods=['GET'])
@jwt_required()
def get_property_analytics(property_id):
    """
    Get analytics data for a property (view count, timestamps, user agents)
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Returns:
        {
            "view_count": 10,
            "unique_viewers": 5,
            "views": [
                {
                    "viewed_at": "2025-01-01T10:00:00Z",
                    "user_agent": "Mozilla/5.0...",
                    "ip_address": "192.168.1.1"
                }
            ]
        }
    """
    try:
        user_id = get_jwt_identity()
        
        # Verify property ownership
        db = get_db()
        result = db.table('properties').select('id').eq('id', property_id).eq('agent_id', user_id).execute()
        
        if not result.data:
            return jsonify({
                'error': 'Property not found',
                'message': 'Property does not exist or you do not have access'
            }), 404
        
        # Fetch analytics from property_views table
        views_result = db.table('property_views').select('*').eq('property_id', property_id).order('viewed_at', desc=True).execute()
        
        views = views_result.data if views_result.data else []
        
        # Calculate unique viewers (by IP address)
        unique_ips = set(view.get('ip_address') for view in views if view.get('ip_address'))
        
        return jsonify({
            'view_count': len(views),
            'unique_viewers': len(unique_ips),
            'views': views
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch analytics',
            'message': str(e)
        }), 500


@properties_bp.route('/<property_id>/generate-link', methods=['POST'])
@jwt_required()
def generate_shareable_link(property_id):
    """
    Generate a unique shareable link for a property
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Request Body (optional):
        {
            "expiration_days": 30  // Default: 30 days
        }
    
    Returns:
        {
            "token": "abc123...",
            "shareable_url": "http://localhost:5173/report/abc123...",
            "expires_at": "2025-02-01T00:00:00Z"
        }
    """
    try:
        user_id = get_jwt_identity()
        
        # Verify property ownership
        db = get_db()
        result = db.table('properties').select('id').eq('id', property_id).eq('agent_id', user_id).execute()
        
        if not result.data:
            return jsonify({
                'error': 'Property not found',
                'message': 'Property does not exist or you do not have access'
            }), 404
        
        # Get expiration days from request or use default
        data = request.get_json() or {}
        expiration_days = data.get('expiration_days', 30)
        
        # Generate unique token
        token = str(uuid.uuid4())
        
        # Calculate expiration date
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(days=expiration_days)
        
        # Store token in database
        admin_db = get_admin_db()
        admin_db.table('shareable_links').insert({
            'property_id': property_id,
            'token': token,
            'expires_at': expires_at.isoformat(),
            'created_by': user_id,
            'is_active': True
        }).execute()
        
        # Build shareable URL (use environment variable or default)
        base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        shareable_url = f"{base_url}/report/{token}"
        
        return jsonify({
            'token': token,
            'shareable_url': shareable_url,
            'expires_at': expires_at.isoformat()
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate shareable link',
            'message': str(e)
        }), 500


@properties_bp.route('/<property_id>/shareable-link', methods=['GET'])
@jwt_required()
def get_shareable_link(property_id):
    """
    Get the active shareable link for a property
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Returns:
        {
            "token": "abc123...",
            "shareable_url": "http://localhost:5173/report/abc123...",
            "expires_at": "2025-02-01T00:00:00Z",
            "created_at": "2025-01-01T00:00:00Z"
        }
        
        Or 404 if no active link exists
    """
    try:
        user_id = get_jwt_identity()
        
        # Verify property ownership
        db = get_db()
        result = db.table('properties').select('id').eq('id', property_id).eq('agent_id', user_id).execute()
        
        if not result.data:
            return jsonify({
                'error': 'Property not found',
                'message': 'Property does not exist or you do not have access'
            }), 404
        
        # Fetch active shareable link
        link_result = db.table('shareable_links').select('*').eq('property_id', property_id).eq('is_active', True).order('created_at', desc=True).limit(1).execute()
        
        if not link_result.data:
            return jsonify({
                'error': 'No shareable link found',
                'message': 'No active shareable link exists for this property'
            }), 404
        
        link = link_result.data[0]
        
        # Build shareable URL
        base_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        shareable_url = f"{base_url}/report/{link['token']}"
        
        return jsonify({
            'token': link['token'],
            'shareable_url': shareable_url,
            'expires_at': link['expires_at'],
            'created_at': link.get('created_at', link['expires_at'])
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch shareable link',
            'message': str(e)
        }), 500


# ================================
# PHASE 2: ENHANCED FLOOR PLAN ANALYSIS
# ================================

@properties_bp.route('/<property_id>/analyze-enhanced', methods=['POST'])
@jwt_required()
def analyze_floor_plan_enhanced(property_id):
    """
    Enhanced floor plan analysis with detailed measurements (Phase 2)
    
    Combines:
    - Basic property data extraction (Agent #1)
    - Room-by-room measurement estimation (AI service)
    - Cross-validation and confidence scoring
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Query Parameters:
        detailed: Include detailed measurements (default: true)
        store: Store results in database (default: true)
    
    Returns:
        {
            "property_id": "uuid",
            "basic_analysis": {
                "bedrooms": 2,
                "bathrooms": 1.0,
                "square_footage": 934,
                "rooms": [...],
                "features": [...]
            },
            "detailed_measurements": {
                "total_square_feet": 934,
                "total_square_feet_confidence": 0.85,
                "quality_score": 83,
                "rooms": [
                    {
                        "type": "bedroom",
                        "name": "Master Bedroom",
                        "length_ft": 12.0,
                        "width_ft": 14.0,
                        "sqft": 168,
                        "features": ["closet", "window"],
                        "confidence": 0.90
                    }
                ]
            },
            "validation": {
                "confidence": "High",
                "confidence_score": 0.95,
                "agreement": "Good"
            }
        }
    """
    try:
        from app.agents.floor_plan_analyst_enhanced import EnhancedFloorPlanAnalyst
        import tempfile
        
        user_id = get_jwt_identity()
        
        # Get query parameters
        include_detailed = request.args.get('detailed', 'true').lower() == 'true'
        include_features = request.args.get('features', 'true').lower() == 'true'
        store_results = request.args.get('store', 'true').lower() == 'true'
        
        # Verify property ownership and get floor plan
        db = get_db()
        result = db.table('properties').select('*').eq('id', property_id).eq('agent_id', user_id).execute()
        
        if not result.data:
            return jsonify({
                'error': 'Property not found',
                'message': 'Property does not exist or you do not have access'
            }), 404
        
        property_data = result.data[0]
        floor_plan_url = property_data.get('image_url')
        
        if not floor_plan_url:
            return jsonify({
                'error': 'No floor plan',
                'message': 'This property does not have a floor plan image'
            }), 400
        
        # Download floor plan to temporary file
        import requests
        response = requests.get(floor_plan_url)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        
        try:
            # Run enhanced analysis
            analyst = EnhancedFloorPlanAnalyst()
            
            if include_detailed:
                analysis_result = analyst.analyze_with_validation(image_path=tmp_path)
            else:
                analysis_result = analyst.analyze_floor_plan(
                    image_path=tmp_path,
                    include_measurements=include_detailed,
                    include_features=include_features
                )
            
            # Store results in database if requested
            if store_results:
                admin_db = get_admin_db()
                
                # Update properties.extracted_data
                admin_db.table('properties').update({
                    'extracted_data': analysis_result['basic_analysis'],
                    'status': 'parsing_complete'
                }).eq('id', property_id).execute()
                
                # Store detailed measurements if available
                if analysis_result.get('detailed_measurements'):
                    measurements_data = analysis_result['detailed_measurements'].copy()
                    measurements_data['property_id'] = property_id
                    
                    # Merge feature detection data if available
                    if analysis_result.get('feature_detection'):
                        # The feature detection goes into detected_features field
                        measurements_data['detected_features'] = analysis_result['feature_detection']
                    
                    # Upsert (insert or update)
                    admin_db.table('floor_plan_measurements').upsert(
                        measurements_data,
                        on_conflict='property_id'
                    ).execute()
            
            # Return results
            return jsonify({
                'property_id': property_id,
                'basic_analysis': analysis_result['basic_analysis'],
                'detailed_measurements': analysis_result.get('detailed_measurements'),
                'feature_detection': analysis_result.get('feature_detection'),
                'validation': analysis_result.get('validation'),
                'stages_completed': analysis_result.get('stages_completed', 1),
                'stored_in_database': store_results
            }), 200
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        import traceback
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e),
            'traceback': traceback.format_exc() if os.getenv('DEBUG') else None
        }), 500


@properties_bp.route('/<property_id>/measurements', methods=['GET'])
@jwt_required()
def get_floor_plan_measurements(property_id):
    """
    Get stored floor plan measurements for a property
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Returns:
        {
            "property_id": "uuid",
            "total_square_feet": 934,
            "confidence": 0.85,
            "quality_score": 83,
            "rooms": [...],
            "detected_features": [...],
            "measurement_method": "hybrid",
            "created_at": "2025-10-13T..."
        }
    """
    try:
        user_id = get_jwt_identity()
        
        # Verify property ownership
        db = get_db()
        property_result = db.table('properties').select('id').eq('id', property_id).eq('agent_id', user_id).execute()
        
        if not property_result.data:
            return jsonify({
                'error': 'Property not found',
                'message': 'Property does not exist or you do not have access'
            }), 404
        
        # Get measurements
        measurements_result = db.table('floor_plan_measurements').select('*').eq('property_id', property_id).execute()
        
        if not measurements_result.data:
            return jsonify({
                'error': 'No measurements found',
                'message': 'No measurements have been generated for this property yet. Run enhanced analysis first.'
            }), 404
        
        measurements = measurements_result.data[0]
        
        return jsonify(measurements), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch measurements',
            'message': str(e)
        }), 500


@properties_bp.route('/<property_id>/enrich', methods=['POST'])
@jwt_required()
def retrigger_enrichment(property_id):
    """
    Re-trigger enrichment (ATTOM fetch + market insights) for an existing property.
    Does not re-run floor plan analysis.

    Returns 202 when the Celery task has been queued.
    """
    try:
        user_id = get_jwt_identity()

        # Verify property ownership
        db = get_db()
        result = db.table('properties').select('id').eq('id', property_id).eq('agent_id', user_id).execute()

        if not result.data:
            return jsonify({
                'error': 'Property not found',
                'message': 'Property does not exist or you do not have access'
            }), 404

        # Queue enrichment task
        from app.tasks.property_tasks import enrich_property_data_task
        enrich_property_data_task.delay(property_id)

        return jsonify({
            'message': 'Enrichment started',
            'property_id': property_id
        }), 202

    except Exception as e:
        return jsonify({
            'error': 'Failed to start enrichment',
            'message': str(e)
        }), 500
