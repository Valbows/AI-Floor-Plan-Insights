"""Quick test of Phase 2 with uploaded floor plan"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded .env from: {env_path}")
else:
    print(f"⚠️ No .env file found at: {env_path}")
    # Fallback: set manually
    os.environ['GOOGLE_GEMINI_API_KEY'] = 'AIzaSyAcqKMX5XzqmPR-V6CG59bxXTXnKI4M7Js'
    os.environ['GEMINI_API_KEY'] = 'AIzaSyAcqKMX5XzqmPR-V6CG59bxXTXnKI4M7Js'

# Import test
print("\n🧪 QUICK PHASE 2 TEST\n")
print("=" * 70)

# Test 1: Dual OCR Parser
try:
    print("\n[Test 1/4] Dual OCR Parser (Gemini + Pytesseract OCR)")
    from app.parsing.parser import FloorPlanParser
    
    # Use the uploaded floor plan
    image_path = input("\nEnter path to floor plan image: ").strip()
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)
    
    parser = FloorPlanParser()
    
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    result = parser.parse_dimensions_from_image(image_bytes, use_fallback=True)
    
    print(f"\n✅ OCR Parser Results:")
    print(f"   Method: {result.get('extraction_method', 'unknown')}")
    print(f"   Has Dimensions: {result.get('has_dimensions', False)}")
    print(f"   Confidence: {result.get('extraction_confidence', 0.0):.2%}")
    print(f"   Dimensions Found: {len(result.get('dimensions', []))}")
    
    if result.get('dimensions'):
        print(f"\n   Sample Dimensions:")
        for dim in result['dimensions'][:3]:
            print(f"     - {dim.get('room', 'Room')}: {dim.get('length', 0)}' x {dim.get('width', 0)}' = {dim.get('sqft', 0)} sqft")
    
    if result.get('total_sqft'):
        print(f"\n   Total Sqft: {result['total_sqft']:,}")
    
    if result.get('ocr_validation'):
        val = result['ocr_validation']
        print(f"\n   OCR Validation:")
        print(f"     Agreement: {val.get('agreement', 'unknown')}")
        print(f"     Gemini found: {val.get('gemini_found_dimensions', 0)}")
        print(f"     OCR found: {val.get('ocr_found_dimensions', 0)}")

except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Test complete!")
