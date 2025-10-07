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
        
        # Regenerate signed URLs for all properties
        admin_db = get_admin_db()
        storage = admin_db.storage
        for prop in result.data:
            if prop.get('image_storage_path'):
                try:
                    signed_url = storage.from_(FLOOR_PLAN_BUCKET).create_signed_url(
                        prop['image_storage_path'],
                        expires_in=3600  # 1 hour
                    )['signedURL']
                    prop['image_url'] = signed_url
                except Exception as e:
                    print(f"Failed to generate signed URL for {prop['id']}: {e}")
        
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
        
        # Regenerate signed URL for image if it exists
        if property_record.get('image_storage_path'):
            try:
                admin_db = get_admin_db()
                storage = admin_db.storage
                signed_url = storage.from_(FLOOR_PLAN_BUCKET).create_signed_url(
                    property_record['image_storage_path'],
                    expires_in=3600  # 1 hour for viewing
                )['signedURL']
                property_record['image_url'] = signed_url
            except Exception as e:
                print(f"Failed to generate signed URL: {e}")
                # Keep existing URL if signing fails
        
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
