"""
Market Insights Analyst Agent
AI Agent #2 - Analyzes property market data and generates investment insights
Uses CrewAI with CoreLogic data + Gemini AI + Web Search
"""

import os
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew
from crewai_tools import tool, SerperDevTool
from langchain_google_genai import ChatGoogleGenerativeAI
from app.clients.corelogic_client import CoreLogicClient


# ================================
# Structured Output Schemas
# ================================

class PriceEstimate(BaseModel):
    """Property price estimation"""
    estimated_value: int = Field(description="Estimated market value in USD")
    confidence: str = Field(description="Confidence level: low, medium, high")
    value_range_low: int = Field(description="Lower bound of value range")
    value_range_high: int = Field(description="Upper bound of value range")
    reasoning: str = Field(description="Explanation of valuation reasoning")


class MarketTrend(BaseModel):
    """Local market trend analysis"""
    trend_direction: str = Field(description="Market trend: rising, stable, declining")
    appreciation_rate: Optional[float] = Field(default=None, description="Annual appreciation rate %")
    days_on_market_avg: Optional[int] = Field(default=None, description="Average days properties stay on market")
    inventory_level: str = Field(description="Inventory: low, balanced, high")
    buyer_demand: str = Field(description="Demand level: low, moderate, high, very_high")
    insights: str = Field(description="Key market insights and trends")


class InvestmentAnalysis(BaseModel):
    """Investment potential assessment"""
    investment_score: int = Field(description="Investment score 1-100")
    rental_potential: str = Field(description="Rental potential: poor, fair, good, excellent")
    estimated_rental_income: Optional[int] = Field(default=None, description="Monthly rental income estimate")
    cap_rate: Optional[float] = Field(default=None, description="Capitalization rate %")
    appreciation_potential: str = Field(description="Appreciation: low, moderate, high")
    risk_factors: List[str] = Field(description="List of investment risks")
    opportunities: List[str] = Field(description="List of investment opportunities")


class MarketInsights(BaseModel):
    """Complete market insights report"""
    price_estimate: PriceEstimate
    market_trend: MarketTrend
    investment_analysis: InvestmentAnalysis
    comparable_properties: List[Dict[str, Any]] = Field(description="List of comparable properties")
    summary: str = Field(description="Executive summary of market insights")


# ================================
# CrewAI Tools for Market Analysis
# ================================

@tool("CoreLogic Property Search")
def search_property_data(address: str) -> str:
    """
    Search CoreLogic database for property information.
    
    Args:
        address: Full property address
    
    Returns:
        str: Property details including CLIP ID, property type, year built, etc.
    """
    try:
        client = CoreLogicClient()
        property_data = client.search_property(address)
        return json.dumps(property_data, indent=2)
    except Exception as e:
        return f"Error fetching property data: {str(e)}"


@tool("CoreLogic Comparables")
def get_comparable_properties(clip_id: str, radius_miles: float = 1.0) -> str:
    """
    Fetch comparable properties from CoreLogic.
    
    Args:
        clip_id: CoreLogic property ID
        radius_miles: Search radius in miles
    
    Returns:
        str: List of comparable properties with sale prices and details
    """
    try:
        client = CoreLogicClient()
        comps = client.get_comparables(clip_id, radius_miles=radius_miles, max_results=5)
        return json.dumps(comps, indent=2)
    except Exception as e:
        return f"Error fetching comparables: {str(e)}"


@tool("CoreLogic AVM Estimate")
def get_avm_estimate(clip_id: str) -> str:
    """
    Get Automated Valuation Model (AVM) estimate from CoreLogic.
    
    Args:
        clip_id: CoreLogic property ID
    
    Returns:
        str: AVM valuation with confidence score and value range
    """
    try:
        client = CoreLogicClient()
        avm = client.estimate_value(clip_id)
        return json.dumps(avm, indent=2)
    except Exception as e:
        return f"AVM not available: {str(e)}"


# ================================
# Market Insights Analyst Agent (CrewAI)
# ================================

