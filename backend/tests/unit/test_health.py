"""
Unit tests for health check endpoint
"""

import pytest
from app import create_app


@pytest.fixture
def client():
    """Create test client"""
    app = create_app('testing')
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test health check endpoint returns 200"""
    response = client.get('/health')
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'AI Floor Plan Insights API'
    assert 'version' in data


def test_health_check_response_structure(client):
    """Test health check returns proper JSON structure"""
    response = client.get('/health')
    
    data = response.get_json()
    assert isinstance(data, dict)
    assert len(data) == 3  # status, service, version
