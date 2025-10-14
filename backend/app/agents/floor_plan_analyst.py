"""
Floor Plan Analyst Agent
AI Agent #1 - Analyzes floor plan images and extracts structured data
Uses CrewAI with Google Gemini Vision for image understanding
"""

import os
import base64
import json
import requests
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from crewai import Agent, Task, Crew
from crewai.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from app.parsing.parser import FloorPlanParser
from litellm import completion as litellm_completion

class Room(BaseModel):
    """Individual room information"""
    type: str = Field(description="Room type (e.g., bedroom, bathroom, kitchen, living room)")
    dimensions: Optional[str] = Field(default="", description="Room dimensions if visible (e.g., '12x14')")
    features: List[str] = Field(default_factory=list, description="Room features (closet, window, etc.)")
    
    @field_validator('dimensions', mode='before')
    @classmethod
    def validate_dimensions(cls, v):
        """Convert None to empty string"""
        return v if v is not None else ""


class FloorPlanData(BaseModel):
    """Structured floor plan analysis output"""
    address: Optional[str] = Field(default="", description="Property address if visible on floor plan")
    bedrooms: int = Field(default=0, description="Number of bedrooms")
    bathrooms: float = Field(default=0.0, description="Number of bathrooms (0.5 for half bath)")
    square_footage: int = Field(default=0, description="Total square footage")
    rooms: List[Room] = Field(default_factory=list, description="List of all rooms identified")
    features: List[str] = Field(default_factory=list, description="Overall property features")
    layout_type: Optional[str] = Field(default="", description="Layout description (e.g., 'Open concept', 'Split level')")
    notes: Optional[str] = Field(default="", description="Additional observations or unclear elements")
    
    @field_validator('address', 'layout_type', 'notes', mode='before')
    @classmethod
    def validate_strings(cls, v):
        """Convert None to empty string for all string fields"""
        return v if v is not None else ""


# ================================
# CrewAI Tools
# ================================

def _analyze_with_gemini_vision(image_url: str, image_bytes_b64: str = None) -> str:
    """
    Internal function to analyze floor plan with Gemini Vision using LiteLLM REST API.
    Returns JSON string with structured data.
    """
    # Set API key for LiteLLM
    os.environ['GEMINI_API_KEY'] = os.getenv('GOOGLE_GEMINI_API_KEY')
    
    prompt = """Analyze this floor plan image and extract structured data.

Carefully examine the floor plan and:

1. **Count Bedrooms**: Look for rooms labeled "BR", "Bedroom", "Master", "MBR", or bedroom-sized spaces
2. **Count Bathrooms**: Count full bathrooms (1.0) and half baths (0.5). Look for "Bath", "WC", toilet symbols
3. **Identify All Rooms**: Kitchen, living room, dining room, office, garage, closets, etc.
4. **Extract Dimensions**: Look for measurements on the floor plan (e.g., "12' x 14'", room sizes)
5. **Calculate Square Footage**: Sum all room dimensions if visible, otherwise estimate based on scale
6. **Note Features**: Garage, patio, balcony, fireplace, walk-in closets, etc.
7. **Layout Type**: Open concept, traditional, split-level, etc.
8. **Extract Text**: Any visible address, lot size, or property details

Return a JSON object with this exact structure:
{
  "address": "address if visible, otherwise empty string",
  "bedrooms": number (count of bedrooms),
  "bathrooms": number (use 0.5 for half bath, 1.0 for full),
  "square_footage": number (total sq ft),
  "rooms": [
    {
      "type": "room type (bedroom, bathroom, kitchen, etc.)",
      "dimensions": "dimensions if visible (e.g., 12' x 14')",
      "features": ["feature1", "feature2"]
    }
  ],
  "features": ["overall property features"],
  "layout_type": "layout description",
  "notes": "any observations or unclear elements"
}

Be precise with bedroom and bathroom counts. This is critical for real estate listings."""
    
    try:
        # Prepare image data URL
        if image_bytes_b64:
            image_data = f"data:image/jpeg;base64,{image_bytes_b64}"
        else:
            response_data = requests.get(image_url).content
            image_b64 = base64.b64encode(response_data).decode('utf-8')
            image_data = f"data:image/jpeg;base64,{image_b64}"
        
        # Call Gemini via LiteLLM (REST API only, no gRPC)
        response = litellm_completion(
            model="gemini/gemini-2.5-flash",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data}}
                    ]
                }
            ],
            response_format={"type": "json_object"}
        )
        
        return response.choices[0].message.content  # Returns JSON string
        
    except Exception as e:
        # Return error in JSON format
        error_response = {
            "address": "",
            "bedrooms": 0,
            "bathrooms": 0.0,
            "square_footage": 0,
            "rooms": [],
            "features": [],
            "layout_type": "",
            "notes": f"Error analyzing image: {str(e)}"
        }
        return json.dumps(error_response)


