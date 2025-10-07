"""
Public API Routes - No Authentication Required

These routes are accessible via shareable tokens and don't require JWT authentication.
Used for public property reports shared with potential buyers.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
from app.utils.supabase_client import get_db
import os

public_bp = Blueprint('public', __name__, url_prefix='/api/public')


@public_bp.route('/report/<token>', methods=['GET'])
def get_public_report(token):
    """
    Get public property report by shareable token
    
    No authentication required - public endpoint
    
    Path Parameters:
        token: UUID token from shareable link
    
    Returns:
        {
            "property": {
                "id": "...",
                "address": "...",
                "extracted_data": {...},
                "floor_plan_url": "...",
                "created_at": "..."
            },
            "token_info": {
                "expires_at": "...",
                "is_active": true
            }
        }
    
    Error Responses:
        404: Token not found or expired
        410: Token has been deactivated
    """
    try:
        db = get_db()
        
        # Find the shareable link by token
        link_result = db.table('shareable_links').select('*').eq('token', token).eq('is_active', True).execute()
        
        if not link_result.data or len(link_result.data) == 0:
            return jsonify({
                'error': 'Link not found',
                'message': 'This shareable link does not exist or has been deactivated'
            }), 404
        
        link = link_result.data[0]
        
        # Check if token has expired
        expires_at = datetime.fromisoformat(link['expires_at'].replace('Z', '+00:00'))
        if datetime.utcnow().replace(tzinfo=expires_at.tzinfo) > expires_at:
            return jsonify({
                'error': 'Link expired',
                'message': 'This shareable link has expired'
            }), 410
        
        # Fetch the property data
        property_id = link['property_id']
        property_result = db.table('properties').select('*').eq('id', property_id).execute()
        
        if not property_result.data or len(property_result.data) == 0:
            return jsonify({
                'error': 'Property not found',
                'message': 'The property associated with this link no longer exists'
            }), 404
        
        property_data = property_result.data[0]
        
        # Sanitize property data - remove sensitive agent information
        sanitized_property = {
            'id': property_data['id'],
            'address': property_data.get('address', ''),
            'extracted_data': property_data.get('extracted_data', {}),
            'floor_plan_url': property_data.get('floor_plan_url', ''),
            'status': property_data.get('status', ''),
            'created_at': property_data.get('created_at', '')
        }
        
        # Remove agent-specific data from extracted_data if present
        if 'agent_id' in sanitized_property['extracted_data']:
            del sanitized_property['extracted_data']['agent_id']
        if 'agent_notes' in sanitized_property['extracted_data']:
            del sanitized_property['extracted_data']['agent_notes']
        
        # Return public report data
        return jsonify({
            'property': sanitized_property,
            'token_info': {
                'expires_at': link['expires_at'],
                'is_active': link['is_active']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch property report',
            'message': str(e)
        }), 500


@public_bp.route('/report/<token>/log_view', methods=['POST'])
def log_property_view(token):
    """
    Log a view of the public property report
    
    No authentication required - public endpoint
    
    Path Parameters:
        token: UUID token from shareable link
    
    Request Body (optional):
        {
            "user_agent": "Mozilla/5.0...",
            "referrer": "https://...",
            "viewport_width": 1920,
            "viewport_height": 1080
        }
    
    Returns:
        {
            "success": true,
            "message": "View logged successfully"
        }
    """
    try:
        db = get_db()
        
        # Verify token exists and is active
        link_result = db.table('shareable_links').select('property_id').eq('token', token).eq('is_active', True).execute()
        
        if not link_result.data or len(link_result.data) == 0:
            return jsonify({
                'error': 'Invalid token',
                'message': 'This shareable link is not valid'
            }), 404
        
        property_id = link_result.data[0]['property_id']
        
        # Get request data
        data = request.get_json() or {}
        
        # Capture view metadata
        user_agent = data.get('user_agent') or request.headers.get('User-Agent', 'Unknown')
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        referrer = data.get('referrer') or request.headers.get('Referer', '')
        
        # Log the view in property_views table
        view_data = {
            'property_id': property_id,
            'viewed_at': datetime.utcnow().isoformat(),
            'user_agent': user_agent,
            'ip_address': ip_address,
            'referrer': referrer,
            'viewport_width': data.get('viewport_width'),
            'viewport_height': data.get('viewport_height')
        }
        
        db.table('property_views').insert(view_data).execute()
        
        return jsonify({
            'success': True,
            'message': 'View logged successfully'
        }), 201
        
    except Exception as e:
        # Don't fail the page load if view logging fails
        return jsonify({
            'success': False,
            'message': 'Failed to log view',
            'error': str(e)
        }), 500


@public_bp.route('/report/<token>/validate', methods=['GET'])
def validate_token(token):
    """
    Validate a shareable token without fetching full property data
    
    Useful for quickly checking if a token is valid before loading the page
    
    Path Parameters:
        token: UUID token from shareable link
    
    Returns:
        {
            "valid": true,
            "expires_at": "2025-11-06T00:00:00Z",
            "property_address": "123 Main St..."
        }
    """
    try:
        db = get_db()
        
        # Find the shareable link
        link_result = db.table('shareable_links').select('*').eq('token', token).eq('is_active', True).execute()
        
        if not link_result.data or len(link_result.data) == 0:
            return jsonify({
                'valid': False,
                'message': 'Token not found or inactive'
            }), 200
        
        link = link_result.data[0]
        
        # Check expiration
        expires_at = datetime.fromisoformat(link['expires_at'].replace('Z', '+00:00'))
        is_expired = datetime.utcnow().replace(tzinfo=expires_at.tzinfo) > expires_at
        
        if is_expired:
            return jsonify({
                'valid': False,
                'message': 'Token has expired',
                'expires_at': link['expires_at']
            }), 200
        
        # Get basic property info
        property_result = db.table('properties').select('address, extracted_data').eq('id', link['property_id']).execute()
        
        address = 'Property'
        if property_result.data and len(property_result.data) > 0:
            prop = property_result.data[0]
            address = prop.get('extracted_data', {}).get('address') or prop.get('address', 'Property')
        
        return jsonify({
            'valid': True,
            'expires_at': link['expires_at'],
            'property_address': address
        }), 200
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': 'Validation failed',
            'error': str(e)
        }), 500
