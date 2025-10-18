"""
Floor Plan Parser with Dual OCR Strategy
Primary: Gemini Vision API
Fallback: Pytesseract OCR

Implements the technical plan's OCR strategy for robust text extraction
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image
import io

# Gemini Vision - Using LiteLLM for REST API ONLY (no gRPC)
from litellm import completion
import base64

# Pytesseract OCR (fallback)
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    logging.warning("pytesseract not installed. OCR fallback will not be available.")

logger = logging.getLogger(__name__)


# Dimension extraction prompt for Gemini
DIMENSION_EXTRACTION_PROMPT = """Analyze this floor plan image and extract ALL visible dimensions and measurements.

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


class FloorPlanParser:
    """
    Floor plan parser with dual OCR strategy:
    1. Primary: Gemini Vision (best for context understanding)
    2. Fallback: Pytesseract (good for pure text extraction)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize parser
        
        Args:
            api_key: Google Gemini API key (or from GOOGLE_GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GOOGLE_GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("Google Gemini API key required")
        
        # Set API key for LiteLLM
        os.environ['GEMINI_API_KEY'] = self.api_key

        # Configure pytesseract binary path if provided (macOS/Homebrew)
        if PYTESSERACT_AVAILABLE:
            try:
                import pytesseract as _pt
                tcmd = os.getenv('TESSERACT_CMD') or os.getenv('TESSERACT_PATH')
                if tcmd:
                    _pt.pytesseract.tesseract_cmd = tcmd
                    logger.info(f"Configured Tesseract command path: {tcmd}")
            except Exception:
                pass
        
        logger.info("Floor Plan Parser initialized (LiteLLM REST API + Pytesseract)")
    
    def parse_dimensions_from_image(
        self,
        image_bytes: bytes,
        use_fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Extract dimensions from floor plan image using dual OCR strategy
        
        Args:
            image_bytes: Floor plan image as bytes
            use_fallback: If True, use Pytesseract as fallback if Gemini fails
            
        Returns:
            Dict with extracted dimensions and metadata
        """
        logger.info("Parsing dimensions from floor plan image...")
        
        # Primary Method: Gemini Vision
        gemini_result = self._parse_with_gemini(image_bytes)
        
        if gemini_result and gemini_result.get('has_dimensions'):
            logger.info("✅ Gemini Vision successfully extracted dimensions")
            gemini_result['extraction_method'] = 'gemini_vision'
            
            # Validate with OCR if available
            if use_fallback and PYTESSERACT_AVAILABLE:
                ocr_validation = self._validate_with_ocr(image_bytes, gemini_result)
                gemini_result['ocr_validation'] = ocr_validation
            
            return gemini_result
        
        # Fallback Method: Pytesseract OCR
        if use_fallback and PYTESSERACT_AVAILABLE:
            logger.warning("Gemini failed or found no dimensions. Trying Pytesseract OCR fallback...")
            ocr_result = self._parse_with_ocr(image_bytes)
            
            if ocr_result and ocr_result.get('has_dimensions'):
                logger.info("✅ Pytesseract OCR found dimensions")
                ocr_result['extraction_method'] = 'pytesseract_ocr'
                return ocr_result
            else:
                logger.warning("⚠️ Pytesseract OCR also found no dimensions")
        
        # Both methods failed
        logger.warning("❌ No dimensions extracted by either method")
        return {
            'dimensions': [],
            'total_sqft': 0,
            'has_dimensions': False,
            'extraction_method': 'failed',
            'extraction_confidence': 0.0,
            'error': 'No dimensions found in floor plan'
        }
    
    def _parse_with_gemini(self, image_bytes: bytes) -> Optional[Dict[str, Any]]:
        """Parse dimensions using Gemini Vision via LiteLLM REST API"""
        try:
            # Prepare image as base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            image_url = f"data:image/jpeg;base64,{image_b64}"
            
            # Call Gemini via LiteLLM (REST API only, no gRPC)
            response = completion(
                model="gemini/gemini-2.5-flash",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": DIMENSION_EXTRACTION_PROMPT},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            result = json.loads(response.choices[0].message.content)
            
            # Validate structure
            if not isinstance(result, dict):
                logger.error("Gemini returned invalid structure")
                return None
            
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned invalid JSON: {e}")
            return None
        
        except Exception as e:
            logger.error(f"Gemini Vision parsing failed: {e}")
            return None
    
    def _parse_with_ocr(self, image_bytes: bytes) -> Dict[str, Any]:
        """Parse dimensions using Pytesseract OCR (fallback method)"""
        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Extract text with OCR
            ocr_text = pytesseract.image_to_string(image)
            
            logger.debug(f"OCR extracted text: {ocr_text[:200]}...")
            
            # Parse dimensions from OCR text using regex
            dimensions = self._extract_dimensions_from_text(ocr_text)
            
            # Calculate total sqft if possible
            total_sqft = self._calculate_total_sqft_from_text(ocr_text, dimensions)
            
            result = {
                'dimensions': dimensions,
                'total_sqft': total_sqft,
                'has_dimensions': len(dimensions) > 0 or total_sqft > 0,
                'extraction_confidence': 0.6 if dimensions else 0.3,
                'ocr_raw_text': ocr_text
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Pytesseract OCR parsing failed: {e}")
            err_str = str(e)
            tesseract_missing = 'TesseractNotFoundError' in err_str or 'tesseract is not installed' in err_str.lower()
            hint = None
            if tesseract_missing:
                hint = "Install Tesseract OCR (e.g., brew install tesseract) and ensure it is on PATH."
            return {
                'dimensions': [],
                'total_sqft': 0,
                'has_dimensions': False,
                'extraction_confidence': 0.0,
                'error': err_str,
                'tesseract_missing': tesseract_missing,
                'hint': hint
            }
    
    def _validate_with_ocr(
        self,
        image_bytes: bytes,
        gemini_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use OCR to validate Gemini's dimension extraction"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            ocr_text = pytesseract.image_to_string(image)
            
            logger.info(f"OCR validation - raw text: {ocr_text[:100]}...")
            
            # Extract dimensions from OCR
            ocr_dimensions = self._extract_dimensions_from_text(ocr_text)
            
            # Extract total square footage from OCR
            ocr_total_sqft = self._calculate_total_sqft_from_text(ocr_text, ocr_dimensions)
            
            # Compare with Gemini results
            gemini_count = len(gemini_result.get('dimensions', []))
            gemini_total_sqft = gemini_result.get('total_sqft', 0)
            ocr_count = len(ocr_dimensions)
            
            # Dimension count agreement
            dim_agreement = 'good' if abs(gemini_count - ocr_count) <= 2 else 'poor'
            
            # Total square footage agreement
            sqft_agreement = 'none'
            sqft_diff_pct = 0
            if gemini_total_sqft > 0 and ocr_total_sqft > 0:
                sqft_diff_pct = abs(gemini_total_sqft - ocr_total_sqft) / gemini_total_sqft
                if sqft_diff_pct < 0.05:
                    sqft_agreement = 'excellent'  # Within 5%
                elif sqft_diff_pct < 0.10:
                    sqft_agreement = 'good'  # Within 10%
                elif sqft_diff_pct < 0.20:
                    sqft_agreement = 'fair'  # Within 20%
                else:
                    sqft_agreement = 'poor'
            elif ocr_total_sqft > 0:
                sqft_agreement = 'ocr_only'
            elif gemini_total_sqft > 0:
                sqft_agreement = 'gemini_only'
            
            # Overall agreement
            if sqft_agreement in ['excellent', 'good']:
                overall_agreement = 'good'
            elif sqft_agreement == 'fair':
                overall_agreement = 'fair'
            else:
                overall_agreement = dim_agreement
            
            return {
                'ocr_found_dimensions': ocr_count,
                'gemini_found_dimensions': gemini_count,
                'dimension_agreement': dim_agreement,
                'ocr_total_sqft': ocr_total_sqft,
                'gemini_total_sqft': gemini_total_sqft,
                'sqft_agreement': sqft_agreement,
                'sqft_difference_pct': round(sqft_diff_pct * 100, 1),
                'overall_agreement': overall_agreement,
                'ocr_raw_text_sample': ocr_text[:200],
                'validation_note': self._get_validation_note(sqft_agreement, ocr_total_sqft, gemini_total_sqft)
            }
        
        except Exception as e:
            logger.error(f"OCR validation failed: {e}")
            return {'error': str(e)}
    
    def _get_validation_note(self, sqft_agreement: str, ocr_sqft: int, gemini_sqft: int) -> str:
        """Get a human-readable validation note"""
        if sqft_agreement == 'excellent':
            return f'✅ OCR validated total sqft: {ocr_sqft} ≈ {gemini_sqft} (excellent match)'
        elif sqft_agreement == 'good':
            return f'✅ OCR validated total sqft: {ocr_sqft} ≈ {gemini_sqft} (good match)'
        elif sqft_agreement == 'fair':
            return f'⚠️ OCR found {ocr_sqft} sqft vs Gemini {gemini_sqft} sqft (fair match)'
        elif sqft_agreement == 'poor':
            return f'❌ OCR found {ocr_sqft} sqft vs Gemini {gemini_sqft} sqft (poor match)'
        elif sqft_agreement == 'ocr_only':
            return f'ℹ️ OCR found {ocr_sqft} sqft, Gemini did not extract total'
        elif sqft_agreement == 'gemini_only':
            return f'ℹ️ Gemini found {gemini_sqft} sqft, OCR could not validate'
        else:
            return 'No square footage comparison available'
    
    def _extract_dimensions_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract dimension patterns from OCR text
        
        Patterns:
        - "14' x 12'" 
        - "14ft x 12ft"
        - "14 x 12"
        - "14'x12'"
        """
        dimensions = []
        
        # Regex patterns for dimensions
        patterns = [
            r"(\d+\.?\d*)\s*['\"]?\s*x\s*(\d+\.?\d*)\s*['\"]?",  # 14' x 12' or 14 x 12
            r"(\d+\.?\d*)\s*ft\s*x\s*(\d+\.?\d*)\s*ft",         # 14ft x 12ft
            r"(\d+\.?\d*)\s*'?\s*x\s*(\d+\.?\d*)\s*'?",         # 14'x12'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                length = float(match.group(1))
                width = float(match.group(2))
                
                # Sanity check (dimensions should be reasonable)
                if 1 <= length <= 100 and 1 <= width <= 100:
                    dimensions.append({
                        'length': length,
                        'width': width,
                        'sqft': int(length * width),
                        'unit': 'feet',
                        'raw_text': match.group(0)
                    })
        
        return dimensions
    
    def _calculate_total_sqft_from_text(
        self,
        text: str,
        dimensions: List[Dict[str, Any]]
    ) -> int:
        """Calculate total square footage from text or dimensions"""
        
        # Try to find explicit total sqft in text
        sqft_patterns = [
            r"(\d{3,5})\s*(?:sq\.?\s*ft\.?|sqft|SF|square feet)",  # Added SF
            r"total:?\s*(\d{3,5})",
        ]
        
        for pattern in sqft_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                sqft = int(match.group(1))
                if 100 <= sqft <= 50000:  # Reasonable range
                    return sqft
        
        # Calculate from dimensions if available
        if dimensions:
            total = sum(d.get('sqft', 0) for d in dimensions)
            if total > 0:
                return total
        
        return 0


# Convenience function
def parse_floor_plan_dimensions(
    image_bytes: bytes,
    use_fallback: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to parse floor plan dimensions
    
    Args:
        image_bytes: Floor plan image bytes
        use_fallback: Use OCR fallback if Gemini fails
        
    Returns:
        Parsed dimensions and metadata
    """
    parser = FloorPlanParser()
    return parser.parse_dimensions_from_image(image_bytes, use_fallback)


# Example usage
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python parser.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    print("=" * 70)
    print("FLOOR PLAN DIMENSION PARSER (Dual OCR Strategy)")
    print("=" * 70)
    print()
    
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    result = parse_floor_plan_dimensions(image_bytes)
    
    print(f"Extraction Method: {result.get('extraction_method', 'unknown')}")
    print(f"Has Dimensions: {result.get('has_dimensions', False)}")
    print(f"Confidence: {result.get('extraction_confidence', 0.0):.2%}")
    print()
    
    if result.get('dimensions'):
        print("Dimensions Found:")
        for dim in result['dimensions']:
            room = dim.get('room', 'Unknown')
            length = dim.get('length', 0)
            width = dim.get('width', 0)
            sqft = dim.get('sqft', 0)
            raw = dim.get('raw_text', '')
            print(f"  - {room}: {length}' x {width}' = {sqft} sqft ('{raw}')")
    
    if result.get('total_sqft'):
        print(f"\nTotal Square Footage: {result['total_sqft']:,}")
    
    if result.get('ocr_validation'):
        print("\nOCR Validation:")
        val = result['ocr_validation']
        print(f"  Gemini found: {val.get('gemini_found_dimensions', 0)} dimensions")
        print(f"  OCR found: {val.get('ocr_found_dimensions', 0)} dimensions")
        print(f"  Agreement: {val.get('agreement', 'unknown')}")
    
    print()
    print("=" * 70)
