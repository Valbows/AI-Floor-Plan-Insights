"""
Market Insights Analyst Agent
AI Agent #2 - Analyzes property market data and generates investment insights
Uses CoreLogic data + Gemini AI for market analysis
"""

import os
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from pydantic import BaseModel, Field
from app.clients.corelogic_client import CoreLogicClient

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))


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
# Market Insights Analyst Agent
# ================================

class MarketInsightsAnalyst:
    """
    AI Agent specialized in real estate market analysis
    
    Capabilities:
    - Property valuation using comps and AVM data
    - Market trend analysis
    - Investment potential assessment
    - Rental income estimation
    - Risk and opportunity identification
    
    Data Sources:
    - CoreLogic Property API (comps, AVM, property details)
    - Gemini AI for analysis and insights generation
    
    Usage:
        analyst = MarketInsightsAnalyst()
        insights = analyst.analyze_property(
            address="123 Main St, Miami, FL 33101",
            property_data={...}
        )
    """
    
    def __init__(self):
        """Initialize Market Insights Analyst"""
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.corelogic = CoreLogicClient()
        
        # Agent persona and expertise
        self.role = "Senior Real Estate Market Analyst"
        self.expertise = """You are a senior real estate market analyst with 20 years of experience 
        in residential property valuation, market trend analysis, and investment assessment. 
        You specialize in analyzing comparable sales, market conditions, and investment potential 
        to provide data-driven insights for real estate professionals."""
    
    def analyze_property(self, address: str, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive market analysis for a property
        
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
            Exception: If CoreLogic data unavailable or analysis fails
        """
        try:
            # Step 1: Get CoreLogic property data
            print(f"Fetching CoreLogic data for: {address}")
            corelogic_property = self.corelogic.search_property(address)
            clip_id = corelogic_property['clip_id']
            
            # Step 2: Get comparable properties
            print(f"Finding comparable properties...")
            comps = self.corelogic.get_comparables(clip_id, radius_miles=1.0, max_results=5)
            
            # Step 3: Get AVM estimate (if available)
            avm_estimate = None
            try:
                avm_estimate = self.corelogic.estimate_value(clip_id)
            except Exception as e:
                print(f"AVM not available: {e}")
            
            # Step 4: Run AI analysis
            print(f"Running AI market analysis...")
            insights = self._generate_insights(
                property_data=property_data,
                corelogic_data=corelogic_property,
                comps=comps,
                avm=avm_estimate
            )
            
            return insights
            
        except Exception as e:
            print(f"Market analysis error: {str(e)}")
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
