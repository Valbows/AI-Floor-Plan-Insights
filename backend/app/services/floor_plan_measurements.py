"""
Floor Plan Measurement Estimation Service
Uses AI (Gemini Vision) to extract detailed room measurements from floor plans

Features:
- Room-by-room dimension estimation
- Total square footage calculation
- Feature detection (windows, doors, closets)
- Quality scoring and confidence metrics
- Support for labeled and unlabeled floor plans
"""

import os
import base64
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)


@dataclass
class RoomMeasurement:
    """Individual room measurement"""
    type: str  # bedroom, living_room, kitchen, bathroom, etc.
    name: str
    length_ft: Optional[float]
    width_ft: Optional[float]
    sqft: Optional[int]
    features: List[str]  # windows, closet, door, etc.
    confidence: float  # 0-1


@dataclass
class FloorPlanQuality:
    """Quality assessment of floor plan"""
    clarity: int  # 0-100 (image clarity)
    completeness: int  # 0-100 (how complete the plan is)
    label_quality: int  # 0-100 (quality of dimension labels if present)
    scale_accuracy: int  # 0-100 (accuracy of scale estimation)
    overall_score: int  # 0-100 (weighted average)


@dataclass
class FloorPlanMeasurements:
    """Complete floor plan measurements"""
    total_square_feet: int
    total_square_feet_confidence: float
    measurement_method: str  # 'ai_estimation', 'labeled_dimensions', 'hybrid'
    rooms: List[RoomMeasurement]
    quality: FloorPlanQuality
    detected_features: List[str]
    processing_time_seconds: float


class FloorPlanMeasurementEstimator:
    """
    AI-powered floor plan measurement estimator using Gemini Vision
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the estimator
        
        Args:
            api_key: Google Gemini API key (or from GOOGLE_GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GOOGLE_GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("Google Gemini API key required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        logger.info("Floor Plan Measurement Estimator initialized")
    
    def estimate_measurements(
        self,
        image_path: str,
        property_type: Optional[str] = None,
        known_total_sqft: Optional[int] = None
    ) -> FloorPlanMeasurements:
        """
        Estimate measurements from a floor plan image
        
        Args:
            image_path: Path to floor plan image
            property_type: Type of property (helps with context)
            known_total_sqft: Known total square footage (if available, for calibration)
            
        Returns:
            FloorPlanMeasurements object with detailed measurements
        """
        import time
        start_time = time.time()
        
        logger.info(f"Analyzing floor plan: {image_path}")
        
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Build prompt
        prompt = self._build_measurement_prompt(property_type, known_total_sqft)
        
        # Analyze with Gemini Vision
        try:
            response = self.model.generate_content([
                prompt,
                {'mime_type': 'image/png', 'data': image_data}
            ])
            
            result_text = response.text
            logger.debug(f"Gemini response: {result_text[:500]}...")
            
            # Parse response
            measurements = self._parse_response(result_text, known_total_sqft)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            measurements.processing_time_seconds = processing_time
            
            logger.info(f"Analysis complete in {processing_time:.2f}s - Total: {measurements.total_square_feet} sqft")
            
            return measurements
        
        except Exception as e:
            logger.error(f"Failed to analyze floor plan: {e}")
            raise
    
    def _build_measurement_prompt(
        self,
        property_type: Optional[str],
        known_total_sqft: Optional[int]
    ) -> str:
        """Build the AI prompt for measurement estimation"""
        
        prompt = """You are an expert floor plan analyst. Analyze this floor plan image and provide detailed measurements.

TASK:
1. Identify all rooms and spaces
2. Estimate dimensions for each room (length × width in feet)
3. Calculate square footage for each room
4. Detect features (windows, doors, closets, stairs, etc.)
5. Assess the quality of the floor plan image

INSTRUCTIONS:
- If the floor plan has dimension labels, use those exactly
- If no labels, estimate based on typical room sizes and proportions
- Be conservative with estimates - better to underestimate than overestimate
- Look for scale bars or legends that indicate scale
- Consider typical room sizes (e.g., master bedroom: 12x14, living room: 16x18)

"""
        
        if property_type:
            prompt += f"\nPROPERTY TYPE: {property_type}\n"
        
        if known_total_sqft:
            prompt += f"\nKNOWN TOTAL SQFT: {known_total_sqft} (use this to calibrate your estimates)\n"
        
        prompt += """
OUTPUT FORMAT (valid JSON only):
{
  "rooms": [
    {
      "type": "bedroom",
      "name": "Master Bedroom",
      "length_ft": 12.0,
      "width_ft": 14.0,
      "sqft": 168,
      "features": ["closet", "window"],
      "confidence": 0.85
    }
  ],
  "total_square_feet": 1200,
  "measurement_method": "labeled_dimensions|ai_estimation|hybrid",
  "detected_features": ["windows", "doors", "closets", "stairs"],
  "quality_assessment": {
    "clarity": 85,
    "completeness": 90,
    "label_quality": 75,
    "scale_accuracy": 80
  }
}

