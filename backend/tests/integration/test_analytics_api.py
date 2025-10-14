"""
Integration Tests for Analytics API - Phase 4
Tests regression model endpoints, price prediction, and property comparison
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask_jwt_extended import create_access_token
from app import create_app
from app.services.regression_models import PropertyFeatures, RegressionResults, ComparisonResult


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Create JWT authentication headers with valid token"""
    with app.app_context():
        token = create_access_token(identity='user-123')
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def mock_property_features():
    """Mock property features"""
    return PropertyFeatures(
        property_id='test-property-id',
        bedrooms=3,
        bathrooms=2.0,
        total_sqft=1500,
        room_count=8,
        avg_room_sqft=187.5,
        largest_room_sqft=300,
        smallest_room_sqft=50,
        has_garage=1,
        has_fireplace=1,
        has_balcony=0,
        has_closets=1,
        num_doors=8,
        num_windows=12,
        quality_score=95,
        confidence=0.9
    )


@pytest.fixture
def mock_regression_results():
    """Mock regression results"""
    return RegressionResults(
        model_type='ridge',
        r2_score=0.85,
        mae=15000.0,
        rmse=18000.0,
        cross_val_scores=[0.82, 0.84, 0.86, 0.88, 0.80],
        feature_importance={
            'total_sqft': 0.35,
            'bedrooms': 0.20,
            'bathrooms': 0.15,
            'room_count': 0.10,
            'has_garage': 0.08,
            'avg_room_sqft': 0.07,
            'largest_room_sqft': 0.05
        },
        predictions={'prop-1': 450000, 'prop-2': 320000},
        coefficients={'total_sqft': 150.5, 'bedrooms': 25000.0},
        intercept=50000.0
    )


# ============================================================================
# TEST MODEL TRAINING ENDPOINT
# ============================================================================