@tool("Floor Plan Image Analyzer")
def analyze_image_with_gemini(image_url: str, image_bytes_b64: str = None) -> str:
    """
    Tool wrapper for Gemini Vision floor plan analysis.
    
    Args:
        image_url: URL to the floor plan image
        image_bytes_b64: Base64 encoded image bytes (optional)
    
    Returns:
        str: JSON string with structured floor plan data
    """
    return _analyze_with_gemini_vision(image_url, image_bytes_b64)


# ================================
# Floor Plan Analyst Agent (CrewAI)
# ================================

class FloorPlanAnalyst:
    """
    AI Agent specialized in analyzing floor plan images using CrewAI
    
    Uses Google Gemini 2.0 Flash with vision capabilities to:
    - Identify rooms and their types
    - Count bedrooms and bathrooms
    - Estimate square footage
    - Extract property features
    - Parse any visible text (address, dimensions)
    """
    
    def __init__(self):
        # Initialize Gemini 2.5 Flash LLM for CrewAI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0.1
        )
        
        # Initialize OCR Parser (Gemini Vision + Pytesseract fallback)
        self.ocr_parser = FloorPlanParser()
        
        self.role = "Expert Real Estate Floor Plan Analyst"
        
        self.goal = """Analyze floor plan images to extract comprehensive property data 
        including room counts, dimensions, layout, and features with high accuracy"""
        
        self.backstory = """You are an experienced real estate analyst with 15 years 
        of expertise in reading architectural floor plans. You have a keen eye for 
        detail and can identify room types, count spaces accurately, and estimate 
        dimensions from floor plan layouts. You understand real estate terminology 
        and can distinguish between bedrooms, bathrooms, living spaces, and utility 
        areas with precision."""
        
        # Create CrewAI agent
        self.agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=[analyze_image_with_gemini],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def analyze_floor_plan(self, image_url: str = None, image_bytes: bytes = None) -> Dict[str, Any]:
        """
        Analyze a floor plan image using DUAL STRATEGY:
        1. OCR Parser (Gemini Vision + Pytesseract) for dimensions
        2. Gemini Vision for room analysis and layout
        3. Merge both for complete data
        
        Args:
            image_url: URL to the floor plan image (optional)
            image_bytes: Raw image bytes (optional)
        
        Returns:
            Dictionary with extracted floor plan data matching FloorPlanData schema
        """
        if not image_url and not image_bytes:
            raise ValueError("Either image_url or image_bytes must be provided")
        
        # Prepare image data
        image_bytes_b64 = None
        if image_bytes:
            image_bytes_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        try:
            # STEP 1: Extract dimensions using OCR Parser (Gemini + Pytesseract)
            print("🔍 Step 1: Running OCR to extract dimensions...")
            ocr_result = None
            if image_bytes:
                ocr_result = self.ocr_parser.parse_dimensions_from_image(image_bytes)
                print(f"   OCR found {len(ocr_result.get('dimensions', []))} dimensions via {ocr_result.get('extraction_method', 'unknown')}")
            
            # STEP 2: Analyze floor plan layout with Gemini Vision
            print("🔍 Step 2: Analyzing floor plan layout with Gemini Vision...")
            result_text = _analyze_with_gemini_vision(
                image_url=image_url or '',
                image_bytes_b64=image_bytes_b64 or ''
            )
            
            # Parse JSON (tool returns valid JSON string)
            extracted_data = json.loads(result_text)
            
            # STEP 3: Merge OCR dimensions with Vision analysis
            if ocr_result and ocr_result.get('has_dimensions'):
                print("🔗 Step 3: Merging OCR dimensions with Vision analysis...")
                
                # Use OCR square footage if more confident (handle None values)
                ocr_sqft = ocr_result.get('total_sqft') or 0
                if ocr_sqft > 0:
                    extracted_data['square_footage'] = ocr_sqft
                
                # Add OCR dimensions to room data
                for dim in ocr_result.get('dimensions', []):
                    room_name = dim.get('room', '') or ''
                    # Try to match with existing rooms or add as new
                    matched = False
                    for room in extracted_data.get('rooms', []):
                        room_type = room.get('type', '') or ''
                        if room_name and room_type and room_name.lower() in room_type.lower():
                            room['dimensions'] = dim.get('raw_text', '') or ''
                            matched = True
                            break
                    
                    if not matched and room_name:
                        # Add as new room
                        extracted_data.setdefault('rooms', []).append({
                            'type': room_name,
                            'dimensions': dim.get('raw_text', '') or '',
                            'features': []
                        })
                
                # Add OCR metadata to notes
                extraction_method = ocr_result.get('extraction_method', 'unknown')
                extracted_data['notes'] = f"{extracted_data.get('notes', '')} | OCR: {extraction_method}".strip(' |')
            
            # Validate against schema
            validated_data = FloorPlanData(**extracted_data)
            
            print(f"✅ Floor plan analysis complete: {validated_data.bedrooms} BR, {validated_data.bathrooms} BA, {validated_data.square_footage} sq ft")
            
            return validated_data.model_dump()
            
        except Exception as e:
            print(f"❌ Floor plan analysis error: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return partial data on error
            return {
                'address': '',
                'bedrooms': 0,
                'bathrooms': 0.0,
                'square_footage': 0,
                'rooms': [],
                'features': [],
                'layout_type': '',
                'notes': f'Error analyzing floor plan: {str(e)}'
            }
    
    def get_agent_info(self) -> Dict[str, str]:
        """Return agent metadata"""
        return {
            'name': 'Floor Plan Analyst (CrewAI)',
            'role': self.role,
            'goal': self.goal,
            'backstory': self.backstory,
            'model': 'gemini-2.0-flash-exp',
            'framework': 'CrewAI',
            'capabilities': [
                'Image analysis with Gemini Vision',
                'Room identification',
                'Dimension extraction',
                'Feature detection',
                'Layout assessment',
                'Tool-based architecture'
            ]
        }


# ================================
# Convenience Functions
# ================================

def analyze_floor_plan_from_url(image_url: str) -> Dict[str, Any]:
    """
    Quick function to analyze a floor plan from a URL
    
    Args:
        image_url: Public URL to the floor plan image
    
    Returns:
        Extracted floor plan data as dictionary
    """
    analyst = FloorPlanAnalyst()
    return analyst.analyze_floor_plan(image_url=image_url)


def analyze_floor_plan_from_bytes(image_bytes: bytes) -> Dict[str, Any]:
    """
    Quick function to analyze a floor plan from raw bytes
    
    Args:
        image_bytes: Raw image data
    
    Returns:
        Extracted floor plan data as dictionary
    """
    analyst = FloorPlanAnalyst()
    return analyst.analyze_floor_plan(image_bytes=image_bytes)
