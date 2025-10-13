"""
Enhanced Floor Plan Analyst Agent - Phase 2
Integrates basic extraction (Agent #1) with detailed measurements (Phase 1 service)

Features:
- Basic property data extraction (bedrooms, bathrooms, sqft)
- Room-by-room measurement estimation
- Quality scoring and confidence metrics
- Feature detection (windows, doors, closets)
- Unified output format for database storage
"""

import os
import base64
import json
from typing import Dict, Any, Optional
from dataclasses import asdict
import logging

# Original Agent #1
from app.agents.floor_plan_analyst import FloorPlanAnalyst, FloorPlanData

# Phase 1 measurement estimator
from app.services.floor_plan_measurements import (
    FloorPlanMeasurementEstimator,
    FloorPlanMeasurements
)

logger = logging.getLogger(__name__)


class EnhancedFloorPlanAnalyst:
    """
    Enhanced Floor Plan Analyst combining:
    1. Basic extraction (bedrooms, bathrooms) - Agent #1
    2. Detailed measurements (room-by-room) - Phase 1 service
    
    Two-stage analysis:
    - Stage 1: Quick extraction of key metrics (Agent #1)
    - Stage 2: Detailed measurement estimation (AI measurement service)
    """
    
    def __init__(self):
        """Initialize both analyzers"""
        self.basic_analyst = FloorPlanAnalyst()
        self.measurement_estimator = FloorPlanMeasurementEstimator()
        
        logger.info("Enhanced Floor Plan Analyst initialized (Phase 2)")
    
    def analyze_floor_plan(
        self,
        image_path: str = None,
        image_url: str = None,
        image_bytes: bytes = None,
        include_measurements: bool = True
    ) -> Dict[str, Any]:
        """
        Complete floor plan analysis with optional detailed measurements
        
        Args:
            image_path: Local path to floor plan image
            image_url: URL to floor plan image
            image_bytes: Raw image bytes
            include_measurements: If True, includes room-by-room measurements
            
        Returns:
            Combined analysis results
        """
        logger.info("Starting enhanced floor plan analysis...")
        
        # Stage 1: Basic extraction (fast)
        logger.info("[Stage 1/2] Extracting basic property data...")
        if image_url:
            basic_data = self.basic_analyst.analyze_floor_plan(image_url=image_url)
        elif image_bytes:
            basic_data = self.basic_analyst.analyze_floor_plan(image_bytes=image_bytes)
        elif image_path:
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            basic_data = self.basic_analyst.analyze_floor_plan(image_bytes=image_bytes)
        else:
            raise ValueError("Must provide image_path, image_url, or image_bytes")
        
        logger.info(f"✅ Stage 1 complete: {basic_data['bedrooms']}BR, {basic_data['bathrooms']}BA, {basic_data['square_footage']} sqft")
        
        # Stage 2: Detailed measurements (if requested)
        measurements_data = None
        if include_measurements:
            logger.info("[Stage 2/2] Estimating room-by-room measurements...")
            
            # Use local file path if available, otherwise save bytes temporarily
            if not image_path:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    if image_bytes:
                        tmp.write(image_bytes)
                    elif image_url:
                        import requests
                        tmp.write(requests.get(image_url).content)
                    image_path = tmp.name
            
            try:
                measurements = self.measurement_estimator.estimate_measurements(
                    image_path=image_path,
                    property_type=basic_data.get('layout_type', 'Unknown'),
                    known_total_sqft=basic_data.get('square_footage')
                )
                
                # Convert to database format
                measurements_data = self.measurement_estimator.to_database_format(measurements)
                
                logger.info(f"✅ Stage 2 complete: {len(measurements.rooms)} rooms identified, quality: {measurements.quality.overall_score}/100")
            
            except Exception as e:
                logger.error(f"Stage 2 failed: {e}")
                measurements_data = None
        
        # Combine results
        result = {
            'basic_analysis': basic_data,
            'detailed_measurements': measurements_data,
            'analysis_complete': True,
            'stages_completed': 2 if measurements_data else 1
        }
        
        return result
    
    def analyze_with_validation(
        self,
        image_path: str = None,
        image_url: str = None,
        image_bytes: bytes = None
    ) -> Dict[str, Any]:
        """
        Analyze with cross-validation between basic and detailed measurements
        
        Compares basic sqft estimate with detailed room-by-room total
        to provide confidence scoring
        """
        result = self.analyze_floor_plan(
            image_path=image_path,
            image_url=image_url,
            image_bytes=image_bytes,
            include_measurements=True
        )
        
        # Cross-validate measurements
        basic = result['basic_analysis']
        detailed = result['detailed_measurements']
        
        if detailed and basic['square_footage'] > 0:
            basic_sqft = basic['square_footage']
            detailed_sqft = detailed['total_square_feet']
            
            # Calculate agreement
            if detailed_sqft > 0:
                difference_pct = abs(basic_sqft - detailed_sqft) / basic_sqft
                
                if difference_pct < 0.05:  # Within 5%
                    confidence = 'High'
                    confidence_score = 0.95
                elif difference_pct < 0.15:  # Within 15%
                    confidence = 'Medium'
                    confidence_score = 0.80
                else:
                    confidence = 'Low'
                    confidence_score = 0.60
                
                result['validation'] = {
                    'basic_sqft': basic_sqft,
                    'detailed_sqft': detailed_sqft,
                    'difference_pct': difference_pct,
                    'confidence': confidence,
                    'confidence_score': confidence_score,
                    'agreement': 'Good' if difference_pct < 0.10 else 'Fair' if difference_pct < 0.20 else 'Poor'
                }
                
                logger.info(f"Cross-validation: {confidence} confidence ({difference_pct:.1%} difference)")
        
        return result
    
    def get_database_ready_output(
        self,
        image_path: str = None,
        image_url: str = None,
        image_bytes: bytes = None
    ) -> Dict[str, Any]:
        """
        Get analysis results in database-ready format
        
        Returns data structured for insertion into:
        - properties.extracted_data (basic analysis)
        - floor_plan_measurements table (detailed measurements)
        """
        result = self.analyze_with_validation(
            image_path=image_path,
            image_url=image_url,
            image_bytes=image_bytes
        )
        
        # Structure for database
        db_output = {
            'properties_extracted_data': {
                'address': result['basic_analysis']['address'],
                'bedrooms': result['basic_analysis']['bedrooms'],
                'bathrooms': result['basic_analysis']['bathrooms'],
                'square_footage': result['basic_analysis']['square_footage'],
                'rooms': result['basic_analysis']['rooms'],
                'features': result['basic_analysis']['features'],
                'layout_type': result['basic_analysis']['layout_type'],
                'notes': result['basic_analysis']['notes']
            },
            'floor_plan_measurements': result['detailed_measurements'],
            'validation_metrics': result.get('validation')
        }
        
        return db_output


