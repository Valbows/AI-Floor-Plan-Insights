"""
Market Insights Analyst Agent
AI Agent #2 - Analyzes property market data and generates investment insights
Uses CrewAI with ATTOM API + Multi-Source Web Scraping + Gemini AI

Data Sources:
- ATTOM API (property data, AVM, sales history, area stats)
- Bright Data Web Scraping (Zillow, Redfin, StreetEasy)
- Tavily Web Search (market trends, neighborhood info)
"""

import os
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew
from crewai_tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from app.clients.attom_client import AttomAPIClient
import asyncio
import logging

logger = logging.getLogger(__name__)


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

@tool("ATTOM Property Search")
def search_property_data(address: str, city: str = "", state: str = "") -> str:
    """
    Search ATTOM database for property information.
    
    Args:
        address: Street address
        city: City name (optional but recommended)
        state: State abbreviation (optional but recommended)
    
    Returns:
        str: Property details including ATTOM ID, property type, year built, etc.
    """
    try:
        client = AttomAPIClient()
        property_data = client.search_property(address, city=city, state=state)
        return json.dumps(property_data, indent=2)
    except Exception as e:
        return f"Error fetching property data: {str(e)}"


@tool("ATTOM Comparables")
def get_comparable_properties(address: str, city: str, state: str, radius_miles: float = 0.5) -> str:
    """
    Fetch comparable properties from ATTOM.
    
    Args:
        address: Street address
        city: City name
        state: State abbreviation
        radius_miles: Search radius in miles (default 0.5)
    
    Returns:
        str: List of comparable properties with sale prices and details
    """
    try:
        client = AttomAPIClient()
        comps = client.get_comparables(address, city, state, radius_miles=radius_miles, max_results=10)
        return json.dumps(comps, indent=2)
    except Exception as e:
        return f"Error fetching comparables: {str(e)}"


@tool("ATTOM AVM Estimate")
def get_avm_estimate(address: str, city: str, state: str, zip_code: str = "") -> str:
    """
    Get Automated Valuation Model (AVM) estimate from ATTOM.
    
    Args:
        address: Street address
        city: City name
        state: State abbreviation
        zip_code: ZIP code (optional)
    
    Returns:
        str: AVM valuation with confidence score and value range
    """
    try:
        client = AttomAPIClient()
        avm = client.get_avm(address, city, state, zip_code=zip_code)
        return json.dumps(avm, indent=2)
    except Exception as e:
        return f"AVM not available: {str(e)}"


@tool("Multi-Source Property Scraping")
def scrape_property_data(address: str, city: str, state: str) -> str:
    """
    Scrape property data from Zillow, Redfin, and StreetEasy using Bright Data.
    
    Provides:
    - Consensus pricing from multiple sources
    - Price range (low, median, high, average)
    - Data quality score
    - Source-specific estimates (Zestimate, Redfin Estimate)
    - Walk Score, Transit Score
    - Building amenities
    
    Args:
        address: Street address
        city: City name
        state: State abbreviation
    
    Returns:
        str: Aggregated property data from web scraping
    """
    try:
        # Import here to avoid circular imports
        from app.scrapers.multi_source_scraper import MultiSourceScraper
        
        # Run async scraper in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run_scraper():
            async with MultiSourceScraper() as scraper:
                return await scraper.scrape_property(address, city, state)
        
        result = loop.run_until_complete(run_scraper())
        loop.close()
        
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.warning(f"Web scraping failed: {str(e)}")
        return f"Web scraping unavailable: {str(e)}"


@tool("Tavily Web Search")
def tavily_search_tool(query: str) -> str:
    """
    Search the web using Tavily for real estate market information.
    
    Args:
        query: Search query for market trends, neighborhood info, etc.
    
    Returns:
        str: Search results with relevant market information
    """
    try:
        from tavily import TavilyClient
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if not tavily_api_key:
            return "Tavily API key not configured"
        
        client = TavilyClient(api_key=tavily_api_key)
        response = client.search(query, max_results=5)
        
        # Format results
        results = []
        for result in response.get('results', []):
            results.append(f"Title: {result.get('title', 'N/A')}\n"
                         f"URL: {result.get('url', 'N/A')}\n"
                         f"Content: {result.get('content', 'N/A')}\n")
        
        return "\n---\n".join(results) if results else "No results found"
    except Exception as e:
        return f"Web search error: {str(e)}"


