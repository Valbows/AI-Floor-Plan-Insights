"""
Statistical Regression Models for Property Valuation
Phase 3: Extract room dimensions and build predictive pricing models

Features:
- Room dimension regression (sqft impact on price)
- Amenity impact model (features like garage, fireplace)
- Location factor model (neighborhood, proximity)
- Unified predictive pricing model
- "Each 1ft adds $X/sqft" calculations
- Property comparison algorithm (3BR/2BA vs 3BR/1.5BA)
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PropertyFeatures:
    """Property features for regression model"""
    property_id: str
    
    # Basic features
    bedrooms: int
    bathrooms: float
    total_sqft: int
    
    # Room dimensions
    room_count: int = 0
    avg_room_sqft: float = 0.0
    largest_room_sqft: int = 0
    smallest_room_sqft: int = 0
    
    # Amenities (binary: 0 or 1)
    has_garage: int = 0
    has_fireplace: int = 0
    has_balcony: int = 0
    has_closets: int = 0
    num_doors: int = 0
    num_windows: int = 0
    
    # Location (to be filled from market data)
    zip_code: Optional[str] = None
    neighborhood: Optional[str] = None
    
    # Price (target variable)
    sale_price: Optional[float] = None
    estimated_value: Optional[float] = None
    
    # Metadata
    quality_score: int = 0
    confidence: float = 0.0


@dataclass
class RegressionResults:
    """Results from regression model"""
    model_type: str
    r2_score: float
    mae: float
    rmse: float
    cross_val_scores: List[float]
    feature_importance: Dict[str, float]
    predictions: Dict[str, float]  # property_id -> predicted_price
    coefficients: Dict[str, float] = field(default_factory=dict)
    intercept: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'model_type': self.model_type,
            'r2_score': round(self.r2_score, 4),
            'mae': round(self.mae, 2),
            'rmse': round(self.rmse, 2),
            'mean_cv_score': round(np.mean(self.cross_val_scores), 4) if self.cross_val_scores else 0.0,
            'feature_importance': {k: round(v, 4) for k, v in self.feature_importance.items()},
            'coefficients': {k: round(v, 2) for k, v in self.coefficients.items()},
            'intercept': round(self.intercept, 2),
            'num_predictions': len(self.predictions)
        }


@dataclass
class ComparisonResult:
    """Property comparison results"""
    property_a_id: str
    property_b_id: str
    
    # Feature differences
    bedroom_diff: int
    bathroom_diff: float
    sqft_diff: int
    
    # Price impact
    predicted_price_diff: float
    price_per_sqft_diff: float
    
    # Detailed breakdown
    sqft_impact: float
    bedroom_impact: float
    bathroom_impact: float
    amenity_impact: float
    
    # Summary
    comparison_summary: str
    recommendation: str


# ============================================================================
# REGRESSION MODEL SERVICE
# ============================================================================

class PropertyRegressionModel:
    """
    Statistical regression model for property valuation
    Builds models based on room dimensions, amenities, and location
    """
    
    def __init__(self, db_client=None):
        """
        Initialize regression model service
        
        Args:
            db_client: Supabase client for database queries
        """
        self.db = db_client
        self.scaler = StandardScaler()
        self.models = {
            'linear': LinearRegression(),
            'ridge': Ridge(alpha=1.0),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        
        self.trained_model = None
        self.trained_model_type = None
        self.feature_names = []
        
        logger.info("PropertyRegressionModel initialized")
    
    # ========================================================================
    # STEP 1: DATA EXTRACTION
    # ========================================================================
    
    def extract_property_features(self, min_properties: int = 10) -> List[PropertyFeatures]:
        """
        Extract room dimensions and features from all properties in database
        
        Args:
            min_properties: Minimum properties needed to build model
            
        Returns:
            List of PropertyFeatures objects
        """
        logger.info("Extracting property features from database...")
        
        if not self.db:
            raise ValueError("Database client required for data extraction")
        
        try:
            # Query properties with floor plan measurements
            query = """
                SELECT 
                    p.id as property_id,
                    p.extracted_data,
                    fpm.total_square_feet,
                    fpm.quality_score,
                    fpm.total_square_feet_confidence,
                    fpm.rooms,
                    fpm.detected_features
                FROM properties p
                LEFT JOIN floor_plan_measurements fpm ON p.id = fpm.property_id
                WHERE p.status IN ('complete', 'enrichment_complete')
            """
            
            result = self.db.rpc('execute_sql', {'query': query}).execute()
            rows = result.data or []
            # Unwrap RPC jsonb column (execute_sql/to_jsonb)
            unwrapped = []
            for r in rows:
                if isinstance(r, dict):
                    payload = r.get('execute_sql') or r.get('to_jsonb') or r
                else:
                    payload = r
                unwrapped.append(payload)

            logger.info(f"Found {len(unwrapped)} candidate properties")

            # Convert to PropertyFeatures objects
            features_list = []
            for row in unwrapped:
                features = self._parse_property_row(row)
                if features:
                    features_list.append(features)

            if len(features_list) < min_properties:
                logger.warning(f"Insufficient data after parsing: {len(features_list)} features, need {min_properties}")
                return []

            logger.info(f"Extracted features for {len(features_list)} properties")
            return features_list
        
        except Exception as e:
            logger.error(f"Error extracting property features: {e}")
            return []
    
    def _parse_property_row(self, row: Dict) -> Optional[PropertyFeatures]:
        """Parse database row into PropertyFeatures object"""
        try:
            extracted_data = row.get('extracted_data', {}) or {}
            rooms = row.get('rooms', []) or []
            detected_features = row.get('detected_features', {}) or {}
            
            # Basic features
            bedrooms = extracted_data.get('bedrooms', 0)
            bathrooms = extracted_data.get('bathrooms', 0.0)
            # total_sqft: fallback to extracted_data.square_footage/square_feet if FPM missing
            total_sqft = row.get('total_square_feet')
            if not total_sqft:
                # Coerce string numbers like "1,234"
                import re as _re
                def _to_int(v):
                    if v is None:
                        return 0
                    if isinstance(v, (int, float)):
                        return int(v)
                    if isinstance(v, str):
                        s = _re.sub(r'[^0-9]', '', v)
                        return int(s) if s else 0
                    return 0
                total_sqft = _to_int(extracted_data.get('total_square_feet'))
                if not total_sqft:
                    total_sqft = _to_int(extracted_data.get('square_footage'))
                if not total_sqft:
                    total_sqft = _to_int(extracted_data.get('square_feet'))
            if not total_sqft or total_sqft <= 0:
                return None
            
            # Room statistics
            room_sqfts = [r.get('sqft', 0) for r in rooms if isinstance(r, dict) and r.get('sqft')]
            room_count = len(room_sqfts)
            avg_room_sqft = sum(room_sqfts) / room_count if room_count > 0 else 0.0
            largest_room_sqft = max(room_sqfts) if room_sqfts else 0
            smallest_room_sqft = min(room_sqfts) if room_sqfts else 0
            
            # Amenities from detected features
            totals = detected_features.get('totals', {}) if isinstance(detected_features, dict) else {}
            num_doors = totals.get('doors', 0)
            num_windows = totals.get('windows', 0)
            closets = totals.get('closets', 0)
            
            # Check for specific amenities in rooms
            room_list = extracted_data.get('rooms', []) or []
            has_garage = any('garage' in str(r.get('type', '')).lower() for r in room_list if isinstance(r, dict))
            has_fireplace = any('fireplace' in str(r.get('features', [])) for r in room_list if isinstance(r, dict))
            has_balcony = any('balcony' in str(r.get('features', [])) for r in room_list if isinstance(r, dict))
            
            # Price data (from comparables if available)
            sale_price = None
            comparables = row.get('comparables', []) or []
            # Also check properties JSON path: extracted_data.market_insights.comparable_properties
            if not comparables:
                mi = (extracted_data.get('market_insights') or {}) if isinstance(extracted_data, dict) else {}
                comparables = (mi.get('comparable_properties') or []) if isinstance(mi, dict) else []
            if comparables and len(comparables) > 0:
                # Use median of comparable prices as proxy
                comp_prices = []
                for c in comparables:
                    if not isinstance(c, dict):
                        continue
                    val = c.get('sale_price')
                    if val is None:
                        val = c.get('last_sale_price')
                    if val is None:
                        val = c.get('price')
                    # Coerce numbers if strings with $/commas
                    try:
                        if isinstance(val, str):
                            import re as _re
                            s = _re.sub(r'[^0-9\.-]', '', val)
                            if s:
                                val = float(s)
                        if isinstance(val, (int, float)) and val > 0:
                            comp_prices.append(float(val))
                    except Exception:
                        continue
                if comp_prices:
                    sale_price = float(np.median(comp_prices))
            # As last resort, use price estimate from extracted data
            if sale_price is None:
                try:
                    pe = ((extracted_data.get('market_insights') or {}).get('price_estimate') or {})
                    ev = pe.get('estimated_value')
                    if isinstance(ev, str):
                        import re as _re
                        s = _re.sub(r'[^0-9\.-]', '', ev)
                        ev = float(s) if s else None
                    if isinstance(ev, (int, float)) and ev > 0:
                        sale_price = float(ev)
                except Exception:
                    pass
            
            # Create PropertyFeatures object
            features = PropertyFeatures(
                property_id=row['property_id'],
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                total_sqft=total_sqft,
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
                sale_price=sale_price,
                quality_score=row.get('quality_score', 0),
                confidence=row.get('total_square_feet_confidence', 0.0) or 0.0
            )
            
            return features
        
        except Exception as e:
            logger.error(f"Error parsing property row: {e}")
            return None
    
    # ========================================================================
    # STEP 2: BUILD ROOM DIMENSION REGRESSION MODEL
    # ========================================================================
    
    def build_room_dimension_model(
        self,
        features_list: List[PropertyFeatures],
        model_type: str = 'ridge'
    ) -> Optional[RegressionResults]:
        """
        Build regression model based on room dimensions
        
        Args:
            features_list: List of property features
            model_type: 'linear', 'ridge', or 'random_forest'
            
        Returns:
            RegressionResults object with model performance
        """
        logger.info(f"Building {model_type} regression model for room dimensions...")
        
        if len(features_list) < 5:
            logger.error(f"Insufficient data: {len(features_list)} properties, need at least 5")
            return None
        
        # Filter properties with sale prices
        data_with_prices = [f for f in features_list if f.sale_price is not None and f.sale_price > 0]
        
        if len(data_with_prices) < 3:
            logger.warning(f"Insufficient price data: {len(data_with_prices)} properties with prices")
            return None
        
        logger.info(f"Training on {len(data_with_prices)} properties with price data")
        
        # Prepare feature matrix
        X, y, feature_names = self._prepare_feature_matrix(data_with_prices)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        model = self.models[model_type]
        model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Cross-validation scores
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=min(5, len(X_train)), scoring='r2')
        
        # Feature importance
        feature_importance = self._get_feature_importance(model, feature_names)
        
        # Coefficients (for linear models)
        coefficients = {}
        if hasattr(model, 'coef_'):
            coefficients = dict(zip(feature_names, model.coef_))
        
        intercept = model.intercept_ if hasattr(model, 'intercept_') else 0.0
        
        # Store trained model
        self.trained_model = model
        self.trained_model_type = model_type
        self.feature_names = feature_names
        
        logger.info(f"Model trained: R²={r2:.3f}, MAE=${mae:,.0f}, RMSE=${rmse:,.0f}")
        
        # Generate predictions for all properties
        predictions = {}
        for prop in data_with_prices:
            try:
                pred_price = self.predict_price(prop)
                if pred_price:
                    predictions[prop.property_id] = pred_price
            except:
                pass
        
        results = RegressionResults(
            model_type=model_type,
            r2_score=r2,
            mae=mae,
            rmse=rmse,
            cross_val_scores=cv_scores.tolist(),
            feature_importance=feature_importance,
            predictions=predictions,
            coefficients=coefficients,
            intercept=intercept
        )
        
        return results
    
    def _prepare_feature_matrix(
        self,
        features_list: List[PropertyFeatures]
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare feature matrix X and target vector y"""
        
        feature_names = [
            'total_sqft',
            'bedrooms',
            'bathrooms',
            'room_count',
            'avg_room_sqft',
            'largest_room_sqft',
            'has_garage',
            'has_fireplace',
            'has_balcony',
            'has_closets',
            'num_doors',
            'num_windows'
        ]
        
        X = []
        y = []
        
        for prop in features_list:
            features = [
                prop.total_sqft,
                prop.bedrooms,
                prop.bathrooms,
                prop.room_count,
                prop.avg_room_sqft,
                prop.largest_room_sqft,
                prop.has_garage,
                prop.has_fireplace,
                prop.has_balcony,
                prop.has_closets,
                prop.num_doors,
                prop.num_windows
            ]
            X.append(features)
            y.append(prop.sale_price)
        
        return np.array(X), np.array(y), feature_names
    
    def _get_feature_importance(
        self,
        model,
        feature_names: List[str]
    ) -> Dict[str, float]:
        """Extract feature importance from model"""
        
        if hasattr(model, 'feature_importances_'):
            # Random Forest
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            # Linear models - use absolute coefficients
            importances = np.abs(model.coef_)
        else:
            return {}
        
        # Normalize to sum to 1
        importances = importances / importances.sum()
        
        return dict(zip(feature_names, importances))
    
    # ========================================================================
    # STEP 3: PRICE PREDICTION
    # ========================================================================
    
    def predict_price(self, features: PropertyFeatures) -> Optional[float]:
        """
        Predict property price based on features
        
        Args:
            features: PropertyFeatures object
            
        Returns:
            Predicted price or None
        """
        if not self.trained_model:
            logger.error("Model not trained. Call build_room_dimension_model() first")
            return None
        
        try:
            # Prepare feature vector
            feature_vector = np.array([[
                features.total_sqft,
                features.bedrooms,
                features.bathrooms,
                features.room_count,
                features.avg_room_sqft,
                features.largest_room_sqft,
                features.has_garage,
                features.has_fireplace,
                features.has_balcony,
                features.has_closets,
                features.num_doors,
                features.num_windows
            ]])
            
            # Scale features
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Predict
            predicted_price = self.trained_model.predict(feature_vector_scaled)[0]
            
            return max(0, predicted_price)  # Ensure non-negative
        
        except Exception as e:
            logger.error(f"Error predicting price: {e}")
            return None
    
    # ========================================================================
    # STEP 4: IMPACT CALCULATIONS
    # ========================================================================
    
    def calculate_sqft_impact(self) -> Optional[float]:
        """
        Calculate price impact per square foot
        "Each 1ft adds $X/sqft"
        
        Returns:
            Price per additional square foot
        """
        if not self.trained_model or 'total_sqft' not in self.feature_names:
            return None
        
        try:
            if hasattr(self.trained_model, 'coef_'):
                sqft_idx = self.feature_names.index('total_sqft')
                sqft_coefficient = self.trained_model.coef_[sqft_idx]
                
                # Account for scaling
                scaler_std = self.scaler.scale_[sqft_idx] if hasattr(self.scaler, 'scale_') else 1.0
                
                price_per_sqft = sqft_coefficient / scaler_std
                
                logger.info(f"Each additional sqft adds ${price_per_sqft:.2f} to property value")
                return price_per_sqft
            
            return None
        
        except Exception as e:
            logger.error(f"Error calculating sqft impact: {e}")
            return None
    
    # ========================================================================
    # STEP 5: PROPERTY COMPARISON
    # ========================================================================
    
    def compare_properties(
        self,
        property_a: PropertyFeatures,
        property_b: PropertyFeatures
    ) -> ComparisonResult:
        """
        Compare two properties and calculate price differences
        Example: 3BR/2BA vs 3BR/1.5BA
        
        Args:
            property_a: First property features
            property_b: Second property features
            
        Returns:
            ComparisonResult with detailed breakdown
        """
        logger.info(f"Comparing {property_a.property_id} vs {property_b.property_id}")
        
        # Calculate differences
        bedroom_diff = property_a.bedrooms - property_b.bedrooms
        bathroom_diff = property_a.bathrooms - property_b.bathrooms
        sqft_diff = property_a.total_sqft - property_b.total_sqft
        
        # Predict prices
        price_a = self.predict_price(property_a) or 0.0
        price_b = self.predict_price(property_b) or 0.0
        price_diff = price_a - price_b
        
        price_per_sqft_a = price_a / property_a.total_sqft if property_a.total_sqft > 0 else 0
        price_per_sqft_b = price_b / property_b.total_sqft if property_b.total_sqft > 0 else 0
        price_per_sqft_diff = price_per_sqft_a - price_per_sqft_b
        
        # Calculate impact breakdown
        sqft_impact = sqft_diff * (self.calculate_sqft_impact() or 0)
        
        # Estimate bedroom/bathroom impacts (simplified)
        bedroom_impact = bedroom_diff * 15000  # Rough estimate: $15k per bedroom
        bathroom_impact = bathroom_diff * 10000  # Rough estimate: $10k per bathroom
        
        # Amenity impact
        amenity_diff = (
            (property_a.has_garage - property_b.has_garage) * 20000 +
            (property_a.has_fireplace - property_b.has_fireplace) * 5000 +
            (property_a.has_balcony - property_b.has_balcony) * 3000
        )
        
        # Generate summary
        summary = self._generate_comparison_summary(
            property_a, property_b, bedroom_diff, bathroom_diff, sqft_diff, price_diff
        )
        
        recommendation = self._generate_recommendation(price_diff, price_per_sqft_diff)
        
        return ComparisonResult(
            property_a_id=property_a.property_id,
            property_b_id=property_b.property_id,
            bedroom_diff=bedroom_diff,
            bathroom_diff=bathroom_diff,
            sqft_diff=sqft_diff,
            predicted_price_diff=price_diff,
            price_per_sqft_diff=price_per_sqft_diff,
            sqft_impact=sqft_impact,
            bedroom_impact=bedroom_impact,
            bathroom_impact=bathroom_impact,
            amenity_impact=amenity_diff,
            comparison_summary=summary,
            recommendation=recommendation
        )
    
    def _generate_comparison_summary(
        self,
        prop_a: PropertyFeatures,
        prop_b: PropertyFeatures,
        bedroom_diff: int,
        bathroom_diff: float,
        sqft_diff: int,
        price_diff: float
    ) -> str:
        """Generate human-readable comparison summary"""
        
        summary_parts = []
        
        # Bedroom comparison
        if bedroom_diff != 0:
            summary_parts.append(
                f"{'more' if bedroom_diff > 0 else 'fewer'} bedroom{'s' if abs(bedroom_diff) > 1 else ''}"
            )
        
        # Bathroom comparison
        if bathroom_diff != 0:
            summary_parts.append(
                f"{'more' if bathroom_diff > 0 else 'fewer'} bathroom{'s' if abs(bathroom_diff) > 1 else ''}"
            )
        
        # Square footage
        if sqft_diff != 0:
            summary_parts.append(
                f"{abs(sqft_diff):,} {'more' if sqft_diff > 0 else 'fewer'} sqft"
            )
        
        if not summary_parts:
            return "Properties are similar in size and features"
        
        comparison = "Property A has " + ", ".join(summary_parts)
        price_impact = f"resulting in a ${abs(price_diff):,.0f} {'higher' if price_diff > 0 else 'lower'} estimated value"
        
        return f"{comparison}, {price_impact}."
    
    def _generate_recommendation(self, price_diff: float, price_per_sqft_diff: float) -> str:
        """Generate recommendation based on comparison"""
        
        if abs(price_diff) < 10000:
            return "Properties are similarly valued. Consider other factors like location and condition."
        
        if price_per_sqft_diff > 20:
            return "Property A offers better value per square foot. Recommended if budget allows."
        elif price_per_sqft_diff < -20:
            return "Property B offers better value per square foot. More cost-effective option."
        else:
            return "Both properties offer similar value per square foot. Decision should be based on specific needs."


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_comparison_report(comparison: ComparisonResult) -> str:
    """Format comparison result as readable report"""
    
    report = f"""
PROPERTY COMPARISON REPORT
{'='*70}

Differences:
- Bedrooms: {comparison.bedroom_diff:+d}
- Bathrooms: {comparison.bathroom_diff:+.1f}
- Square Footage: {comparison.sqft_diff:+,d} sqft

Price Impact Breakdown:
- Square Footage Impact: ${comparison.sqft_impact:+,.0f}
- Bedroom Impact: ${comparison.bedroom_impact:+,.0f}
- Bathroom Impact: ${comparison.bathroom_impact:+,.0f}
- Amenity Impact: ${comparison.amenity_impact:+,.0f}

Total Price Difference: ${comparison.predicted_price_diff:+,.0f}
Price per Sqft Difference: ${comparison.price_per_sqft_diff:+.2f}/sqft

Summary:
{comparison.comparison_summary}

Recommendation:
{comparison.recommendation}
"""
    
    return report