@patch('app.routes.analytics.get_jwt_identity')
@patch('app.routes.analytics.get_admin_db')
@patch('app.routes.analytics.PropertyRegressionModel')
def test_train_model_success(mock_model_class, mock_db, mock_jwt, client, auth_headers, mock_regression_results):
    """Test successful model training"""
    mock_jwt.return_value = 'user-123'
    
    # Mock model instance
    mock_model = Mock()
    mock_model.extract_property_features.return_value = [Mock() for _ in range(15)]
    mock_model.build_room_dimension_model.return_value = mock_regression_results
    mock_model_class.return_value = mock_model
    
    response = client.post(
        '/api/analytics/model/train',
        json={'model_type': 'ridge'},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert data['model_type'] == 'ridge'
    assert 'performance' in data
    assert data['performance']['r2_score'] == 0.85
    assert data['performance']['mae'] == 15000.0
    assert 'feature_importance' in data
    assert data['num_properties'] == 15


@patch('app.routes.analytics.get_jwt_identity')
@patch('app.routes.analytics.get_admin_db')
@patch('app.routes.analytics.PropertyRegressionModel')
def test_train_model_insufficient_data(mock_model_class, mock_db, mock_jwt, client, auth_headers):
    """Test model training with insufficient data"""
    mock_jwt.return_value = 'user-123'
    
    mock_model = Mock()
    mock_model.extract_property_features.return_value = []
    mock_model_class.return_value = mock_model
    
    response = client.post(
        '/api/analytics/model/train',
        json={'model_type': 'ridge'},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert 'error' in data
    assert data['error'] == 'Insufficient data'


@patch('app.routes.analytics.get_jwt_identity')
def test_train_model_invalid_type(mock_jwt, client, auth_headers):
    """Test model training with invalid model type"""
    mock_jwt.return_value = 'user-123'
    
    response = client.post(
        '/api/analytics/model/train',
        json={'model_type': 'invalid_type'},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert 'error' in data
    assert data['error'] == 'Invalid model type'
    assert 'valid_types' in data


# ============================================================================
# TEST PRICE PREDICTION ENDPOINT
# ============================================================================

@patch('app.routes.analytics.get_jwt_identity')
@patch('app.routes.analytics.get_property_features_from_db')
@patch('app.routes.analytics.get_admin_db')
@patch('app.routes.analytics.PropertyRegressionModel')
def test_predict_price_success(mock_model_class, mock_db, mock_get_features, mock_jwt, client, auth_headers, mock_property_features):
    """Test successful price prediction"""
    mock_jwt.return_value = 'user-123'
    mock_get_features.return_value = mock_property_features
    
    mock_model = Mock()
    mock_model.predict_price.return_value = 450000.0
    mock_model.calculate_sqft_impact.return_value = 37.54
    mock_model_class.return_value = mock_model
    
    response = client.get(
        '/api/analytics/predict/test-property-id',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['property_id'] == 'test-property-id'
    assert data['predicted_price'] == 450000.0
    assert 'price_per_sqft' in data
    assert data['confidence'] == 'high'  # confidence >= 0.9
    assert 'features' in data
    assert data['features']['bedrooms'] == 3
    assert data['features']['bathrooms'] == 2.0


@patch('app.routes.analytics.get_jwt_identity')
@patch('app.routes.analytics.get_property_features_from_db')
@patch('app.routes.analytics.get_admin_db')
@patch('app.routes.analytics.PropertyRegressionModel')
def test_predict_price_not_trained(mock_model_class, mock_db, mock_get_features, mock_jwt, client, auth_headers, mock_property_features):
    """Test price prediction without trained model"""
    mock_jwt.return_value = 'user-123'
    mock_get_features.return_value = mock_property_features
    
    mock_model = Mock()
    mock_model.predict_price.return_value = None  # Model not trained
    mock_model_class.return_value = mock_model
    
    response = client.get(
        '/api/analytics/predict/test-property-id',
        headers=auth_headers
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert 'error' in data
    assert 'Model not trained' in data['message']


@patch('app.routes.analytics.get_jwt_identity')
@patch('app.routes.analytics.get_property_features_from_db')
def test_predict_price_property_not_found(mock_get_features, mock_jwt, client, auth_headers):
    """Test price prediction for non-existent property"""
    mock_jwt.return_value = 'user-123'
    mock_get_features.side_effect = ValueError("Property not found or unauthorized")
    
    response = client.get(
        '/api/analytics/predict/nonexistent-id',
        headers=auth_headers
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    
    assert 'error' in data
    assert data['error'] == 'Property not found'


# ============================================================================
# TEST PROPERTY COMPARISON ENDPOINT
# ============================================================================

@patch('app.routes.analytics.get_jwt_identity')
@patch('app.routes.analytics.get_property_features_from_db')
@patch('app.routes.analytics.get_admin_db')
@patch('app.routes.analytics.PropertyRegressionModel')
def test_compare_properties_success(mock_model_class, mock_db, mock_get_features, mock_jwt, client, auth_headers):
    """Test successful property comparison"""
    mock_jwt.return_value = 'user-123'
    
    # Mock features for two properties
    features_a = PropertyFeatures(
        property_id='prop-a',
        bedrooms=3,
        bathrooms=2.0,
        total_sqft=1500,
        room_count=8,
        avg_room_sqft=187.5,
        largest_room_sqft=300
    )
    
    features_b = PropertyFeatures(
        property_id='prop-b',
        bedrooms=3,
        bathrooms=1.5,
        total_sqft=1400,
        room_count=7,
        avg_room_sqft=200.0,
        largest_room_sqft=280
    )
    
    mock_get_features.side_effect = [features_a, features_b]
    
    # Mock comparison result
    mock_comparison = ComparisonResult(
        property_a_id='prop-a',
        property_b_id='prop-b',
        bedroom_diff=0,
        bathroom_diff=0.5,
        sqft_diff=100,
        predicted_price_diff=25000.0,
        price_per_sqft_diff=10.5,
        sqft_impact=3754.0,
        bedroom_impact=0.0,
        bathroom_impact=5000.0,
        amenity_impact=0.0,
        comparison_summary="Property A has more bathroom, 100 more sqft",
        recommendation="Property A offers better value"
    )
    
    mock_model = Mock()
    mock_model.compare_properties.return_value = mock_comparison
    mock_model_class.return_value = mock_model
    
    response = client.post(
        '/api/analytics/compare',
        json={
            'property_a_id': 'prop-a',
            'property_b_id': 'prop-b'
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['property_a_id'] == 'prop-a'
    assert data['property_b_id'] == 'prop-b'
    assert 'differences' in data
    assert data['differences']['bathroom_diff'] == 0.5
    assert 'price_impact' in data
    assert data['price_impact']['total_difference'] == 25000.0
    assert 'summary' in data
    assert 'recommendation' in data


@patch('app.routes.analytics.get_jwt_identity')
def test_compare_properties_missing_fields(mock_jwt, client, auth_headers):
    """Test property comparison with missing fields"""
    mock_jwt.return_value = 'user-123'
    
    response = client.post(
        '/api/analytics/compare',
        json={'property_a_id': 'prop-a'},  # Missing property_b_id
        headers=auth_headers
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert 'error' in data
    assert 'Missing required fields' in data['error']


# ============================================================================
# TEST SQFT IMPACT ENDPOINT
# ============================================================================

@patch('app.routes.analytics.get_jwt_identity')
@patch('app.routes.analytics.get_admin_db')
@patch('app.routes.analytics.PropertyRegressionModel')
def test_get_sqft_impact_success(mock_model_class, mock_db, mock_jwt, client, auth_headers):
    """Test successful sqft impact calculation"""
    mock_jwt.return_value = 'user-123'
    
    mock_model = Mock()
    mock_model.calculate_sqft_impact.return_value = 37.54
    mock_model_class.return_value = mock_model
    
    response = client.get(
        '/api/analytics/sqft-impact',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['price_per_sqft'] == 37.54
    assert 'examples' in data
    assert data['examples']['100_sqft'] == 3754
    assert data['examples']['500_sqft'] == 18770
    assert data['examples']['1000_sqft'] == 37540
    assert data['model_trained'] is True


@patch('app.routes.analytics.get_jwt_identity')
@patch('app.routes.analytics.get_admin_db')
@patch('app.routes.analytics.PropertyRegressionModel')
def test_get_sqft_impact_not_trained(mock_model_class, mock_db, mock_jwt, client, auth_headers):
    """Test sqft impact without trained model"""
    mock_jwt.return_value = 'user-123'
    
    mock_model = Mock()
    mock_model.calculate_sqft_impact.return_value = None
    mock_model_class.return_value = mock_model
    
    response = client.get(
        '/api/analytics/sqft-impact',
        headers=auth_headers
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert 'error' in data
    assert 'Model not trained' in data['message']


# ============================================================================
# TEST AUTHENTICATION
# ============================================================================

def test_endpoints_require_auth(client):
    """Test that all endpoints require authentication"""
    endpoints = [
        ('/api/analytics/model/train', 'POST'),
        ('/api/analytics/predict/test-id', 'GET'),
        ('/api/analytics/compare', 'POST'),
        ('/api/analytics/sqft-impact', 'GET')
    ]
    
    for endpoint, method in endpoints:
        if method == 'POST':
            response = client.post(endpoint, json={})
        else:
            response = client.get(endpoint)
        
        # Should return 401 Unauthorized without JWT token
        assert response.status_code == 401


# ============================================================================
# TEST ERROR HANDLING
# ============================================================================

@patch('app.routes.analytics.get_jwt_identity')
@patch('app.routes.analytics.get_admin_db')
@patch('app.routes.analytics.PropertyRegressionModel')
def test_train_model_handles_exception(mock_model_class, mock_db, mock_jwt, client, auth_headers):
    """Test that exceptions are handled gracefully"""
    mock_jwt.return_value = 'user-123'
    
    mock_model = Mock()
    mock_model.extract_property_features.side_effect = Exception("Database error")
    mock_model_class.return_value = mock_model
    
    response = client.post(
        '/api/analytics/model/train',
        json={'model_type': 'ridge'},
        headers=auth_headers
    )
    
    assert response.status_code == 500
    data = json.loads(response.data)
    
    assert 'error' in data
    assert data['error'] == 'Model training failed'


# ============================================================================
# TEST WITH TRAIN_MODEL PARAMETER
# ============================================================================

@patch('app.routes.analytics.get_jwt_identity')
@patch('app.routes.analytics.get_property_features_from_db')
@patch('app.routes.analytics.get_admin_db')
@patch('app.routes.analytics.PropertyRegressionModel')
def test_predict_with_train_first(mock_model_class, mock_db, mock_get_features, mock_jwt, client, auth_headers, mock_property_features, mock_regression_results):
    """Test prediction with train_model=true"""
    mock_jwt.return_value = 'user-123'
    mock_get_features.return_value = mock_property_features
    
    mock_model = Mock()
    mock_model.extract_property_features.return_value = [Mock() for _ in range(10)]
    mock_model.build_room_dimension_model.return_value = mock_regression_results
    mock_model.predict_price.return_value = 450000.0
    mock_model.calculate_sqft_impact.return_value = 37.54
    mock_model_class.return_value = mock_model
    
    response = client.get(
        '/api/analytics/predict/test-property-id?train_model=true',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify model was trained
    mock_model.build_room_dimension_model.assert_called_once()
    
    # Verify prediction was made
    assert data['predicted_price'] == 450000.0