IMPORTANT: 
- Return ONLY valid JSON, no markdown, no explanations
- confidence: 0.0-1.0 (how confident you are in that room's measurements)
- All measurements in feet and square feet
- Be thorough but realistic
"""
        
        return prompt
    
    def _parse_response(
        self,
        response_text: str,
        known_total_sqft: Optional[int]
    ) -> FloorPlanMeasurements:
        """Parse Gemini's response into structured measurements"""
        
        # Extract JSON from response (handle markdown code blocks)
        json_text = response_text.strip()
        if json_text.startswith('```json'):
            json_text = json_text.split('```json')[1].split('```')[0].strip()
        elif json_text.startswith('```'):
            json_text = json_text.split('```')[1].split('```')[0].strip()
        
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            raise ValueError(f"Invalid JSON response from AI: {e}")
        
        # Parse rooms
        rooms = []
        for room_data in data.get('rooms', []):
            room = RoomMeasurement(
                type=room_data.get('type', 'unknown'),
                name=room_data.get('name', 'Unknown Room'),
                length_ft=room_data.get('length_ft'),
                width_ft=room_data.get('width_ft'),
                sqft=room_data.get('sqft'),
                features=room_data.get('features', []),
                confidence=room_data.get('confidence', 0.5)
            )
            rooms.append(room)
        
        # Parse quality assessment
        quality_data = data.get('quality_assessment', {})
        quality = FloorPlanQuality(
            clarity=quality_data.get('clarity', 50),
            completeness=quality_data.get('completeness', 50),
            label_quality=quality_data.get('label_quality', 50),
            scale_accuracy=quality_data.get('scale_accuracy', 50),
            overall_score=0  # Calculate below
        )
        
        # Calculate overall quality score (weighted average)
        quality.overall_score = int(
            quality.clarity * 0.25 +
            quality.completeness * 0.30 +
            quality.label_quality * 0.25 +
            quality.scale_accuracy * 0.20
        )
        
        # Get total square feet
        total_sqft = data.get('total_square_feet', 0)
        
        # Calculate confidence
        # Higher confidence if we have known_total_sqft and it matches
        if known_total_sqft and total_sqft:
            difference_pct = abs(total_sqft - known_total_sqft) / known_total_sqft
            if difference_pct < 0.05:  # Within 5%
                confidence = 0.95
            elif difference_pct < 0.10:  # Within 10%
                confidence = 0.85
            elif difference_pct < 0.20:  # Within 20%
                confidence = 0.70
            else:
                confidence = 0.50
        else:
            # Base confidence on average room confidence
            if rooms:
                avg_room_confidence = sum(r.confidence for r in rooms) / len(rooms)
                confidence = avg_room_confidence
            else:
                confidence = 0.50
        
        # Create measurements object
        measurements = FloorPlanMeasurements(
            total_square_feet=total_sqft,
            total_square_feet_confidence=confidence,
            measurement_method=data.get('measurement_method', 'ai_estimation'),
            rooms=rooms,
            quality=quality,
            detected_features=data.get('detected_features', []),
            processing_time_seconds=0  # Set by caller
        )
        
        return measurements
    
    def to_database_format(self, measurements: FloorPlanMeasurements) -> Dict[str, Any]:
        """
        Convert measurements to database-ready format
        
        Returns:
            Dict ready for insertion into floor_plan_measurements table
        """
        return {
            'total_square_feet': measurements.total_square_feet,
            'total_square_feet_confidence': measurements.total_square_feet_confidence,
            'measurement_method': measurements.measurement_method,
            'rooms': [
                {
                    'type': room.type,
                    'name': room.name,
                    'length_ft': room.length_ft,
                    'width_ft': room.width_ft,
                    'sqft': room.sqft,
                    'features': room.features,
                    'confidence': room.confidence
                }
                for room in measurements.rooms
            ],
            'quality_score': measurements.quality.overall_score,
            'quality_factors': {
                'clarity': measurements.quality.clarity,
                'completeness': measurements.quality.completeness,
                'label_quality': measurements.quality.label_quality,
                'scale_accuracy': measurements.quality.scale_accuracy
            },
            'detected_features': measurements.detected_features,
            'model_version': 'gemini-2.0-flash-exp',
            'processing_time_seconds': measurements.processing_time_seconds
        }


# Convenience function
def estimate_floor_plan_measurements(
    image_path: str,
    property_type: Optional[str] = None,
    known_total_sqft: Optional[int] = None
) -> FloorPlanMeasurements:
    """
    Convenience function to estimate floor plan measurements
    
    Args:
        image_path: Path to floor plan image
        property_type: Type of property (optional)
        known_total_sqft: Known total square footage (optional)
        
    Returns:
        FloorPlanMeasurements object
    """
    estimator = FloorPlanMeasurementEstimator()
    return estimator.estimate_measurements(image_path, property_type, known_total_sqft)


# Example usage
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python floor_plan_measurements.py <image_path> [known_sqft]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    known_sqft = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print(f"Analyzing floor plan: {image_path}")
    if known_sqft:
        print(f"Known total sqft: {known_sqft}")
    print()
    
    measurements = estimate_floor_plan_measurements(image_path, known_total_sqft=known_sqft)
    
    print("=" * 60)
    print("MEASUREMENTS")
    print("=" * 60)
    print(f"Total Square Feet: {measurements.total_square_feet}")
    print(f"Confidence: {measurements.total_square_feet_confidence:.2%}")
    print(f"Method: {measurements.measurement_method}")
    print()
    
    print("Rooms:")
    for room in measurements.rooms:
        print(f"  - {room.name} ({room.type}): {room.sqft} sqft")
        if room.length_ft and room.width_ft:
            print(f"    Dimensions: {room.length_ft}' × {room.width_ft}'")
        if room.features:
            print(f"    Features: {', '.join(room.features)}")
        print(f"    Confidence: {room.confidence:.2%}")
    
    print()
    print("Quality Assessment:")
    print(f"  Overall Score: {measurements.quality.overall_score}/100")
    print(f"  Clarity: {measurements.quality.clarity}/100")
    print(f"  Completeness: {measurements.quality.completeness}/100")
    print(f"  Label Quality: {measurements.quality.label_quality}/100")
    print(f"  Scale Accuracy: {measurements.quality.scale_accuracy}/100")
    
    print()
    print(f"Detected Features: {', '.join(measurements.detected_features)}")
    print(f"Processing Time: {measurements.processing_time_seconds:.2f}s")
