"""
Unit tests for property endpoints
"""

import pytest
import io
from app import create_app
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def client():
    """Create test client"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_token(client):
    """Get authentication token for tests"""
    with patch('app.routes.auth.get_supabase_client') as mock_supabase, \
         patch('app.routes.auth.get_admin_db') as mock_admin:
        
        # Mock successful login
        mock_user = Mock()
        mock_user.id = 'test-user-123'
        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        
        mock_user_data = Mock()
        mock_user_data.data = [{
            'id': 'test-user-123',
            'email': 'test@example.com',
            'full_name': 'Test User'
        }]
        
        mock_supabase.return_value.auth.sign_in_with_password.return_value = mock_auth_response
        mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_user_data
        
        response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'Test1234'
        })
        
        return response.get_json()['token']


class TestFloorPlanUpload:
    """Test floor plan upload endpoint"""
    
    def test_upload_success(self, client, auth_token):
        """Test successful floor plan upload"""
        with patch('app.routes.properties.get_admin_db') as mock_admin:
            # Mock storage upload
            mock_storage = Mock()
            mock_storage.from_.return_value.upload.return_value = None
            mock_storage.from_.return_value.get_public_url.return_value = 'https://storage.url/floor-plan.png'
            
            mock_admin.return_value.storage = mock_storage
            
            # Mock database insert
            mock_db_result = Mock()
            mock_db_result.data = [{
                'id': 'property-123',
                'floor_plan_url': 'https://storage.url/floor-plan.png',
                'address': None,
                'status': 'uploaded',
                'created_at': '2025-10-04T12:00:00Z'
            }]
            
            mock_admin.return_value.table.return_value.insert.return_value.execute.return_value = mock_db_result
            
            # Create test file
            data = {
                'file': (io.BytesIO(b'fake image data'), 'test.png')
            }
            
            response = client.post(
                '/api/properties/upload',
                data=data,
                headers={'Authorization': f'Bearer {auth_token}'},
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 201
            json_data = response.get_json()
            assert 'property' in json_data
            assert json_data['property']['status'] == 'uploaded'
    
    def test_upload_no_file(self, client, auth_token):
        """Test upload without file"""
        response = client.post(
            '/api/properties/upload',
            data={},
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'file' in json_data['error'].lower()
    
    def test_upload_invalid_file_type(self, client, auth_token):
        """Test upload with invalid file type"""
        data = {
            'file': (io.BytesIO(b'fake data'), 'test.txt')
        }
        
        response = client.post(
            '/api/properties/upload',
            data=data,
            headers={'Authorization': f'Bearer {auth_token}'},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'invalid file type' in json_data['error'].lower()
    
    def test_upload_with_address(self, client, auth_token):
        """Test upload with address provided"""
        with patch('app.routes.properties.get_admin_db') as mock_admin:
            mock_storage = Mock()
            mock_storage.from_.return_value.upload.return_value = None
            mock_storage.from_.return_value.get_public_url.return_value = 'https://storage.url/floor-plan.png'
            mock_admin.return_value.storage = mock_storage
            
            mock_db_result = Mock()
            mock_db_result.data = [{
                'id': 'property-123',
                'floor_plan_url': 'https://storage.url/floor-plan.png',
                'address': '123 Main St',
                'status': 'uploaded',
                'created_at': '2025-10-04T12:00:00Z'
            }]
            mock_admin.return_value.table.return_value.insert.return_value.execute.return_value = mock_db_result
            
            data = {
                'file': (io.BytesIO(b'fake image data'), 'test.png'),
                'address': '123 Main St'
            }
            
            response = client.post(
                '/api/properties/upload',
                data=data,
                headers={'Authorization': f'Bearer {auth_token}'},
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 201
            json_data = response.get_json()
            assert json_data['property']['address'] == '123 Main St'


class TestPropertySearch:
    """Test property search/creation endpoint"""
    
    def test_search_success(self, client, auth_token):
        """Test creating property with address only"""
        with patch('app.routes.properties.get_admin_db') as mock_admin:
            mock_db_result = Mock()
            mock_db_result.data = [{
                'id': 'property-456',
                'address': '456 Oak Ave',
                'status': 'address_only',
                'created_at': '2025-10-04T12:00:00Z'
            }]
            mock_admin.return_value.table.return_value.insert.return_value.execute.return_value = mock_db_result
            
            response = client.post(
                '/api/properties/search',
                json={'address': '456 Oak Ave'},
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            
            assert response.status_code == 201
            json_data = response.get_json()
            assert json_data['property']['address'] == '456 Oak Ave'
            assert json_data['property']['status'] == 'address_only'
    
    def test_search_missing_address(self, client, auth_token):
        """Test search without address"""
        response = client.post(
            '/api/properties/search',
            json={},
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'address' in json_data['error'].lower()
    
    def test_search_invalid_address(self, client, auth_token):
        """Test search with too short address"""
        response = client.post(
            '/api/properties/search',
            json={'address': '123'},
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'invalid' in json_data['error'].lower()


class TestListProperties:
    """Test list properties endpoint"""
    
    def test_list_success(self, client, auth_token):
        """Test listing user's properties"""
        with patch('app.routes.properties.get_db') as mock_db:
            mock_result = Mock()
            mock_result.data = [
                {'id': 'prop-1', 'address': '123 Main St', 'status': 'complete'},
                {'id': 'prop-2', 'address': '456 Oak Ave', 'status': 'uploaded'}
            ]
            
            mock_db.return_value.table.return_value.select.return_value.eq.return_value.range.return_value.execute.return_value = mock_result
            
            response = client.get(
                '/api/properties/',
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            
            assert response.status_code == 200
            json_data = response.get_json()
            assert len(json_data['properties']) == 2
    
    def test_list_with_status_filter(self, client, auth_token):
        """Test listing with status filter"""
        with patch('app.routes.properties.get_db') as mock_db:
            mock_result = Mock()
            mock_result.data = [
                {'id': 'prop-1', 'address': '123 Main St', 'status': 'complete'}
            ]
            
            mock_query = Mock()
            mock_query.eq.return_value.range.return_value.execute.return_value = mock_result
            mock_db.return_value.table.return_value.select.return_value.eq.return_value = mock_query
            
            response = client.get(
                '/api/properties/?status=complete',
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            
            assert response.status_code == 200


class TestGetProperty:
    """Test get single property endpoint"""
    
    def test_get_success(self, client, auth_token):
        """Test getting a specific property"""
        with patch('app.routes.properties.get_db') as mock_db:
            mock_result = Mock()
            mock_result.data = [{
                'id': 'property-123',
                'address': '123 Main St',
                'status': 'complete',
                'floor_plan_data': {'rooms': 3}
            }]
            
            mock_db.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_result
            
            response = client.get(
                '/api/properties/property-123',
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            
            assert response.status_code == 200
            json_data = response.get_json()
            assert json_data['property']['id'] == 'property-123'
    
    def test_get_not_found(self, client, auth_token):
        """Test getting non-existent property"""
        with patch('app.routes.properties.get_db') as mock_db:
            mock_result = Mock()
            mock_result.data = []
            
            mock_db.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_result
            
            response = client.get(
                '/api/properties/nonexistent',
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            
            assert response.status_code == 404


class TestDeleteProperty:
    """Test delete property endpoint"""
    
    def test_delete_success(self, client, auth_token):
        """Test deleting a property"""
        with patch('app.routes.properties.get_db') as mock_db, \
             patch('app.routes.properties.get_admin_db') as mock_admin:
            
            # Mock get property
            mock_result = Mock()
            mock_result.data = [{
                'id': 'property-123',
                'floor_plan_path': 'user/floor-plan.png'
            }]
            mock_db.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_result
            
            # Mock storage delete
            mock_storage = Mock()
            mock_admin.return_value.storage = mock_storage
            
            # Mock db delete
            mock_admin.return_value.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = None
            
            response = client.delete(
                '/api/properties/property-123',
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            
            assert response.status_code == 200
            json_data = response.get_json()
            assert 'deleted' in json_data['message'].lower()
    
    def test_delete_not_found(self, client, auth_token):
        """Test deleting non-existent property"""
        with patch('app.routes.properties.get_db') as mock_db:
            mock_result = Mock()
            mock_result.data = []
            
            mock_db.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_result
            
            response = client.delete(
                '/api/properties/nonexistent',
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            
            assert response.status_code == 404


class TestAuthentication:
    """Test authentication requirements"""
    
    def test_upload_requires_auth(self, client):
        """Test upload requires authentication"""
        data = {
            'file': (io.BytesIO(b'fake image data'), 'test.png')
        }
        
        response = client.post(
            '/api/properties/upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 401
    
    def test_list_requires_auth(self, client):
        """Test list requires authentication"""
        response = client.get('/api/properties/')
        assert response.status_code == 401
