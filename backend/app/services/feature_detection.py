"""
Feature Detection Service for Floor Plans
Uses Google Vision API to detect doors, windows, and other architectural features

Features:
- Door detection and counting
- Window detection and counting
- Architectural element recognition
- Feature localization (where on the floor plan)
- Integration with floor plan measurements
"""

import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)


@dataclass
class DetectedFeature:
    """A detected architectural feature"""
    type: str  # 'door', 'window', 'closet', 'stairs', etc.
    location: str  # 'north wall', 'east wall', room name, etc.
    quantity: int  # Number of this feature type
    confidence: float  # 0-1
    description: Optional[str] = None


@dataclass
class FeatureDetectionResult:
    """Complete feature detection results"""
    total_doors: int
    total_windows: int
    total_closets: int
    features_by_room: Dict[str, List[DetectedFeature]]
    overall_features: List[DetectedFeature]
    detection_confidence: float
    processing_time_seconds: float


class FloorPlanFeatureDetector:
    """
    Detects architectural features (doors, windows, etc.) in floor plans
    using Google Gemini Vision
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize feature detector
        
        Args:
            api_key: Google Gemini API key (or from GOOGLE_GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GOOGLE_GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("Google Gemini API key required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        logger.info("Floor Plan Feature Detector initialized")
    
    def detect_features(
        self,
        image_path: str,
        room_data: Optional[List[Dict[str, Any]]] = None
    ) -> FeatureDetectionResult:
        """
        Detect architectural features in a floor plan
        
        Args:
            image_path: Path to floor plan image
            room_data: Optional list of rooms (from measurement estimator)
            
        Returns:
            FeatureDetectionResult with detected features
        """
        import time
        start_time = time.time()
        
        logger.info(f"Detecting features in floor plan: {image_path}")
        
        # Read image
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Build prompt
        prompt = self._build_detection_prompt(room_data)
        
        try:
            # Analyze with Gemini Vision
            response = self.model.generate_content([
                prompt,
                {'mime_type': 'image/png', 'data': image_data}
            ])
            
            result_text = response.text
            logger.debug(f"Gemini response: {result_text[:500]}...")
            
            # Parse response
            result = self._parse_response(result_text, room_data)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            result.processing_time_seconds = processing_time
            
            logger.info(f"Feature detection complete in {processing_time:.2f}s - "
                       f"{result.total_doors} doors, {result.total_windows} windows")
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to detect features: {e}")
            raise
    
    def _build_detection_prompt(self, room_data: Optional[List[Dict[str, Any]]]) -> str:
        """Build the AI prompt for feature detection"""
        
        prompt = """You are an expert at analyzing architectural floor plans. 
Analyze this floor plan image and detect all doors, windows, and other architectural features.

TASK:
1. Count all doors (interior doors, exterior doors, sliding doors, etc.)
2. Count all windows (standard windows, bay windows, etc.)
3. Identify closets, walk-in closets, and storage areas
4. Detect stairs, elevators, or level changes
5. Identify other features (fireplace, built-in shelves, etc.)
6. For each feature, note which room or area it belongs to

INSTRUCTIONS:
- Look for standard architectural symbols (door arcs, window lines, etc.)
- Count carefully - every door and window matters
- Include exterior and interior doors separately if visible
- Note the location/orientation of features when possible
"""
        
        if room_data:
            prompt += f"\n\nKNOWN ROOMS (use these names for location reference):\n"
            for room in room_data:
                prompt += f"- {room.get('name', 'Unknown')} ({room.get('type', 'unknown')})\n"
        
        prompt += """
OUTPUT FORMAT (valid JSON only):
{
  "doors": {
    "total": 8,
    "by_type": {
      "interior": 5,
      "exterior": 2,
      "sliding": 1
    },
    "by_room": [
      {
        "room": "Master Bedroom",
        "type": "interior",
        "quantity": 1,
        "location": "west wall",
        "confidence": 0.95
      }
    ]
  },
  "windows": {
    "total": 12,
    "by_room": [
      {
        "room": "Living Room",
        "quantity": 3,
        "location": "south wall",
        "confidence": 0.90
      }
    ]
  },
  "closets": {
    "total": 4,
    "details": [
      {
        "room": "Master Bedroom",
        "type": "walk-in",
        "quantity": 1,
        "confidence": 0.95
      }
    ]
  },
  "other_features": [
    {
      "type": "stairs",
      "location": "hallway",
      "description": "interior stairs",
      "confidence": 0.90
    },
    {
      "type": "fireplace",
      "location": "living room",
      "confidence": 0.85
    }
  ],
  "detection_confidence": 0.88
}