class MarketInsightsAnalyst:
    """
    AI Agent specialized in real estate market analysis using CrewAI
    
    Capabilities:
    - Property valuation using comps and AVM data
    - Market trend analysis with web search
    - Investment potential assessment
    - Rental income estimation
    - Risk and opportunity identification
    
    Data Sources:
    - CoreLogic Property API (comps, AVM, property details)
    - Web search for local market trends
    - Gemini AI for analysis and insights generation
    
    Usage:
        analyst = MarketInsightsAnalyst()
        insights = analyst.analyze_property(
            address="123 Main St, Miami, FL 33101",
            property_data={...}
        )
    """
    
    def __init__(self):
        """Initialize Market Insights Analyst with CrewAI"""
        self.corelogic = CoreLogicClient()
        
        # Initialize Gemini LLM for CrewAI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=os.getenv('GOOGLE_GEMINI_API_KEY'),
            temperature=0.1
        )
        
        # Agent persona and expertise
        self.role = "Senior Real Estate Market Analyst"
        self.expertise = """You are a senior real estate market analyst with 20 years of experience 
        in residential property valuation, market trend analysis, and investment assessment. 
        You specialize in analyzing comparable sales, market conditions, and investment potential 
        to provide data-driven insights for real estate professionals."""
        
        # Create web search tool (optional - requires Serper API key)
        self.search_tool = SerperDevTool() if os.getenv('SERPER_API_KEY') else None
        
        # Build tools list
        tools = [search_property_data, get_comparable_properties, get_avm_estimate]
        if self.search_tool:
            tools.append(self.search_tool)
        
        # Create CrewAI agent
        self.agent = Agent(
            role=self.role,
            goal="Analyze property market data and provide comprehensive investment insights",
            backstory=self.expertise,
            tools=tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def analyze_property(self, address: str, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive market analysis for a property using CrewAI
        
        Args:
            address: Property address
            property_data: Floor plan data from Agent #1
                {
                    "bedrooms": 3,
                    "bathrooms": 2.0,
                    "square_footage": 1500,
                    "features": [...],
                    "layout_type": "Traditional"
                }
        
        Returns:
            {
                "price_estimate": {...},
                "market_trend": {...},
                "investment_analysis": {...},
                "comparable_properties": [...],
                "summary": "Executive summary..."
            }
        
        Raises:
            Exception: If CorewAI execution fails
        """
        try:
            # Create analysis task for CrewAI
            task_description = f"""
Analyze the real estate market for the following property:

ADDRESS: {address}

PROPERTY DETAILS (from floor plan analysis):
- Bedrooms: {property_data.get('bedrooms', 0)}
- Bathrooms: {property_data.get('bathrooms', 0)}
- Square Footage: {property_data.get('square_footage', 0)}
- Layout: {property_data.get('layout_type', 'Not specified')}
- Features: {', '.join(property_data.get('features', []))}

TASKS:
1. Use the CoreLogic Property Search tool to find property details
2. Use the CoreLogic Comparables tool to find similar properties
3. Use the CoreLogic AVM Estimate tool to get automated valuation
4. If web search is available, research local market trends for the area
5. Analyze all data and provide:
   - Price estimate with confidence level and reasoning
   - Market trend analysis (direction, appreciation, demand, inventory)
   - Investment analysis (score 1-100, rental potential, cap rate, risks, opportunities)
   - Executive summary with actionable insights

Provide your analysis in JSON format matching the MarketInsights schema:
{{
  "price_estimate": {{
    "estimated_value": number,
    "confidence": "low/medium/high",
    "value_range_low": number,
    "value_range_high": number,
    "reasoning": "detailed explanation"
  }},
  "market_trend": {{
    "trend_direction": "rising/stable/declining",
    "appreciation_rate": number or null,
    "days_on_market_avg": number or null,
    "inventory_level": "low/balanced/high",
    "buyer_demand": "low/moderate/high/very_high",
    "insights": "market insights"
  }},
  "investment_analysis": {{
    "investment_score": number (1-100),
    "rental_potential": "poor/fair/good/excellent",
    "estimated_rental_income": number or null,
    "cap_rate": number or null,
    "appreciation_potential": "low/moderate/high",
    "risk_factors": ["risk1", "risk2"],
    "opportunities": ["opp1", "opp2"]
  }},
  "comparable_properties": [],
  "summary": "executive summary"
}}

Be data-driven and specific. Use actual numbers from CoreLogic data.
"""
            
            task = Task(
                description=task_description,
                agent=self.agent,
                expected_output="JSON object with comprehensive market analysis"
            )
            
            # Create crew and execute
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            print(f"[CrewAI] Starting market analysis for: {address}")
            result = crew.kickoff(inputs={'address': address})
            
            # Parse result
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
            insights_data = json.loads(result_text)
            
            # Validate against schema
            validated = MarketInsights(**insights_data)
            
            return validated.model_dump()
            
        except Exception as e:
            print(f"CrewAI market analysis error: {str(e)}")
            # Return fallback data
            return self._generate_fallback_insights(property_data, str(e))
    
    def _generate_insights(self, property_data: Dict, corelogic_data: Dict, 
                          comps: List[Dict], avm: Optional[Dict]) -> Dict[str, Any]:
        """
        Use Gemini AI to generate market insights from data
        
        Args:
            property_data: Floor plan data
            corelogic_data: CoreLogic property info
            comps: Comparable properties
            avm: AVM estimate (if available)
        
        Returns:
            Structured market insights
        """
        # Build comprehensive prompt with all data
        prompt = f"""
{self.expertise}

SUBJECT PROPERTY ANALYSIS REQUEST:

PROPERTY DETAILS:
- Address: {corelogic_data.get('address', 'Not specified')}
- City: {corelogic_data.get('city', 'Not specified')}
- Property Type: {corelogic_data.get('property_type', 'Not specified')}
- Year Built: {corelogic_data.get('year_built', 'Not specified')}

FLOOR PLAN DATA (from AI analysis):
- Bedrooms: {property_data.get('bedrooms', 0)}
- Bathrooms: {property_data.get('bathrooms', 0)}
- Square Footage: {property_data.get('square_footage', 0)}
- Layout: {property_data.get('layout_type', 'Not specified')}
- Features: {', '.join(property_data.get('features', []))}

COMPARABLE SALES (last 6 months):
{self._format_comps(comps)}

AVM ESTIMATE:
{self._format_avm(avm) if avm else 'Not available'}

LAST SALE INFO:
- Sale Date: {corelogic_data.get('last_sale_date', 'Not available')}
- Sale Price: ${corelogic_data.get('last_sale_price', 0):,}

ASSESSED VALUE: ${corelogic_data.get('assessed_value', 0):,}

ANALYSIS REQUIRED:
1. Price Estimate: Provide detailed valuation with confidence level and reasoning
2. Market Trend: Analyze local market conditions, appreciation rates, and inventory
3. Investment Analysis: Score investment potential (1-100), rental income estimate, cap rate, risks, and opportunities
4. Executive Summary: Synthesize all findings into actionable insights

Provide data-driven analysis based on the comparable sales, market trends, and property characteristics. 
Be specific with numbers and reasoning. Consider location, condition, features, and market timing.

Respond with a comprehensive market analysis in JSON format following the MarketInsights schema.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=MarketInsights
                )
            )
            
            # Parse and return structured insights
            import json
            insights_data = json.loads(response.text)
            
            # Add comps list to response
            insights_data['comparable_properties'] = comps
            
            return insights_data
            
        except Exception as e:
            raise Exception(f"AI market analysis failed: {str(e)}")
    
    def _format_comps(self, comps: List[Dict]) -> str:
        """Format comparable properties for prompt"""
        if not comps:
            return "No recent comparable sales found"
        
        formatted = []
        for i, comp in enumerate(comps, 1):
            formatted.append(f"""
Comp #{i}:
- Address: {comp.get('address', 'Unknown')}
- Distance: {comp.get('distance_miles', 0):.2f} miles
- Beds/Baths: {comp.get('bedrooms', 0)}/{comp.get('bathrooms', 0)}
- Square Feet: {comp.get('square_feet', 0):,}
- Year Built: {comp.get('year_built', 'Unknown')}
- Sale Date: {comp.get('last_sale_date', 'Unknown')}
- Sale Price: ${comp.get('last_sale_price', 0):,}
- Price/SqFt: ${comp.get('last_sale_price', 0) / max(comp.get('square_feet', 1), 1):.2f}
- Similarity: {comp.get('similarity_score', 0)}%
""")
        
        return '\n'.join(formatted)
    
    def _format_avm(self, avm: Dict) -> str:
        """Format AVM estimate for prompt"""
        return f"""
- Estimated Value: ${avm.get('estimated_value', 0):,}
- Confidence: {avm.get('confidence_score', 0)}%
- Value Range: ${avm.get('value_range_low', 0):,} - ${avm.get('value_range_high', 0):,}
- As of Date: {avm.get('as_of_date', 'Unknown')}
"""
    
    def _generate_fallback_insights(self, property_data: Dict, error_message: str) -> Dict[str, Any]:
        """
        Generate basic insights when CoreLogic data is unavailable
        
        Used when:
        - CoreLogic API is down
        - Property not found in database
        - API quota exceeded
        """
        bedrooms = property_data.get('bedrooms', 0)
        bathrooms = property_data.get('bathrooms', 0)
        sqft = property_data.get('square_footage', 0)
        
        # Rough estimate based on square footage (national average ~$200/sqft)
        estimated_value = sqft * 200 if sqft > 0 else 300000
        
        return {
            'price_estimate': {
                'estimated_value': estimated_value,
                'confidence': 'low',
                'value_range_low': int(estimated_value * 0.85),
                'value_range_high': int(estimated_value * 1.15),
                'reasoning': f'Estimate based on square footage only. CoreLogic data unavailable: {error_message}'
            },
            'market_trend': {
                'trend_direction': 'unknown',
                'appreciation_rate': None,
                'days_on_market_avg': None,
                'inventory_level': 'unknown',
                'buyer_demand': 'unknown',
                'insights': 'Market data unavailable. Unable to analyze local trends.'
            },
            'investment_analysis': {
                'investment_score': 50,
                'rental_potential': 'fair',
                'estimated_rental_income': None,
                'cap_rate': None,
                'appreciation_potential': 'moderate',
                'risk_factors': ['Limited market data available', 'Unable to verify property details'],
                'opportunities': ['Potential value-add through renovations']
            },
            'comparable_properties': [],
            'summary': f'Limited market analysis available. {bedrooms} bed, {bathrooms} bath property estimated at ${estimated_value:,}. Full analysis requires CoreLogic property data.'
        }