# Convenience function for backward compatibility
def analyze_floor_plan_enhanced(
    image_path: str = None,
    image_url: str = None,
    image_bytes: bytes = None,
    detailed: bool = True
) -> Dict[str, Any]:
    """
    Convenience function for enhanced floor plan analysis
    
    Args:
        image_path: Local path to image
        image_url: URL to image
        image_bytes: Raw image data
        detailed: Include detailed measurements (default: True)
        
    Returns:
        Complete analysis results
    """
    analyst = EnhancedFloorPlanAnalyst()
    return analyst.analyze_floor_plan(
        image_path=image_path,
        image_url=image_url,
        image_bytes=image_bytes,
        include_measurements=detailed
    )


# Example usage
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python floor_plan_analyst_enhanced.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    print("=" * 70)
    print("ENHANCED FLOOR PLAN ANALYSIS (Phase 2)")
    print("=" * 70)
    print()
    
    analyst = EnhancedFloorPlanAnalyst()
    result = analyst.analyze_with_validation(image_path=image_path)
    
    # Display results
    basic = result['basic_analysis']
    print("BASIC ANALYSIS (Agent #1):")
    print(f"  Bedrooms: {basic['bedrooms']}")
    print(f"  Bathrooms: {basic['bathrooms']}")
    print(f"  Square Footage: {basic['square_footage']:,}")
    print(f"  Layout: {basic['layout_type']}")
    print()
    
    if result['detailed_measurements']:
        detailed = result['detailed_measurements']
        print("DETAILED MEASUREMENTS (Phase 1 Service):")
        print(f"  Total: {detailed['total_square_feet']:,} sqft")
        print(f"  Confidence: {detailed['total_square_feet_confidence']:.2%}")
        print(f"  Quality Score: {detailed['quality_score']}/100")
        print(f"  Rooms Identified: {len(detailed['rooms'])}")
        print()
        
        print("ROOM BREAKDOWN:")
        for room in detailed['rooms']:
            print(f"  - {room['name']} ({room['type']}): {room['sqft']} sqft")
            if room['length_ft'] and room['width_ft']:
                print(f"    Dimensions: {room['length_ft']}' × {room['width_ft']}'")
        print()
    
    if 'validation' in result:
        val = result['validation']
        print("CROSS-VALIDATION:")
        print(f"  Basic sqft: {val['basic_sqft']:,}")
        print(f"  Detailed sqft: {val['detailed_sqft']:,}")
        print(f"  Difference: {val['difference_pct']:.1%}")
        print(f"  Confidence: {val['confidence']}")
        print(f"  Agreement: {val['agreement']}")
    
    print()
    print("=" * 70)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 70)
