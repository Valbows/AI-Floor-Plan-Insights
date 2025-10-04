"""
Unit tests for authentication endpoints
"""

import pytest
from app import create_app
from unittest.mock import Mock, patch


@pytest.fixture
def client():
    """Create test client"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    with patch('app.routes.auth.get_supabase_client') as mock:
        yield mock.return_value


class TestRegistration:
    """Test user registration endpoint"""
    
    def test_register_success(self, client, mock_supabase):
        """Test successful user registration"""
        # Mock Supabase responses
        mock_user = Mock()
        mock_user.id = 'test-user-id-123'
        mock_user.email = 'test@example.com'
        
        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        
        mock_supabase.auth.sign_up.return_value = mock_auth_response
        mock_supabase.table.return_value.insert.return_value.execute.return_value = None
        
        # Make request
        response = client.post('/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test1234',
            'full_name': 'Test User'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'token' in data
        assert data['user']['email'] == 'test@example.com'
        assert data['user']['full_name'] == 'Test User'
    
    def test_register_missing_email(self, client):
        """Test registration with missing email"""
        response = client.post('/auth/register', json={
            'password': 'Test1234'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'required' in data['message'].lower()
    
    def test_register_missing_password(self, client):
        """Test registration with missing password"""
        response = client.post('/auth/register', json={
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post('/auth/register', json={
            'email': 'invalid-email',
            'password': 'Test1234'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'email' in data['error'].lower()
    
    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        response = client.post('/auth/register', json={
            'email': 'test@example.com',
            'password': 'weak'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'password' in data['error'].lower()
    
    def test_register_password_no_numbers(self, client):
        """Test registration with password without numbers"""
        response = client.post('/auth/register', json={
            'email': 'test@example.com',
            'password': 'NoNumbers'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'number' in data['message'].lower()


class TestLogin:
    """Test user login endpoint"""
    
    def test_login_success(self, client, mock_supabase):
        """Test successful login"""
        # Mock Supabase responses
        mock_user = Mock()
        mock_user.id = 'test-user-id-123'
        
        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        
        mock_user_data = Mock()
        mock_user_data.data = [{
            'id': 'test-user-id-123',
            'email': 'test@example.com',
            'full_name': 'Test User'
        }]
        
        mock_supabase.auth.sign_in_with_password.return_value = mock_auth_response
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_user_data
        
        # Make request
        response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'Test1234'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post('/auth/login', json={
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['message'].lower()
    
    def test_login_invalid_credentials(self, client, mock_supabase):
        """Test login with invalid credentials"""
        mock_supabase.auth.sign_in_with_password.side_effect = Exception('Invalid credentials')
        
        response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword1'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'failed' in data['error'].lower()


class TestTokenVerification:
    """Test JWT token verification"""
    
    def test_verify_valid_token(self, client, mock_supabase):
        """Test verification with valid token"""
        # First register/login to get a token
        mock_user = Mock()
        mock_user.id = 'test-user-id-123'
        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        
        mock_user_data = Mock()
        mock_user_data.data = [{
            'id': 'test-user-id-123',
            'email': 'test@example.com',
            'full_name': 'Test User'
        }]
        
        mock_supabase.auth.sign_in_with_password.return_value = mock_auth_response
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_user_data
        
        # Login to get token
        login_response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'Test1234'
        })
        
        token = login_response.get_json()['token']
        
        # Verify token
        response = client.get('/auth/verify', headers={
            'Authorization': f'Bearer {token}'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
    
    def test_verify_missing_token(self, client):
        """Test verification without token"""
        response = client.get('/auth/verify')
        
        assert response.status_code == 401
    
    def test_verify_invalid_token(self, client):
        """Test verification with invalid token"""
        response = client.get('/auth/verify', headers={
            'Authorization': 'Bearer invalid-token'
        })
        
        assert response.status_code == 422  # Unprocessable entity


class TestPasswordValidation:
    """Test password validation logic"""
    
    def test_password_too_short(self, client):
        """Test password shorter than 8 characters"""
        response = client.post('/auth/register', json={
            'email': 'test@example.com',
            'password': 'Test1'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert '8 characters' in data['message']
    
    def test_password_no_letter(self, client):
        """Test password without letters"""
        response = client.post('/auth/register', json={
            'email': 'test@example.com',
            'password': '12345678'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'letter' in data['message'].lower()
