"""
Unit Tests for Statistical Regression Models
Phase 3: Tests for property valuation and comparison algorithms
"""

import pytest
import numpy as np
from unittest.mock import Mock, MagicMock
from app.services.regression_models import (
    PropertyRegressionModel,
    PropertyFeatures,
    RegressionResults,
    ComparisonResult,
    format_comparison_report
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_properties():
    """Create sample property features for testing"""
    return [
        PropertyFeatures(
            property_id='prop-1',
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
            sale_price=450000,
            quality_score=95,
            confidence=0.9
        ),
        PropertyFeatures(
            property_id='prop-2',
            bedrooms=2,
            bathrooms=1.0,
            total_sqft=1000,
            room_count=5,
            avg_room_sqft=200.0,
            largest_room_sqft=250,
            smallest_room_sqft=80,
            has_garage=0,
            has_fireplace=0,
            has_balcony=1,
            has_closets=1,
            num_doors=6,
            num_windows=8,
            sale_price=320000,
            quality_score=85,
            confidence=0.8
        ),
        PropertyFeatures(
            property_id='prop-3',
            bedrooms=4,
            bathrooms=2.5,
            total_sqft=2000,
            room_count=10,
            avg_room_sqft=200.0,
            largest_room_sqft=350,
            smallest_room_sqft=60,
            has_garage=1,
            has_fireplace=1,
            has_balcony=1,
            has_closets=1,
            num_doors=10,
            num_windows=15,
            sale_price=580000,
            quality_score=98,
            confidence=0.95
        ),
        PropertyFeatures(
            property_id='prop-4',
            bedrooms=3,
            bathrooms=1.5,
            total_sqft=1400,
            room_count=7,
            avg_room_sqft=200.0,
            largest_room_sqft=280,
            smallest_room_sqft=70,
            has_garage=1,
            has_fireplace=0,
            has_balcony=0,
            has_closets=1,
            num_doors=7,
            num_windows=10,
            sale_price=410000,
            quality_score=90,
            confidence=0.85
        ),
        PropertyFeatures(
            property_id='prop-5',
            bedrooms=2,
            bathrooms=2.0,
            total_sqft=1200,
            room_count=6,
            avg_room_sqft=200.0,
            largest_room_sqft=260,
            smallest_room_sqft=75,
            has_garage=0,
            has_fireplace=1,
            has_balcony=0,
            has_closets=1,
            num_doors=6,
            num_windows=9,
            sale_price=360000,
            quality_score=88,
            confidence=0.82
        )
    ]


@pytest.fixture
def regression_model():
    """Create PropertyRegressionModel instance"""
    return PropertyRegressionModel(db_client=None)


@pytest.fixture
def trained_model(regression_model, sample_properties):
    """Create and train a regression model"""
    # Add more properties to meet minimum requirement
    extended_properties = sample_properties * 3  # 15 properties total
    
    # Vary prices slightly for each copy
    for i, prop in enumerate(extended_properties[5:10]):
        prop.sale_price = prop.sale_price * 1.05
        prop.property_id = f"{prop.property_id}-copy1"
    
    for i, prop in enumerate(extended_properties[10:15]):
        prop.sale_price = prop.sale_price * 0.95
        prop.property_id = f"{prop.property_id}-copy2"
    
    # Train the model
    results = regression_model.build_room_dimension_model(extended_properties, model_type='ridge')
    
    return regression_model, results


# ============================================================================
# TEST DATA EXTRACTION
# ============================================================================

def test_parse_property_row(regression_model):
    """Test parsing database row into PropertyFeatures"""
    row = {
        'property_id': 'test-id',
        'extracted_data': {
            'bedrooms': 3,
            'bathrooms': 2.0,
            'rooms': [
                {'type': 'bedroom', 'features': []},
                {'type': 'garage', 'features': []}
            ]
        },
        'total_square_feet': 1500,
        'quality_score': 95,
        'total_square_feet_confidence': 0.9,
        'rooms': [
            {'name': 'Living', 'sqft': 300},
            {'name': 'Kitchen', 'sqft': 200},
            {'name': 'Bedroom 1', 'sqft': 250}
        ],
        'detected_features': {
            'totals': {
                'doors': 8,
                'windows': 12,
                'closets': 2
            }
        },
        'comparables': [
            {'sale_price': 450000},
            {'sale_price': 460000},
            {'sale_price': 440000}
        ]
    }
    
    features = regression_model._parse_property_row(row)
    
    assert features is not None
    assert features.property_id == 'test-id'
    assert features.bedrooms == 3
    assert features.bathrooms == 2.0
    assert features.total_sqft == 1500
    assert features.room_count == 3
    assert features.has_garage == 1
    assert features.num_doors == 8
    assert features.num_windows == 12
    assert features.sale_price == 450000  # Median of comparables


def test_parse_property_row_missing_data(regression_model):
    """Test parsing row with missing data"""
    row = {
        'property_id': 'test-id',
        'extracted_data': {},
        'total_square_feet': 1000,
        'quality_score': None,
        'total_square_feet_confidence': None,
        'rooms': None,
        'detected_features': None,
        'comparables': []
    }
    
    features = regression_model._parse_property_row(row)
    
    assert features is not None
    assert features.bedrooms == 0
    assert features.bathrooms == 0.0
    assert features.room_count == 0
    assert features.sale_price is None


# ============================================================================
# TEST MODEL BUILDING
# ============================================================================

def test_build_room_dimension_model_success(regression_model, sample_properties):
    """Test successful model building"""
    # Extend to meet minimum requirement
    extended_properties = sample_properties * 3
    for i, prop in enumerate(extended_properties[5:]):
        prop.property_id = f"{prop.property_id}-copy{i}"
    
    results = regression_model.build_room_dimension_model(
        extended_properties,
        model_type='ridge'
    )
    
    assert results is not None
    assert isinstance(results, RegressionResults)
    assert results.model_type == 'ridge'
    assert 0 <= results.r2_score <= 1
    assert results.mae > 0
    assert results.rmse > 0
    assert len(results.feature_importance) > 0
    assert 'total_sqft' in results.feature_importance
    assert len(results.predictions) > 0


def test_build_model_insufficient_data(regression_model):
    """Test model building with insufficient data"""
    # Only 3 properties
    limited_data = [
        PropertyFeatures(
            property_id=f'prop-{i}',
            bedrooms=2,
            bathrooms=1.0,
            total_sqft=1000,
            room_count=5,
            avg_room_sqft=200,
            largest_room_sqft=250,
            sale_price=300000
        )
        for i in range(3)
    ]
    
    results = regression_model.build_room_dimension_model(limited_data)
    
    assert results is None


def test_build_model_no_prices(regression_model, sample_properties):
    """Test model building when no properties have prices"""
    for prop in sample_properties:
        prop.sale_price = None
    
    results = regression_model.build_room_dimension_model(sample_properties)
    
    assert results is None


def test_different_model_types(regression_model, sample_properties):
    """Test building different model types"""
    extended_properties = sample_properties * 3
    for i, prop in enumerate(extended_properties[5:]):
        prop.property_id = f"{prop.property_id}-copy{i}"
    
    # Test linear model
    linear_results = regression_model.build_room_dimension_model(
        extended_properties,
        model_type='linear'
    )
    assert linear_results.model_type == 'linear'
    
    # Test random forest
    rf_results = regression_model.build_room_dimension_model(
        extended_properties,
        model_type='random_forest'
    )
    assert rf_results.model_type == 'random_forest'


# ============================================================================
# TEST PRICE PREDICTION
# ============================================================================

def test_predict_price(trained_model):
    """Test price prediction for a property"""
    model, _ = trained_model
    
    test_property = PropertyFeatures(
        property_id='test-prop',
        bedrooms=3,
        bathrooms=2.0,
        total_sqft=1500,
        room_count=8,
        avg_room_sqft=187.5,
        largest_room_sqft=300,
        has_garage=1,
        has_fireplace=1,
        num_doors=8,
        num_windows=12
    )
    
    predicted_price = model.predict_price(test_property)
    
    assert predicted_price is not None
    assert predicted_price > 0
    assert 200000 < predicted_price < 1000000  # Reasonable range


def test_predict_price_no_trained_model(regression_model):
    """Test prediction without trained model"""
    test_property = PropertyFeatures(
        property_id='test-prop',
        bedrooms=3,
        bathrooms=2.0,
        total_sqft=1500,
        room_count=5,
        avg_room_sqft=300
    )
    
    predicted_price = regression_model.predict_price(test_property)
    
    assert predicted_price is None


def test_predict_price_larger_property(trained_model):
    """Test that larger properties predict higher prices"""
    model, _ = trained_model
    
    small_property = PropertyFeatures(
        property_id='small',
        bedrooms=2,
        bathrooms=1.0,
        total_sqft=1000,
        room_count=5,
        avg_room_sqft=200,
        largest_room_sqft=250
    )
    
    large_property = PropertyFeatures(
        property_id='large',
        bedrooms=4,
        bathrooms=3.0,
        total_sqft=2500,
        room_count=10,
        avg_room_sqft=250,
        largest_room_sqft=400,
        has_garage=1
    )
    
    small_price = model.predict_price(small_property)
    large_price = model.predict_price(large_property)
    
    assert small_price is not None
    assert large_price is not None
    assert large_price > small_price


# ============================================================================
# TEST IMPACT CALCULATIONS
# ============================================================================

def test_calculate_sqft_impact(trained_model):
    """Test calculation of price per square foot"""
    model, _ = trained_model
    
    sqft_impact = model.calculate_sqft_impact()
    
    assert sqft_impact is not None
    assert sqft_impact > 0
    assert sqft_impact < 1000  # Reasonable max $/sqft


def test_sqft_impact_no_model(regression_model):
    """Test sqft impact calculation without trained model"""
    sqft_impact = regression_model.calculate_sqft_impact()
    
    assert sqft_impact is None


# ============================================================================
# TEST PROPERTY COMPARISON
# ============================================================================

def test_compare_properties(trained_model, sample_properties):
    """Test property comparison algorithm"""
    model, _ = trained_model
    
    prop_a = sample_properties[0]  # 3BR/2BA, 1500 sqft
    prop_b = sample_properties[1]  # 2BR/1BA, 1000 sqft
    
    comparison = model.compare_properties(prop_a, prop_b)
    
    assert isinstance(comparison, ComparisonResult)
    assert comparison.bedroom_diff == 1
    assert comparison.bathroom_diff == 1.0
    assert comparison.sqft_diff == 500
    assert comparison.predicted_price_diff != 0
    assert len(comparison.comparison_summary) > 0
    assert len(comparison.recommendation) > 0


def test_compare_similar_properties(trained_model):
    """Test comparing very similar properties"""
    model, _ = trained_model
    
    prop_a = PropertyFeatures(
        property_id='a',
        bedrooms=3,
        bathrooms=2.0,
        total_sqft=1500,
        room_count=8,
        avg_room_sqft=187.5,
        largest_room_sqft=300
    )
    
    prop_b = PropertyFeatures(
        property_id='b',
        bedrooms=3,
        bathrooms=2.0,
        total_sqft=1500,
        room_count=8,
        avg_room_sqft=187.5,
        largest_room_sqft=300
    )
    
    comparison = model.compare_properties(prop_a, prop_b)
    
    assert comparison.bedroom_diff == 0
    assert comparison.bathroom_diff == 0.0
    assert comparison.sqft_diff == 0
    assert abs(comparison.predicted_price_diff) < 1000  # Should be very small


def test_compare_3br_2ba_vs_3br_1_5ba(trained_model):
    """Test specific comparison: 3BR/2BA vs 3BR/1.5BA"""
    model, _ = trained_model
    
    prop_a = PropertyFeatures(
        property_id='a',
        bedrooms=3,
        bathrooms=2.0,
        total_sqft=1500,
        room_count=8,
        avg_room_sqft=187.5,
        largest_room_sqft=300,
        has_garage=1
    )
    
    prop_b = PropertyFeatures(
        property_id='b',
        bedrooms=3,
        bathrooms=1.5,
        total_sqft=1500,
        room_count=8,
        avg_room_sqft=187.5,
        largest_room_sqft=300,
        has_garage=1
    )
    
    comparison = model.compare_properties(prop_a, prop_b)
    
    assert comparison.bedroom_diff == 0
    assert comparison.bathroom_diff == 0.5
    assert comparison.sqft_diff == 0
    # Property A should be valued higher (more bathrooms)
    assert comparison.predicted_price_diff > 0


# ============================================================================
# TEST UTILITY FUNCTIONS
# ============================================================================

def test_format_comparison_report(trained_model, sample_properties):
    """Test comparison report formatting"""
    model, _ = trained_model
    
    comparison = model.compare_properties(
        sample_properties[0],
        sample_properties[1]
    )
    
    report = format_comparison_report(comparison)
    
    assert isinstance(report, str)
    assert 'PROPERTY COMPARISON REPORT' in report
    assert 'Bedrooms:' in report
    assert 'Bathrooms:' in report
    assert 'Square Footage:' in report
    assert 'Total Price Difference:' in report
    assert 'Recommendation:' in report


def test_regression_results_to_dict(trained_model):
    """Test RegressionResults conversion to dictionary"""
    _, results = trained_model
    
    results_dict = results.to_dict()
    
    assert isinstance(results_dict, dict)
    assert 'model_type' in results_dict
    assert 'r2_score' in results_dict
    assert 'mae' in results_dict
    assert 'rmse' in results_dict
    assert 'feature_importance' in results_dict
    assert 'num_predictions' in results_dict


# ============================================================================
# TEST FEATURE MATRIX PREPARATION
# ============================================================================

def test_prepare_feature_matrix(regression_model, sample_properties):
    """Test feature matrix preparation"""
    X, y, feature_names = regression_model._prepare_feature_matrix(sample_properties)
    
    assert X.shape[0] == len(sample_properties)
    assert X.shape[1] == len(feature_names)
    assert y.shape[0] == len(sample_properties)
    assert 'total_sqft' in feature_names
    assert 'bedrooms' in feature_names
    assert 'bathrooms' in feature_names
    assert all(price > 0 for price in y)


# ============================================================================
# TEST EDGE CASES
# ============================================================================

def test_property_with_zero_sqft(trained_model):
    """Test prediction for property with zero square footage"""
    model, _ = trained_model
    
    prop = PropertyFeatures(
        property_id='zero-sqft',
        bedrooms=3,
        bathrooms=2.0,
        total_sqft=0,  # Invalid
        room_count=5,
        avg_room_sqft=0
    )
    
    # Should still return a prediction (model will handle it)
    price = model.predict_price(prop)
    assert price is not None


def test_property_with_negative_features(trained_model):
    """Test handling of invalid negative features"""
    model, _ = trained_model
    
    prop = PropertyFeatures(
        property_id='negative',
        bedrooms=3,
        bathrooms=2.0,
        total_sqft=1500,
        room_count=5,
        avg_room_sqft=300,
        # Negative values should be impossible but test handling
        num_doors=-1,
        num_windows=-1
    )
    
    # Model should still handle this (features will be scaled)
    price = model.predict_price(prop)
    assert price is not None
    assert price >= 0  # Ensure non-negative output


def test_model_with_single_feature(regression_model):
    """Test model performance with only sqft feature"""
    properties = [
        PropertyFeatures(
            property_id=f'prop-{i}',
            bedrooms=0,
            bathrooms=0,
            total_sqft=1000 + i * 100,
            room_count=0,
            avg_room_sqft=0,
            largest_room_sqft=0,
            sale_price=300000 + i * 30000
        )
        for i in range(15)
    ]
    
    results = regression_model.build_room_dimension_model(properties)
    
    assert results is not None
    assert results.r2_score > 0.5  # Should have decent correlation with just sqft


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_prediction_speed(trained_model, sample_properties):
    """Test that predictions are fast"""
    import time
    
    model, _ = trained_model
    
    start = time.time()
    for _ in range(100):
        model.predict_price(sample_properties[0])
    end = time.time()
    
    avg_time = (end - start) / 100
    assert avg_time < 0.01  # Should be < 10ms per prediction


def test_model_training_speed(regression_model):
    """Test that model training completes in reasonable time"""
    import time
    
    # Create 50 properties
    properties = [
        PropertyFeatures(
            property_id=f'prop-{i}',
            bedrooms=2 + (i % 3),
            bathrooms=1.0 + (i % 3) * 0.5,
            total_sqft=1000 + i * 50,
            room_count=5 + (i % 5),
            avg_room_sqft=200,
            largest_room_sqft=300,
            sale_price=300000 + i * 10000
        )
        for i in range(50)
    ]
    
    start = time.time()
    results = regression_model.build_room_dimension_model(properties)
    end = time.time()
    
    training_time = end - start
    assert training_time < 5.0  # Should complete in < 5 seconds
    assert results is not None
