"""
Test Script for Phase 2 Enhanced Floor Plan Analysis
Tests all three stages of enhanced analysis
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env from parent directory (root of project)
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded .env from: {env_path}\n")
else:
    print(f"⚠️ No .env file found at: {env_path}\n")

def test_enhanced_analysis():
    """Test the complete 3-stage enhanced analysis"""
    
    print("=" * 70)
    print("PHASE 2: ENHANCED FLOOR PLAN ANALYSIS TEST")
    print("=" * 70)
    print()
    
    # Check if test image exists
    test_image_path = input("Enter path to a floor plan image (or press Enter to skip): ").strip()
    
    if not test_image_path or not os.path.exists(test_image_path):
        print("⚠️ No valid image path provided.")
        print()
        print("To test with a real floor plan:")
        print("1. Download a sample floor plan image")
        print("2. Run: python test_phase2_enhanced_analysis.py")
        print("3. Provide the path when prompted")
        print()
        return
    
    try:
        from app.agents.floor_plan_analyst_enhanced import EnhancedFloorPlanAnalyst
        
        print(f"Testing with image: {test_image_path}")
        print()
        
        # Initialize analyst
        print("[1/4] Initializing Enhanced Floor Plan Analyst...")
        analyst = EnhancedFloorPlanAnalyst()
        print("✅ Analyst initialized")
        print()
        
        # Run basic analysis only
        print("[2/4] Testing Stage 1: Basic extraction...")
        basic_result = analyst.analyze_floor_plan(
            image_path=test_image_path,
            include_measurements=False,
            include_features=False
        )
        
        basic = basic_result['basic_analysis']
        print(f"✅ Stage 1 complete:")
        print(f"   Bedrooms: {basic['bedrooms']}")
        print(f"   Bathrooms: {basic['bathrooms']}")
        print(f"   Square Footage: {basic['square_footage']:,}")
        print(f"   Layout: {basic['layout_type']}")
        print()
        
        # Run with measurements
        print("[3/4] Testing Stage 2: Room-by-room measurements...")
        detailed_result = analyst.analyze_floor_plan(
            image_path=test_image_path,
            include_measurements=True,
            include_features=False
        )
        
        if detailed_result.get('detailed_measurements'):
            measurements = detailed_result['detailed_measurements']
            print(f"✅ Stage 2 complete:")
            print(f"   Total Sqft: {measurements['total_square_feet']:,}")
            print(f"   Confidence: {measurements['total_square_feet_confidence']:.2%}")
            print(f"   Quality Score: {measurements['quality_score']}/100")
            print(f"   Rooms Identified: {len(measurements['rooms'])}")
            print()
            
            if measurements['rooms']:
                print("   Room Breakdown:")
                for room in measurements['rooms'][:5]:  # Show first 5
                    print(f"     - {room['name']}: {room['sqft']} sqft (confidence: {room['confidence']:.2%})")
                if len(measurements['rooms']) > 5:
                    print(f"     ... and {len(measurements['rooms']) - 5} more rooms")
                print()
        else:
            print("⚠️ Stage 2 failed (measurements not generated)")
            print()
        
        # Run complete analysis with features
        print("[4/4] Testing Stage 3: Feature detection...")
        complete_result = analyst.analyze_with_validation(
            image_path=test_image_path
        )
        
        if complete_result.get('feature_detection'):
            features = complete_result['feature_detection']
            print(f"✅ Stage 3 complete:")
            print(f"   Total Doors: {features['totals']['doors']}")
            print(f"   Total Windows: {features['totals']['windows']}")
            print(f"   Total Closets: {features['totals']['closets']}")
            print(f"   Detection Confidence: {features['detection_confidence']:.2%}")
            print()
            
            if features['features_by_room']:
                print("   Features by Room:")
                for room, room_features in list(features['features_by_room'].items())[:3]:
                    print(f"     {room}:")
                    for feature in room_features:
                        print(f"       - {feature['quantity']}x {feature['description']} ({feature['type']})")
                if len(features['features_by_room']) > 3:
                    print(f"     ... and {len(features['features_by_room']) - 3} more rooms")
                print()
        else:
            print("⚠️ Stage 3 failed (feature detection not generated)")
            print()
        
        # Show validation
        if complete_result.get('validation'):
            val = complete_result['validation']
            print("Cross-Validation Results:")
            print(f"   Basic sqft: {val['basic_sqft']:,}")
            print(f"   Detailed sqft: {val['detailed_sqft']:,}")
            print(f"   Difference: {val['difference_pct']:.1%}")
            print(f"   Confidence: {val['confidence']}")
            print(f"   Agreement: {val['agreement']}")
            print()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print(f"   Stages Completed: {complete_result['stages_completed']}/3")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_individual_services():
    """Test each service independently"""
    
    print("=" * 70)
    print("TESTING INDIVIDUAL SERVICES")
    print("=" * 70)
    print()
    
    test_image_path = input("Enter path to a floor plan image (or press Enter to skip): ").strip()
    
    if not test_image_path or not os.path.exists(test_image_path):
        print("⚠️ No valid image path provided. Skipping individual service tests.")
        return
    
    # Test 0: Dual OCR Parser
    try:
        print("[Test 0/4] Dual OCR Parser (Gemini + Pytesseract)")
        from app.parsing.parser import FloorPlanParser
        
        parser = FloorPlanParser()
        
        with open(test_image_path, 'rb') as f:
            image_bytes = f.read()
        
        result = parser.parse_dimensions_from_image(image_bytes, use_fallback=True)
        
        print(f"✅ Dimensions parsed:")
        print(f"   Method: {result.get('extraction_method', 'unknown')}")
        print(f"   Has Dimensions: {result.get('has_dimensions', False)}")
        print(f"   Confidence: {result.get('extraction_confidence', 0.0):.2%}")
        print(f"   Dimensions Found: {len(result.get('dimensions', []))}")
        if result.get('total_sqft'):
            print(f"   Total Sqft: {result['total_sqft']:,}")
        if result.get('ocr_validation'):
            val = result['ocr_validation']
            print(f"   OCR Validation: {val.get('agreement', 'unknown')}")
        print()
        
    except Exception as e:
        print(f"❌ Dual OCR Parser failed: {e}")
        print()
    
    # Test 1: Measurement Estimator
    try:
        print("[Test 1/3] Floor Plan Measurement Estimator")
        from app.services.floor_plan_measurements import FloorPlanMeasurementEstimator
        
        estimator = FloorPlanMeasurementEstimator()
        measurements = estimator.estimate_measurements(
            image_path=test_image_path,
            known_total_sqft=1000
        )
        
        print(f"✅ Measurements: {measurements.total_square_feet} sqft")
        print(f"   Confidence: {measurements.total_square_feet_confidence:.2%}")
        print(f"   Quality: {measurements.quality.overall_score}/100")
        print(f"   Processing Time: {measurements.processing_time_seconds:.2f}s")
        print()
        
    except Exception as e:
        print(f"❌ Measurement estimator failed: {e}")
        print()
    
    # Test 2: Feature Detector
    try:
        print("[Test 2/4] Feature Detector")
        from app.services.feature_detection import FloorPlanFeatureDetector
        
        detector = FloorPlanFeatureDetector()
        features = detector.detect_features(image_path=test_image_path)
        
        print(f"✅ Features detected:")
        print(f"   Doors: {features.total_doors}")
        print(f"   Windows: {features.total_windows}")
        print(f"   Closets: {features.total_closets}")
        print(f"   Confidence: {features.detection_confidence:.2%}")
        print(f"   Processing Time: {features.processing_time_seconds:.2f}s")
        print()
        
    except Exception as e:
        print(f"❌ Feature detector failed: {e}")
        print()
    
    # Test 3: Basic Analyst
    try:
        print("[Test 3/4] Basic Floor Plan Analyst")
        from app.agents.floor_plan_analyst import FloorPlanAnalyst
        
        analyst = FloorPlanAnalyst()
        with open(test_image_path, 'rb') as f:
            result = analyst.analyze_floor_plan(image_bytes=f.read())
        
        print(f"✅ Basic analysis:")
        print(f"   Bedrooms: {result['bedrooms']}")
        print(f"   Bathrooms: {result['bathrooms']}")
        print(f"   Square Footage: {result['square_footage']:,}")
        print()
        
    except Exception as e:
        print(f"❌ Basic analyst failed: {e}")
        print()
    
    print("=" * 70)
    print("Individual service tests complete")
    print("=" * 70)


def check_environment():
    """Check if all required environment variables are set"""
    
    print("=" * 70)
    print("ENVIRONMENT CHECK")
    print("=" * 70)
    print()
    
    required_vars = [
        'GOOGLE_GEMINI_API_KEY',
        'GEMINI_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 20}")
        else:
            print(f"❌ {var}: Not set")
            missing.append(var)
    
    print()
    
    if missing:
        print("⚠️ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        print()
        print("Set these in your .env file or export them:")
        for var in missing:
            print(f"   export {var}='your-api-key-here'")
        print()
        return False
    
    print("✅ All required environment variables are set")
    print()
    return True


def main():
    """Main test runner"""
    
    print("\n")
    print("🧪 PHASE 2 ENHANCED FLOOR PLAN ANALYSIS TEST SUITE")
    print()
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please set required variables.")
        return
    
    print()
    
    # Menu
    print("Select test to run:")
    print("1. Complete Enhanced Analysis (Recommended)")
    print("2. Individual Service Tests")
    print("3. Both")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    print()
    
    if choice == '1':
        test_enhanced_analysis()
    elif choice == '2':
        test_individual_services()
    elif choice == '3':
        test_enhanced_analysis()
        print("\n")
        test_individual_services()
    else:
        print("Invalid choice. Running complete enhanced analysis...")
        test_enhanced_analysis()


if __name__ == '__main__':
    main()
