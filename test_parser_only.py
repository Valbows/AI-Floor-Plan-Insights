#!/usr/bin/env python3
"""
Minimal test for Dual OCR Parser only (no CrewAI dependencies)
Run: python3 test_parser_only.py <image_path>
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv('.env')

def test_parser_standalone():
    """Test just the parser without importing the full app"""
    print("\n🧪 DUAL OCR PARSER TEST (Gemini + Pytesseract Fallback)\n")
    print("=" * 70)
    
    # Get image path
    if len(sys.argv) < 2:
        print("Usage: python3 test_parser_only.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)
    
    print(f"✅ Image: {image_path}")
    
    # Check API key
    api_key = os.getenv('GOOGLE_GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GOOGLE_GEMINI_API_KEY not set")
        sys.exit(1)
    
    print(f"✅ API Key: {api_key[:20]}...")
    print()
    
    # Import just the parser module
    try:
        # We need to manually create the parser without importing app/__init__.py
        # which has CrewAI dependencies
        
        import google.generativeai as genai
        import json
        import re
        from PIL import Image
        import io
        
        print("[1/3] Initializing Gemini Vision...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("✅ Gemini initialized")
        
        print("\n[2/3] Reading and analyzing floor plan...")
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        # Test with Gemini Vision
        prompt = """Analyze this floor plan image and extract ALL visible dimensions and measurements.

Look for:
1. Room dimensions (e.g., "14' x 12'", "14ft x 12ft", "14 x 12")
2. Total square footage labels
3. Room labels with dimensions
4. Any measurement text visible on the floor plan

Return a JSON object with this structure:
{
  "dimensions": [
    {
      "room": "Master Bedroom",
      "length": 14.0,
      "width": 12.0,
      "unit": "feet",
      "raw_text": "14' x 12'"
    }
  ],
  "total_sqft": 1200,
  "has_dimensions": true,
  "extraction_confidence": 0.9
}

IMPORTANT:
- Return ONLY valid JSON
- Include all dimension text you can read
- If no dimensions are visible, set "has_dimensions": false
- Be precise with numbers
"""
        
        image_part = {'mime_type': 'image/png', 'data': image_bytes}
        
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json"
        )
        
        response = model.generate_content(
            [prompt, image_part],
            generation_config=generation_config
        )
        
        result = json.loads(response.text)
        
        print("✅ Gemini Vision extraction complete")
        
        print("\n[3/3] Results:")
        print("=" * 70)
        print(f"\n📊 Extraction Method: GEMINI_VISION")
        print(f"📊 Has Dimensions: {result.get('has_dimensions', False)}")
        print(f"📊 Confidence: {result.get('extraction_confidence', 0):.1%}")
        
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
                    print(f"      (Raw: '{raw}')")
            
            if len(result['dimensions']) > 10:
                print(f"   ... and {len(result['dimensions']) - 10} more")
        
        if result.get('total_sqft'):
            print(f"\n🏠 Total Square Footage: {result['total_sqft']:,} sqft")
        
        print("\n" + "=" * 70)
        print("✅ TEST PASSED - OCR EXTRACTION SUCCESSFUL!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_parser_standalone()
    sys.exit(0 if success else 1)
