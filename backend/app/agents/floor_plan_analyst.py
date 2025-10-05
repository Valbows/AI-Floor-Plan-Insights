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
from crewai_tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

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

@tool("Floor Plan Image Analyzer")
def analyze_image_with_gemini(image_url: str, image_bytes_b64: str = None) -> str:
    """
    Analyze a floor plan image using Google Gemini Vision.
    
    Args:
        image_url: URL to the floor plan image
        image_bytes_b64: Base64 encoded image bytes (optional)
    
    Returns:
        str: Detailed analysis of the floor plan
    """
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = """Analyze this floor plan image in detail:
    
1. Count all bedrooms (look for "BR", "Bedroom", "Master", etc.)
2. Count all bathrooms (full baths = 1.0, half baths = 0.5)
3. Identify all rooms (type, dimensions if visible, features)
4. Calculate or estimate total square footage
5. Note overall property features (garage, patio, balcony, etc.)
6. Describe the layout type (open concept, traditional, etc.)
7. Extract any visible text (address, dimensions)

Be precise and thorough."""
    
    try:
        if image_bytes_b64:
            image_part = {'mime_type': 'image/png', 'data': image_bytes_b64}
        else:
            response_data = requests.get(image_url).content
            image_part = {'mime_type': 'image/png', 'data': base64.b64encode(response_data).decode('utf-8')}
        
        response = model.generate_content([prompt, image_part])
        return response.text
    except Exception as e:
        return f"Error analyzing image: {str(e)}"


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
        # Initialize Gemini LLM for CrewAI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=os.getenv('GOOGLE_GEMINI_API_KEY'),
            temperature=0.1
        )
        
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
        Analyze a floor plan image and extract structured data using CrewAI
        
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
        elif image_url:
            # Ensure we have URL for the tool
            pass
        
        # Create analysis task
        task_description = f"""
Analyze the floor plan image at: {image_url or 'provided bytes'}

Extract the following structured data:

1. **Address**: If visible on the floor plan, extract it. Otherwise leave empty.
2. **Bedrooms**: Count the number of bedrooms (BR, Bedroom, Master Bedroom, etc.)
3. **Bathrooms**: Count full bathrooms and half baths (use 0.5 for half bath, 1.0 for full)
4. **Square Footage**: If dimensions are visible, calculate. Otherwise estimate based on room count and layout.
5. **Rooms**: List all identifiable rooms with:
   - type (bedroom, bathroom, kitchen, living room, dining room, office, etc.)
   - dimensions if visible (e.g., "12' x 14'")
   - features (closet, window, door positions, etc.)
6. **Features**: Overall property features (garage, patio, balcony, fireplace, etc.)
7. **Layout Type**: Describe the layout (open concept, traditional, split-level, etc.)
8. **Notes**: Any observations, unclear elements, or important details

Be precise with counts. If something is unclear, note it in the notes field.

Provide your response as a JSON object matching this exact structure:
{{
  "address": "string or empty",
  "bedrooms": number,
  "bathrooms": number (use decimals for half baths),
  "square_footage": number,
  "rooms": [
    {{
      "type": "room type",
      "dimensions": "dimensions if visible",
      "features": ["feature1", "feature2"]
    }}
  ],
  "features": ["feature1", "feature2"],
  "layout_type": "layout description",
  "notes": "additional observations"
}}
"""
        
        task = Task(
            description=task_description,
            agent=self.agent,
            expected_output="JSON object with floor plan analysis data"
        )
        
        # Create crew and execute
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        try:
            # Execute the task
            result = crew.kickoff(inputs={'image_url': image_url or '', 'image_bytes_b64': image_bytes_b64 or ''})
            
            # Parse the result
            result_text = str(result).strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            result_text = result_text.strip()
            
            # Parse JSON
            extracted_data = json.loads(result_text)
            
            # Validate against schema
            validated_data = FloorPlanData(**extracted_data)
            
            return validated_data.model_dump()
            
        except Exception as e:
            print(f"CrewAI execution error: {str(e)}")
            # Return partial data on error
            return {
                'address': '',
                'bedrooms': 0,
                'bathrooms': 0.0,
                'square_footage': 0,
                'rooms': [],
                'features': [],
                'layout_type': '',
                'notes': f'Error analyzing floor plan with CrewAI: {str(e)}'
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
