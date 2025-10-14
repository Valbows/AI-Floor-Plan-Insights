"""
Analytics API Routes - Phase 4
Endpoints for regression models, price prediction, and property comparison

Features:
- Train regression model on property data
- Predict property prices
- Compare two properties side-by-side
- Get model performance metrics
- Calculate square footage impact
"""

import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.supabase_client import get_db, get_admin_db
from app.services.regression_models import (
    PropertyRegressionModel,
    PropertyFeatures,
    format_comparison_report
)

logger = logging.getLogger(__name__)

# Create blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_property_features_from_db(property_id: str, user_id: str) -> PropertyFeatures:
    """
    Retrieve property features from database
    
    Args:
        property_id: Property UUID
        user_id: User UUID for authorization
        
    Returns:
        PropertyFeatures object
        
    Raises:
        ValueError: If property not found or unauthorized
    """
    db = get_db()
    
    # Get property with measurements
    result = db.table('properties')\
        .select('*, floor_plan_measurements(*)')\
        .eq('id', property_id)\
        .eq('agent_id', user_id)\
        .single()\
        .execute()
    
    if not result.data:
        raise ValueError("Property not found or unauthorized")
    
    prop = result.data
    measurements = prop.get('floor_plan_measurements')
    
    if not measurements:
        raise ValueError("Property has no floor plan measurements")
    
    # Parse into PropertyFeatures
    extracted_data = prop.get('extracted_data', {}) or {}
    rooms = measurements.get('rooms', []) or []
    detected_features = measurements.get('detected_features', {}) or {}
    
    # Room statistics
    room_sqfts = [r.get('sqft', 0) for r in rooms if isinstance(r, dict) and r.get('sqft')]
    room_count = len(room_sqfts)
    avg_room_sqft = sum(room_sqfts) / room_count if room_count > 0 else 0.0
    largest_room_sqft = max(room_sqfts) if room_sqfts else 0
    smallest_room_sqft = min(room_sqfts) if room_sqfts else 0
    
    # Amenities
    totals = detected_features.get('totals', {}) if isinstance(detected_features, dict) else {}
    num_doors = totals.get('doors', 0)
    num_windows = totals.get('windows', 0)
    closets = totals.get('closets', 0)
    
    # Check for specific amenities
    room_list = extracted_data.get('rooms', []) or []
    has_garage = any('garage' in str(r.get('type', '')).lower() for r in room_list if isinstance(r, dict))
    has_fireplace = any('fireplace' in str(r.get('features', [])) for r in room_list if isinstance(r, dict))
    has_balcony = any('balcony' in str(r.get('features', [])) for r in room_list if isinstance(r, dict))
    
    features = PropertyFeatures(
        property_id=property_id,
        bedrooms=extracted_data.get('bedrooms', 0),
        bathrooms=extracted_data.get('bathrooms', 0.0),
        total_sqft=measurements.get('total_square_feet', 0),
        room_count=room_count,
        avg_room_sqft=avg_room_sqft,
        largest_room_sqft=largest_room_sqft,
        smallest_room_sqft=smallest_room_sqft,
        has_garage=1 if has_garage else 0,
        has_fireplace=1 if has_fireplace else 0,
        has_balcony=1 if has_balcony else 0,
        has_closets=1 if closets > 0 else 0,
        num_doors=num_doors,
        num_windows=num_windows,
        quality_score=measurements.get('quality_score', 0),
        confidence=measurements.get('total_square_feet_confidence', 0.0) or 0.0
    )
    
    return features


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@analytics_bp.route('/model/train', methods=['POST'])
@jwt_required()
def train_model():
    """
    Train regression model on all user's properties
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Request Body:
        {
            "model_type": "ridge" | "linear" | "random_forest" (optional, default: ridge),
            "min_properties": 10 (optional, default: 10)
        }
    
    Returns:
        {
            "success": true,
            "model_type": "ridge",
            "performance": {
                "r2_score": 0.85,
                "mae": 15000,
                "rmse": 18000,
                "mean_cv_score": 0.82
            },
            "feature_importance": {
                "total_sqft": 0.35,
                "bedrooms": 0.20,
                ...
            },
            "num_properties": 25,
            "num_predictions": 25
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        model_type = data.get('model_type', 'ridge')
        min_properties = data.get('min_properties', 10)
        
        if model_type not in ['ridge', 'linear', 'random_forest']:
            return jsonify({
                'error': 'Invalid model type',
                'valid_types': ['ridge', 'linear', 'random_forest']
            }), 400
        
        logger.info(f"Training {model_type} model for user {user_id}")
        
        # Initialize model with database
        db = get_admin_db()
        model = PropertyRegressionModel(db_client=db)
        
        # Extract features
        features_list = model.extract_property_features(min_properties=min_properties)
        
        if not features_list:
            return jsonify({
                'error': 'Insufficient data',
                'message': f'Need at least {min_properties} properties with measurements and prices',
                'current_properties': 0
            }), 400
        
        # Train model
        results = model.build_room_dimension_model(features_list, model_type=model_type)
        
        if not results:
            return jsonify({
                'error': 'Model training failed',
                'message': 'Could not train model with available data'
            }), 500
        
        # Return results
        return jsonify({
            'success': True,
            'model_type': results.model_type,
            'performance': {
                'r2_score': round(results.r2_score, 4),
                'mae': round(results.mae, 2),
                'rmse': round(results.rmse, 2),
                'mean_cv_score': round(sum(results.cross_val_scores) / len(results.cross_val_scores), 4) if results.cross_val_scores else 0
            },
            'feature_importance': results.feature_importance,
            'num_properties': len(features_list),
            'num_predictions': len(results.predictions),
            'coefficients': results.coefficients,
            'intercept': results.intercept
        }), 200
    
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return jsonify({
            'error': 'Model training failed',
            'message': str(e)
        }), 500


@analytics_bp.route('/predict/<property_id>', methods=['GET'])
@jwt_required()
def predict_price(property_id):
    """
    Predict price for a specific property
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Path Parameters:
        property_id: Property UUID
    
    Query Parameters:
        train_model: If true, train model first (default: false)
    
    Returns:
        {
            "property_id": "uuid",
            "predicted_price": 450000,
            "price_per_sqft": 300.50,
            "confidence": "medium",
            "features": {
                "bedrooms": 3,
                "bathrooms": 2,
                "total_sqft": 1500,
                ...
            },
            "sqft_impact": 37.54
        }
    """
    try:
        user_id = get_jwt_identity()
        train_first = request.args.get('train_model', 'false').lower() == 'true'
        
        logger.info(f"Predicting price for property {property_id}")
        
        # Get property features
        features = get_property_features_from_db(property_id, user_id)
        
        # Initialize model
        db = get_admin_db()
        model = PropertyRegressionModel(db_client=db)
        
        # Train model if requested
        if train_first:
            all_features = model.extract_property_features(min_properties=5)
            if len(all_features) >= 5:
                model.build_room_dimension_model(all_features)
        
        # Predict price
        predicted_price = model.predict_price(features)
        
        if predicted_price is None:
            return jsonify({
                'error': 'Prediction failed',
                'message': 'Model not trained. Set train_model=true to train first'
            }), 400
        
        # Calculate price per sqft
        price_per_sqft = predicted_price / features.total_sqft if features.total_sqft > 0 else 0
        
        # Get sqft impact
        sqft_impact = model.calculate_sqft_impact()
        
        # Determine confidence
        if features.confidence >= 0.9:
            confidence = 'high'
        elif features.confidence >= 0.7:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return jsonify({
            'property_id': property_id,
            'predicted_price': round(predicted_price, 2),
            'price_per_sqft': round(price_per_sqft, 2),
            'confidence': confidence,
            'features': {
                'bedrooms': features.bedrooms,
                'bathrooms': features.bathrooms,
                'total_sqft': features.total_sqft,
                'room_count': features.room_count,
                'has_garage': bool(features.has_garage),
                'has_fireplace': bool(features.has_fireplace),
                'has_balcony': bool(features.has_balcony),
                'num_doors': features.num_doors,
                'num_windows': features.num_windows
            },
            'sqft_impact': round(sqft_impact, 2) if sqft_impact else None,
            'quality_score': features.quality_score
        }), 200
    
    except ValueError as e:
        return jsonify({
            'error': 'Property not found',
            'message': str(e)
        }), 404
    
    except Exception as e:
        logger.error(f"Error predicting price: {e}")
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e)
        }), 500


@analytics_bp.route('/compare', methods=['POST'])
@jwt_required()
def compare_properties():
    """
    Compare two properties and show price differences
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Request Body:
        {
            "property_a_id": "uuid",
            "property_b_id": "uuid",
            "train_model": false (optional)
        }
    
    Returns:
        {
            "property_a_id": "uuid",
            "property_b_id": "uuid",
            "differences": {
                "bedrooms": 1,
                "bathrooms": 0.5,
                "sqft": 500
            },
            "price_impact": {
                "total_difference": 90000,
                "price_per_sqft_diff": -10.50,
                "sqft_impact": 18770,
                "bedroom_impact": 15000,
                "bathroom_impact": 5000,
                "amenity_impact": 20000
            },
            "summary": "Property A has more bedroom, more bathroom, 500 more sqft...",
            "recommendation": "Property A offers better value per square foot..."
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        property_a_id = data.get('property_a_id')
        property_b_id = data.get('property_b_id')
        train_first = data.get('train_model', False)
        
        if not property_a_id or not property_b_id:
            return jsonify({
                'error': 'Missing required fields',
                'required': ['property_a_id', 'property_b_id']
            }), 400
        
        logger.info(f"Comparing properties {property_a_id} vs {property_b_id}")
        
        # Get features for both properties
        features_a = get_property_features_from_db(property_a_id, user_id)
        features_b = get_property_features_from_db(property_b_id, user_id)
        
        # Initialize model
        db = get_admin_db()
        model = PropertyRegressionModel(db_client=db)
        
        # Train model if requested
        if train_first:
            all_features = model.extract_property_features(min_properties=5)
            if len(all_features) >= 5:
                model.build_room_dimension_model(all_features)
        
        # Compare properties
        comparison = model.compare_properties(features_a, features_b)
        
        return jsonify({
            'property_a_id': property_a_id,
            'property_b_id': property_b_id,
            'property_a': {
                'bedrooms': features_a.bedrooms,
                'bathrooms': features_a.bathrooms,
                'total_sqft': features_a.total_sqft
            },
            'property_b': {
                'bedrooms': features_b.bedrooms,
                'bathrooms': features_b.bathrooms,
                'total_sqft': features_b.total_sqft
            },
            'differences': {
                'bedrooms': comparison.bedroom_diff,
                'bathrooms': comparison.bathroom_diff,
                'sqft': comparison.sqft_diff
            },
            'price_impact': {
                'total_difference': round(comparison.predicted_price_diff, 2),
                'price_per_sqft_diff': round(comparison.price_per_sqft_diff, 2),
                'sqft_impact': round(comparison.sqft_impact, 2),
                'bedroom_impact': round(comparison.bedroom_impact, 2),
                'bathroom_impact': round(comparison.bathroom_impact, 2),
                'amenity_impact': round(comparison.amenity_impact, 2)
            },
            'summary': comparison.comparison_summary,
            'recommendation': comparison.recommendation
        }), 200
    
    except ValueError as e:
        return jsonify({
            'error': 'Property not found',
            'message': str(e)
        }), 404
    
    except Exception as e:
        logger.error(f"Error comparing properties: {e}")
        return jsonify({
            'error': 'Comparison failed',
            'message': str(e)
        }), 500


@analytics_bp.route('/sqft-impact', methods=['GET'])
@jwt_required()
def get_sqft_impact():
    """
    Calculate price impact per square foot
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Query Parameters:
        train_model: If true, train model first (default: false)
    
    Returns:
        {
            "price_per_sqft": 37.54,
            "examples": {
                "100_sqft": 3754,
                "500_sqft": 18770,
                "1000_sqft": 37540
            },
            "model_trained": true
        }
    """
    try:
        user_id = get_jwt_identity()
        train_first = request.args.get('train_model', 'false').lower() == 'true'
        
        # Initialize model
        db = get_admin_db()
        model = PropertyRegressionModel(db_client=db)
        
        # Train model if requested
        if train_first:
            all_features = model.extract_property_features(min_properties=5)
            if len(all_features) >= 5:
                results = model.build_room_dimension_model(all_features)
                if not results:
                    return jsonify({
                        'error': 'Model training failed',
                        'message': 'Could not train model with available data'
                    }), 500
        
        # Calculate sqft impact
        sqft_impact = model.calculate_sqft_impact()
        
        if sqft_impact is None:
            return jsonify({
                'error': 'Calculation failed',
                'message': 'Model not trained. Set train_model=true to train first'
            }), 400
        
        return jsonify({
            'price_per_sqft': round(sqft_impact, 2),
            'examples': {
                '100_sqft': round(sqft_impact * 100, 0),
                '500_sqft': round(sqft_impact * 500, 0),
                '1000_sqft': round(sqft_impact * 1000, 0)
            },
            'model_trained': True
        }), 200
    
    except Exception as e:
        logger.error(f"Error calculating sqft impact: {e}")
        return jsonify({
            'error': 'Calculation failed',
            'message': str(e)
        }), 500


@analytics_bp.route('/quality-score/<property_id>', methods=['GET'])
@jwt_required()
def get_quality_score(property_id):
    """
    Calculate Floor Plan Quality Score for a property
    
    Quality Score is based on:
    - Measurement completeness (all rooms measured)
    - Image clarity and resolution
    - Feature detection accuracy
    - Data consistency
    
    Returns score 0-100 with detailed breakdown
    """
    try:
        user_id = get_jwt_identity()
        db = get_db()
        
        # Get property and measurements (use execute() without single() to avoid exception)
        property_result = db.table('properties')\
            .select('*, floor_plan_measurements(*)')\
            .eq('id', property_id)\
            .eq('agent_id', user_id)\
            .execute()
        
        if not property_result.data or len(property_result.data) == 0:
            return jsonify({
                'error': 'Property not found',
                'message': f'Property with ID {property_id} not found or unauthorized'
            }), 404
        
        property_data = property_result.data[0]
        measurements = property_data.get('floor_plan_measurements')
        
        if not measurements:
            return jsonify({
                'error': 'No measurements',
                'message': 'Property has no floor plan measurements'
            }), 400
        
        # Calculate quality score components
        quality_score = measurements.get('quality_score', 0)
        quality_factors = measurements.get('quality_factors', {})
        
        # Build detailed breakdown
        breakdown = {
            'completeness': quality_factors.get('completeness', 0),
            'accuracy': quality_factors.get('accuracy', 0),
            'clarity': quality_factors.get('clarity', 0),
            'consistency': quality_factors.get('consistency', 0)
        }
        
        # Determine quality level
        if quality_score >= 80:
            quality_level = 'excellent'
            color = 'green'
        elif quality_score >= 60:
            quality_level = 'good'
            color = 'blue'
        elif quality_score >= 40:
            quality_level = 'fair'
            color = 'yellow'
        else:
            quality_level = 'poor'
            color = 'red'
        
        # Get room count and total sqft
        rooms = measurements.get('rooms', [])
        total_sqft = measurements.get('total_square_feet', 0)
        
        return jsonify({
            'property_id': property_id,
            'quality_score': quality_score,
            'quality_level': quality_level,
            'color': color,
            'breakdown': breakdown,
            'metadata': {
                'rooms_measured': len(rooms),
                'total_square_feet': total_sqft,
                'measurement_method': measurements.get('measurement_method', 'unknown'),
                'confidence': measurements.get('total_square_feet_confidence', 0)
            },
            'recommendations': get_quality_recommendations(quality_score, breakdown)
        }), 200
    
    except Exception as e:
        logger.error(f"Error calculating quality score: {e}")
        return jsonify({
            'error': 'Quality score calculation failed',
            'message': str(e)
        }), 500


def get_quality_recommendations(score: int, breakdown: dict) -> list:
    """Generate recommendations based on quality score"""
    recommendations = []
    
    if score < 80:
        if breakdown.get('completeness', 0) < 70:
            recommendations.append('Ensure all rooms are clearly visible in the floor plan')
        if breakdown.get('accuracy', 0) < 70:
            recommendations.append('Verify measurements match actual dimensions')
        if breakdown.get('clarity', 0) < 70:
            recommendations.append('Use a higher resolution image for better analysis')
        if breakdown.get('consistency', 0) < 70:
            recommendations.append('Check for inconsistent scaling in the floor plan')
    
    if not recommendations:
        recommendations.append('Floor plan quality is excellent - no improvements needed')
    
    return recommendations


@analytics_bp.route('/property-analytics/<property_id>', methods=['GET'])
@jwt_required()
def get_property_analytics(property_id):
    """
    Get comprehensive analytics for a property in one call
    
    Returns:
    - Predicted price
    - Quality score
    - Feature breakdown
    - Model performance
    
    Useful for frontend to load all analytics data at once
    """
    try:
        user_id = get_jwt_identity()
        
        # Get quality score
        quality_response = get_quality_score(property_id)
        quality_data = quality_response[0].get_json() if quality_response[1] == 200 else None
        
        # Get price prediction - directly call with params
        try:
            # Try to get prediction (it will handle model training internally)
            features = get_property_features_from_db(property_id, user_id)
            
            # Check if model is trained, if not return None for prediction
            if not hasattr(PropertyRegressionModel, '_instance') or PropertyRegressionModel._instance is None:
                prediction_data = {'message': 'Model not trained. Call /api/analytics/model/train first'}
            else:
                model = PropertyRegressionModel()
                predicted_price, confidence = model.predict(features)
                prediction_data = {
                    'predicted_price': predicted_price,
                    'confidence': confidence,
                    'features': features.__dict__
                }
        except Exception as pred_error:
            logger.warning(f"Price prediction failed: {pred_error}")
            prediction_data = {'error': str(pred_error)}
        
        # Combine results
        return jsonify({
            'property_id': property_id,
            'quality_score': quality_data,
            'price_prediction': prediction_data,
            'timestamp': '2025-10-13T22:30:00Z'
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting property analytics: {e}")
        return jsonify({
            'error': 'Analytics retrieval failed',
            'message': str(e)
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@analytics_bp.errorhandler(400)
def bad_request(e):
    """Handle 400 Bad Request errors"""
    return jsonify({
        'error': 'Bad Request',
        'message': str(e)
    }), 400


@analytics_bp.errorhandler(404)
def not_found(e):
    """Handle 404 Not Found errors"""
    return jsonify({
        'error': 'Not Found',
        'message': str(e)
    }), 404


@analytics_bp.errorhandler(500)
def internal_error(e):
    """Handle 500 Internal Server errors"""
    logger.error(f"Internal server error: {e}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500
