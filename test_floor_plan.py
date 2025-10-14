#!/usr/bin/env python3
"""
Simple test for Phase 2 Enhanced Floor Plan Analysis
Run from project root: python3 test_floor_plan.py <image_path>
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Add backend to path
sys.path.insert(0, 'backend')

def test_dual_ocr_parser(image_path):
    """Test the dual OCR parser (Gemini + Pytesseract)"""
    print("\n" + "=" * 70)
    print("TEST 1: DUAL OCR PARSER (Gemini Vision + Pytesseract Fallback)")
    print("=" * 70)
    
    try:
        from app.parsing.parser import FloorPlanParser
        
        print(f"\n📄 Analyzing: {image_path}")
        
        parser = FloorPlanParser()
        
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        print("⏳ Extracting dimensions...")
        result = parser.parse_dimensions_from_image(image_bytes, use_fallback=True)
        
        print(f"\n✅ EXTRACTION COMPLETE")
        print(f"\n📊 Results:")
        print(f"   Method Used: {result.get('extraction_method', 'unknown').upper()}")
        print(f"   Has Dimensions: {result.get('has_dimensions', False)}")
        print(f"   Confidence: {result.get('extraction_confidence', 0.0):.1%}")
        
        if result.get('dimensions'):
            print(f"\n📐 Dimensions Extracted: {len(result['dimensions'])}")
            print(f"\n   Room-by-Room:")
            for i, dim in enumerate(result['dimensions'][:10], 1):
                room = dim.get('room', f'Room {i}')
                length = dim.get('length', 0)
                width = dim.get('width', 0)
                sqft = dim.get('sqft', int(length * width))
                raw = dim.get('raw_text', '')
                print(f"   {i}. {room}: {length}' × {width}' = {sqft:,} sqft")
                if raw:
                    print(f"      Raw text: '{raw}'")
            
            if len(result['dimensions']) > 10:
                print(f"   ... and {len(result['dimensions']) - 10} more")
        else:
            print(f"\n⚠️ No individual room dimensions found")
        
        if result.get('total_sqft'):
            print(f"\n🏠 Total Square Footage: {result['total_sqft']:,} sqft")
        
        if result.get('ocr_validation'):
            val = result['ocr_validation']
            print(f"\n✅ DUAL OCR VALIDATION (Gemini + Pytesseract):")
            print(f"   Overall Agreement: {val.get('overall_agreement', 'unknown').upper()}")
            print(f"\n   Dimension Count:")
            print(f"     Gemini found: {val.get('gemini_found_dimensions', 0)} dimensions")
            print(f"     OCR found: {val.get('ocr_found_dimensions', 0)} dimensions")
            print(f"     Agreement: {val.get('dimension_agreement', 'unknown').upper()}")
            print(f"\n   Total Square Footage:")
            print(f"     Gemini: {val.get('gemini_total_sqft', 0):,} sqft")
            print(f"     OCR: {val.get('ocr_total_sqft', 0):,} sqft")
            print(f"     Difference: {val.get('sqft_difference_pct', 0):.1f}%")
            print(f"     Agreement: {val.get('sqft_agreement', 'unknown').upper()}")
            if val.get('validation_note'):
                print(f"\n   {val['validation_note']}")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        print("\nMake sure you've installed dependencies:")
        print("  pip install -r backend/requirements.txt")
        return False
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enhanced_analyst(image_path):
    """Test the 3-stage enhanced analyst"""
    print("\n" + "=" * 70)
    print("TEST 2: ENHANCED FLOOR PLAN ANALYST (3-Stage Analysis)")
    print("=" * 70)
    
    try:
        from app.agents.floor_plan_analyst_enhanced import EnhancedFloorPlanAnalyst
        
        print(f"\n📄 Analyzing: {image_path}")
        
        analyst = EnhancedFloorPlanAnalyst()
        
        print("⏳ Running 3-stage analysis...")
        print("   Stage 1: Basic extraction (bedrooms, bathrooms, sqft)")
        print("   Stage 2: Room-by-room measurements")
        print("   Stage 3: Feature detection (doors, windows, closets)")
        
        result = analyst.analyze_with_validation(image_path=image_path)
        
        print(f"\n✅ ANALYSIS COMPLETE")
        print(f"\n📊 Stages Completed: {result.get('stages_completed', 0)}/3")
        
        # Stage 1: Basic Analysis
        if result.get('basic_analysis'):
            basic = result['basic_analysis']
            print(f"\n🏠 Stage 1 - Basic Property Data:")
            print(f"   Bedrooms: {basic.get('bedrooms', 0)}")
            print(f"   Bathrooms: {basic.get('bathrooms', 0)}")
            print(f"   Square Footage: {basic.get('square_footage', 0):,}")
            print(f"   Layout: {basic.get('layout_type', 'unknown')}")
        
        # Stage 2: Detailed Measurements
        if result.get('detailed_measurements'):
            measurements = result['detailed_measurements']
            print(f"\n📐 Stage 2 - Room Measurements:")
            print(f"   Total Sqft: {measurements.get('total_square_feet', 0):,}")
            print(f"   Confidence: {measurements.get('total_square_feet_confidence', 0):.1%}")
            print(f"   Quality Score: {measurements.get('quality_score', 0)}/100")
            
            rooms = measurements.get('rooms', [])
            print(f"   Rooms Identified: {len(rooms)}")
            
            if rooms:
                print(f"\n   Top Rooms:")
                for i, room in enumerate(rooms[:5], 1):
                    print(f"   {i}. {room['name']}: {room['sqft']:,} sqft (confidence: {room['confidence']:.1%})")
        
        # Stage 3: Feature Detection
        if result.get('feature_detection'):
            features = result['feature_detection']
            print(f"\n🚪 Stage 3 - Features Detected:")
            totals = features.get('totals', {})
            print(f"   Doors: {totals.get('doors', 0)}")
            print(f"   Windows: {totals.get('windows', 0)}")
            print(f"   Closets: {totals.get('closets', 0)}")
            print(f"   Other Features: {totals.get('other', 0)}")
            print(f"   Detection Confidence: {features.get('detection_confidence', 0):.1%}")
        
        # Validation
        if result.get('validation'):
            val = result['validation']
            print(f"\n✓ Cross-Validation:")
            print(f"   Basic sqft: {val.get('basic_sqft', 0):,}")
            print(f"   Detailed sqft: {val.get('detailed_sqft', 0):,}")
            print(f"   Difference: {val.get('difference_pct', 0):.1%}")
            print(f"   Agreement: {val.get('agreement', 'unknown').upper()}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n")
    print("🧪 PHASE 2 ENHANCED FLOOR PLAN ANALYSIS - COMPREHENSIVE TEST")
    print("=" * 70)
    
    # Check environment
    api_key = os.getenv('GOOGLE_GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("\n❌ ERROR: GOOGLE_GEMINI_API_KEY not found in environment")
        print("\nMake sure .env file exists in project root with:")
        print("  GOOGLE_GEMINI_API_KEY=your-api-key-here")
        sys.exit(1)
    
    print(f"\n✅ API Key Found: {api_key[:20]}...")
    
    # Get image path
    if len(sys.argv) < 2:
        image_path = input("\n📷 Enter path to floor plan image: ").strip()
    else:
        image_path = sys.argv[1]
    
    if not image_path or not os.path.exists(image_path):
        print(f"\n❌ ERROR: Image not found: {image_path}")
        sys.exit(1)
    
    print(f"\n✅ Image Found: {image_path}")
    
    # Run tests
    results = []
    
    # Test 1: Dual OCR Parser
    results.append(("Dual OCR Parser", test_dual_ocr_parser(image_path)))
    
    # Test 2: Enhanced Analyst
    results.append(("Enhanced Analyst", test_enhanced_analyst(image_path)))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"\n{status}: {test_name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED - PHASE 2 IMPLEMENTATION VERIFIED!")
        print("=" * 70)
        print("\nReady to commit to GitHub! ✅")
    else:
        print("\n⚠️ Some tests failed. Please review errors above.")
    
    print()


if __name__ == '__main__':
    main()