IMPORTANT:
- Return ONLY valid JSON, no markdown, no explanations
- confidence: 0.0-1.0 (how confident you are in each detection)
- Be thorough but accurate
- If uncertain about a feature, note it with lower confidence
"""
        
        return prompt
    
    def _parse_response(
        self,
        response_text: str,
        room_data: Optional[List[Dict[str, Any]]]
    ) -> FeatureDetectionResult:
        """Parse Gemini's response into structured feature data"""
        import json
        
        # Extract JSON from response
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
            # Return empty result
            return FeatureDetectionResult(
                total_doors=0,
                total_windows=0,
                total_closets=0,
                features_by_room={},
                overall_features=[],
                detection_confidence=0.0,
                processing_time_seconds=0.0
            )
        
        # Extract totals
        total_doors = data.get('doors', {}).get('total', 0)
        total_windows = data.get('windows', {}).get('total', 0)
        total_closets = data.get('closets', {}).get('total', 0)
        
        # Parse features by room
        features_by_room = {}
        
        # Add door features
        for door_data in data.get('doors', {}).get('by_room', []):
            room = door_data.get('room', 'Unknown')
            if room not in features_by_room:
                features_by_room[room] = []
            
            features_by_room[room].append(DetectedFeature(
                type='door',
                location=door_data.get('location', 'unknown'),
                quantity=door_data.get('quantity', 1),
                confidence=door_data.get('confidence', 0.5),
                description=f"{door_data.get('type', 'door')}"
            ))
        
        # Add window features
        for window_data in data.get('windows', {}).get('by_room', []):
            room = window_data.get('room', 'Unknown')
            if room not in features_by_room:
                features_by_room[room] = []
            
            features_by_room[room].append(DetectedFeature(
                type='window',
                location=window_data.get('location', 'unknown'),
                quantity=window_data.get('quantity', 1),
                confidence=window_data.get('confidence', 0.5),
                description='window'
            ))
        
        # Add closet features
        for closet_data in data.get('closets', {}).get('details', []):
            room = closet_data.get('room', 'Unknown')
            if room not in features_by_room:
                features_by_room[room] = []
            
            features_by_room[room].append(DetectedFeature(
                type='closet',
                location=room,
                quantity=closet_data.get('quantity', 1),
                confidence=closet_data.get('confidence', 0.5),
                description=closet_data.get('type', 'closet')
            ))
        
        # Parse overall features
        overall_features = []
        for feature_data in data.get('other_features', []):
            overall_features.append(DetectedFeature(
                type=feature_data.get('type', 'unknown'),
                location=feature_data.get('location', 'unknown'),
                quantity=1,
                confidence=feature_data.get('confidence', 0.5),
                description=feature_data.get('description')
            ))
        
        # Overall confidence
        detection_confidence = data.get('detection_confidence', 0.5)
        
        result = FeatureDetectionResult(
            total_doors=total_doors,
            total_windows=total_windows,
            total_closets=total_closets,
            features_by_room=features_by_room,
            overall_features=overall_features,
            detection_confidence=detection_confidence,
            processing_time_seconds=0.0  # Set by caller
        )
        
        return result
    
    def to_database_format(self, result: FeatureDetectionResult) -> Dict[str, Any]:
        """
        Convert feature detection to database-ready format
        
        Can be stored in floor_plan_measurements.detected_features (JSONB)
        """
        features_by_room_dict = {}
        for room, features in result.features_by_room.items():
            features_by_room_dict[room] = [
                {
                    'type': f.type,
                    'location': f.location,
                    'quantity': f.quantity,
                    'confidence': f.confidence,
                    'description': f.description
                }
                for f in features
            ]
        
        return {
            'totals': {
                'doors': result.total_doors,
                'windows': result.total_windows,
                'closets': result.total_closets
            },
            'features_by_room': features_by_room_dict,
            'overall_features': [
                {
                    'type': f.type,
                    'location': f.location,
                    'quantity': f.quantity,
                    'confidence': f.confidence,
                    'description': f.description
                }
                for f in result.overall_features
            ],
            'detection_confidence': result.detection_confidence,
            'processing_time_seconds': result.processing_time_seconds
        }


# Convenience function
def detect_floor_plan_features(
    image_path: str,
    room_data: Optional[List[Dict[str, Any]]] = None
) -> FeatureDetectionResult:
    """
    Convenience function to detect features in a floor plan
    
    Args:
        image_path: Path to floor plan image
        room_data: Optional room data for context
        
    Returns:
        FeatureDetectionResult
    """
    detector = FloorPlanFeatureDetector()
    return detector.detect_features(image_path, room_data)


# Example usage
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python feature_detection.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    print("=" * 70)
    print("FLOOR PLAN FEATURE DETECTION")
    print("=" * 70)
    print()
    
    result = detect_floor_plan_features(image_path)
    
    print(f"Total Doors: {result.total_doors}")
    print(f"Total Windows: {result.total_windows}")
    print(f"Total Closets: {result.total_closets}")
    print(f"Detection Confidence: {result.detection_confidence:.2%}")
    print()
    
    print("Features by Room:")
    for room, features in result.features_by_room.items():
        print(f"\n  {room}:")
        for feature in features:
            print(f"    - {feature.quantity}x {feature.description} "
                  f"({feature.location}, confidence: {feature.confidence:.2%})")
    
    if result.overall_features:
        print("\nOther Features:")
        for feature in result.overall_features:
            print(f"  - {feature.type}: {feature.description} "
                  f"({feature.location}, confidence: {feature.confidence:.2%})")
    
    print()
    print(f"Processing Time: {result.processing_time_seconds:.2f}s")
    print("=" * 70)