# ================================
# Market Insights Analyst Agent (CrewAI)
# ================================

class MarketInsightsAnalyst:
    """
    AI Agent specialized in real estate market analysis using CrewAI
    
    Capabilities:
    - Property valuation using multiple data sources
    - Multi-source price consensus (Zillow, Redfin, StreetEasy)
    - Market trend analysis with web search
    - Investment potential assessment
    - Rental income estimation
    - Risk and opportunity identification
    
    Data Sources:
    - ATTOM API (property data, AVM, comparables, sales history)
    - Bright Data Web Scraping (Zillow, Redfin, StreetEasy)
    - Tavily Web Search (market trends, neighborhood info)
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
        self.attom = AttomAPIClient()
        
        # Initialize Gemini 2.5 Flash LLM for CrewAI
        # CrewAI uses LiteLLM routing internally
        # Format: gemini/model-name (as per LiteLLM docs)
        from crewai import LLM
        
        self.llm = LLM(
            model="gemini/gemini-2.5-flash",  # LiteLLM format for Gemini 2.5 Flash
            api_key=os.getenv('GEMINI_API_KEY'),  # LiteLLM expects GEMINI_API_KEY
            temperature=0.1
        )
        
        # Agent persona and expertise
        self.role = "Senior Real Estate Market Analyst"
        self.expertise = """You are a senior real estate market analyst with 20 years of experience 
        in residential property valuation, market trend analysis, and investment assessment. 
        You specialize in analyzing comparable sales, market conditions, and investment potential 
        to provide data-driven insights for real estate professionals. You have access to ATTOM 
        property data, multi-source web scraping (Zillow, Redfin, StreetEasy), and web research tools."""
        
        # Build tools list (ATTOM + Web Scraping + optional Tavily)
        tools = [
            search_property_data,
            get_comparable_properties,
            get_avm_estimate,
            scrape_property_data  # NEW: Multi-source web scraping
        ]
        
        # Add Tavily web search tool if API key is available
        if os.getenv('TAVILY_API_KEY'):
            tools.append(tavily_search_tool)
        
        # Create CrewAI agent
        self.agent = Agent(
            role=self.role,
            goal="Analyze property market data from multiple sources and provide comprehensive investment insights",
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
1. Use the ATTOM Property Search tool to find official property data
2. Use the Multi-Source Property Scraping tool to get current market prices from Zillow, Redfin, and StreetEasy
3. Use the ATTOM AVM Estimate tool to get automated valuation
4. Use the ATTOM Comparables tool to find similar properties
5. If web search is available, research local market trends and neighborhood info
6. Analyze all data from multiple sources and provide:
   - Price estimate with confidence level and reasoning
   - Market trend analysis (direction, appreciation, demand, inventory)
   - Investment analysis (score 1-100, rental potential, cap rate from RAM, risks, opportunities)
   - Executive summary with actionable insights

Provide your analysis in valid JSON format with the following structure:
- price_estimate (object with estimated_value, confidence, value_range_low, value_range_high, reasoning)
- market_trend (object with trend_direction, appreciation_rate, days_on_market_avg, inventory_level, buyer_demand, insights)
- investment_analysis (object with investment_score 1-100, rental_potential, estimated_rental_income, cap_rate, appreciation_potential, risk_factors array, opportunities array)
- comparable_properties (empty array for now)
- summary (executive summary string)

Return ONLY valid JSON matching the MarketInsights schema. Be data-driven and specific.
"""
            
            task = Task(
                description=task_description,
                agent=self.agent,
                expected_output="Valid JSON object with comprehensive market analysis matching MarketInsights schema"
            )
            
            # Create crew and execute
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            print(f"[CrewAI] Starting market analysis for: {address}")
            print(f"[DEBUG] About to call crew.kickoff()")
            
            result = crew.kickoff(inputs={'address': address})
            
            print(f"[DEBUG] crew.kickoff() completed successfully")
            print(f"[DEBUG] Result type: {type(result)}")
            
            # Parse result
            result_text = str(result).strip()
            
            # DEBUG: Log raw result
            print(f"[DEBUG] Raw CrewAI result (first 500 chars): {result_text[:500]}")
            
            # Extract JSON from markdown code blocks using regex
            import re
            json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1).strip()
                print(f"[DEBUG] Extracted from markdown code block")
            else:
                # Try to find JSON without markdown (look for { to })
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result_text = json_match.group(0).strip()
                    print(f"[DEBUG] Extracted raw JSON object")
                else:
                    print(f"[DEBUG] No JSON pattern found in result")
            
            result_text = result_text.strip()
            print(f"[DEBUG] Final JSON to parse (first 300 chars): {result_text[:300]}")
            
            # Parse JSON
            insights_data = json.loads(result_text)
            
            print(f"[DEBUG] Parsed JSON successfully, sanitizing data types...")
            
            # Sanitize data to match schema types
            insights_data = self._sanitize_market_data(insights_data)
            
            # Validate against schema
            validated = MarketInsights(**insights_data)
            
            print(f"[DEBUG] Validation successful!")
            
            return validated.model_dump()
            
        except Exception as e:
            print(f"CrewAI market analysis error: {str(e)}")
            # Return fallback data
            return self._generate_fallback_insights(property_data, str(e))
    
    def _sanitize_market_data(self, data: Dict) -> Dict:
        """
        Sanitize market data to match schema types.
        Converts human-readable strings to proper numeric types.
        """
        import re
        
        def parse_number(value):
            """Extract number from string like '$8,530' or '3.5%' or 'Moderate'"""
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return value
            if isinstance(value, str):
                # Handle non-numeric strings
                lower_val = value.lower()
                if any(word in lower_val for word in ['unknown', 'undeterminable', 'n/a', 'none', 'null']):
                    return None
                # Remove $, %, commas, and extract first number
                cleaned = re.sub(r'[,$%]', '', value)
                numbers = re.findall(r'-?\d+\.?\d*', cleaned)
                if numbers:
                    try:
                        return float(numbers[0]) if '.' in numbers[0] else int(numbers[0])
                    except:
                        pass
            return None
        
        # Sanitize price_estimate
        if 'price_estimate' in data and data['price_estimate']:
            pe = data['price_estimate']
            if pe.get('estimated_value') is None:
                pe['estimated_value'] = 0
            if pe.get('value_range_low') is None:
                pe['value_range_low'] = 0
            if pe.get('value_range_high') is None:
                pe['value_range_high'] = 0
        
        # Sanitize market_trend
        if 'market_trend' in data and data['market_trend']:
            mt = data['market_trend']
            mt['appreciation_rate'] = parse_number(mt.get('appreciation_rate'))
            mt['days_on_market_avg'] = parse_number(mt.get('days_on_market_avg'))
        
        # Sanitize investment_analysis
        if 'investment_analysis' in data and data['investment_analysis']:
            ia = data['investment_analysis']
            ia['estimated_rental_income'] = parse_number(ia.get('estimated_rental_income'))
            ia['cap_rate'] = parse_number(ia.get('cap_rate'))
        
        return data
    
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
        Generate basic insights when external data sources are unavailable
        
        Used when:
        - ATTOM API is unavailable
        - Web scraping fails
        - Property not found in databases
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
                'reasoning': f'Estimate based on square footage only. External data sources unavailable: {error_message}'
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
            'summary': f'Limited market analysis available. {bedrooms} bed, {bathrooms} bath property estimated at ${estimated_value:,}. Full analysis requires multi-source property data.'
        }
