"""
Authentication Routes
Handles user registration, login, logout, and token verification
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app.utils.supabase_client import get_supabase_client
from datetime import timedelta
import re

auth_bp = Blueprint('auth', __name__)


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength
    Requirements: min 8 chars, at least one letter and one number
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, ""


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new agent user
    
    Request Body:
        {
            "email": "agent@example.com",
            "password": "secure_password",
            "full_name": "Jane Smith"
        }
    
    Returns:
        {
            "token": "jwt_access_token",
            "user": {
                "id": "uuid",
                "email": "agent@example.com",
                "full_name": "Jane Smith"
            }
        }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name', '')
        
        if not email or not password:
            return jsonify({
                'error': 'Missing required fields',
                'message': 'Email and password are required'
            }), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({
                'error': 'Invalid email',
                'message': 'Please provide a valid email address'
            }), 400
        
        # Validate password strength
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({
                'error': 'Weak password',
                'message': error_msg
            }), 400
        
        # Register user with Supabase Auth
        supabase = get_supabase_client()
        
        auth_response = supabase.auth.sign_up({
            'email': email,
            'password': password,
            'options': {
                'data': {
                    'full_name': full_name
                }
            }
        })
        
        if not auth_response.user:
            return jsonify({
                'error': 'Registration failed',
                'message': 'Could not create user account'
            }), 500
        
        user_id = auth_response.user.id
        
        # Insert extended user data into public.users table
        user_data = {
            'id': user_id,
            'email': email,
            'full_name': full_name
        }
        
        supabase.table('users').insert(user_data).execute()
        
        # Create JWT access token
        access_token = create_access_token(
            identity=user_id,
            additional_claims={'email': email}
        )
        
        return jsonify({
            'token': access_token,
            'user': {
                'id': user_id,
                'email': email,
                'full_name': full_name
            }
        }), 201
        
    except Exception as e:
        # Check for duplicate email
        if 'already registered' in str(e).lower() or 'duplicate' in str(e).lower():
            return jsonify({
                'error': 'Email already exists',
                'message': 'An account with this email already exists'
            }), 409
        
        return jsonify({
            'error': 'Registration failed',
            'message': str(e)
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login an existing user
    
    Request Body:
        {
            "email": "agent@example.com",
            "password": "secure_password"
        }
    
    Returns:
        {
            "token": "jwt_access_token",
            "user": {
                "id": "uuid",
                "email": "agent@example.com",
                "full_name": "Jane Smith"
            }
        }
    """
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'error': 'Missing credentials',
                'message': 'Email and password are required'
            }), 400
        
        # Authenticate with Supabase Auth
        supabase = get_supabase_client()
        
        auth_response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        if not auth_response.user:
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Invalid email or password'
            }), 401
        
        user_id = auth_response.user.id
        
        # Fetch extended user data
        user_response = supabase.table('users').select('*').eq('id', user_id).execute()
        
        user_data = user_response.data[0] if user_response.data else {}
        
        # Create JWT access token
        access_token = create_access_token(
            identity=user_id,
            additional_claims={'email': email}
        )
        
        return jsonify({
            'token': access_token,
            'user': {
                'id': user_id,
                'email': email,
                'full_name': user_data.get('full_name', '')
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Login failed',
            'message': 'Invalid email or password'
        }), 401


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout current user
    Note: With JWT, logout is primarily handled client-side by removing the token
    This endpoint can be used for server-side session cleanup if needed
    
    Returns:
        {"message": "Successfully logged out"}
    """
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        
        # Optional: Add token to blacklist or perform cleanup
        # For now, client-side token removal is sufficient
        
        return jsonify({
            'message': 'Successfully logged out'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Logout failed',
            'message': str(e)
        }), 500


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify():
    """
    Verify JWT token and return current user
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Returns:
        {
            "user": {
                "id": "uuid",
                "email": "agent@example.com",
                "full_name": "Jane Smith"
            }
        }
    """
    try:
        # Get user ID from JWT
        user_id = get_jwt_identity()
        jwt_data = get_jwt()
        email = jwt_data.get('email')
        
        # Fetch user data from database
        supabase = get_supabase_client()
        user_response = supabase.table('users').select('*').eq('id', user_id).execute()
        
        if not user_response.data:
            return jsonify({
                'error': 'User not found',
                'message': 'Invalid token or user does not exist'
            }), 404
        
        user_data = user_response.data[0]
        
        return jsonify({
            'user': {
                'id': user_id,
                'email': user_data.get('email', email),
                'full_name': user_data.get('full_name', '')
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Verification failed',
            'message': str(e)
        }), 401


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user's profile
    Alias for /verify endpoint
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Returns:
        {
            "user": {
                "id": "uuid",
                "email": "agent@example.com",
                "full_name": "Jane Smith",
                "created_at": "2025-10-04T13:00:00Z"
            }
        }
    """
    try:
        user_id = get_jwt_identity()
        
        supabase = get_supabase_client()
        user_response = supabase.table('users').select('*').eq('id', user_id).execute()
        
        if not user_response.data:
            return jsonify({
                'error': 'User not found'
            }), 404
        
        user_data = user_response.data[0]
        
        return jsonify({
            'user': user_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch user',
            'message': str(e)
        }), 500
