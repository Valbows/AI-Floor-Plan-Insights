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
from crewai.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient
from app.clients.attom_client import AttomAPIClient
import asyncio
import logging
import time

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
    price_per_sqft: Optional[float] = Field(default=None, description="Estimated price per square foot")


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


@tool("ATTOM Sales Trends")
def get_market_sales_trends(zip_code: str, interval: str = "monthly") -> str:
    """
    Get comprehensive sales trend data for market analysis and comp set building.
    
    ⚠️ NOTE: This endpoint may require ATTOM premium subscription (not in free trial).
    If unavailable, use ATTOM Property Search + Comparables instead.
    
    PRIMARY DATA SOURCE for:
    - Price per square foot (for regression models)
    - Median/average sale prices (for comparables)
    - Market velocity (days on market trends)
    - Year-over-year appreciation rates
    - Historical pricing data (2 years)
    
    Args:
        zip_code: ZIP code for market area (required)
        interval: 'monthly', 'quarterly', or 'yearly' (default: monthly)
    
    Returns:
        str: JSON with comprehensive market trends OR error message if not available
    
    If this tool returns an error, fall back to:
    1. ATTOM Property Search (get recent sales in area)
    2. ATTOM AVM (automated valuation)
    3. Multi-Source Scraping (Zillow/Redfin estimates)
    """
    try:
        client = AttomAPIClient()
        trends = client.get_sales_trends(zip_code, interval=interval)
        return json.dumps(trends, indent=2)
    except Exception as e:
        # Sales trends is a premium feature - provide helpful error
        return f"❌ ATTOM Sales Trends not available (likely requires premium subscription). Error: {str(e)}\n\n💡 RECOMMENDATION: Use alternative tools:\n1. ATTOM Property Search - Find recent sales in the area\n2. ATTOM AVM - Get automated valuation\n3. Multi-Source Scraping - Get Zillow/Redfin pricing\n4. Tavily Web Search - Research market trends"


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
        to provide data-driven insights for real estate professionals.
        
        DATA STRATEGY (use in this order):
        1. ALWAYS start with ATTOM Sales Trends (2 years of market data, price per sqft, velocity)
        2. Use ATTOM Property Search & AVM for subject property details
        3. Use Multi-Source Scraping (Zillow/Redfin/StreetEasy) as backup if ATTOM has gaps
        4. Use Tavily Web Search for general market research and neighborhood insights
        
        The ATTOM Sales Trends tool is your PRIMARY source for building comp sets and 
        understanding market pricing. Always call it first to establish baseline pricing."""
        
        # Build tools list (prioritized by reliability and data quality)
        tools = [
            # Tier 1: ATTOM API (primary, most reliable)
            get_market_sales_trends,  # NEW: Primary source for market trends and comp data
            search_property_data,
            get_comparable_properties,
            get_avm_estimate,
            # Tier 2: Web scraping (backup when ATTOM has limited data)
            scrape_property_data  # Bright Data multi-source scraping
        ]
        
        # Add Tavily web search tool if API key is available
        if os.getenv('TAVILY_API_KEY'):
            tools.append(tavily_search_tool)
        
        # Create CrewAI agent with strict limits
        self.agent = Agent(
            role=self.role,
            goal="Analyze property market data from multiple sources and provide comprehensive investment insights",
            backstory=self.expertise,
            tools=tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=3,  # Reduce to limit LLM/tool loops
            max_rpm=6    # Safer than free-tier 10 RPM
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
            # Summarize pre-fetched ATTOM bundle when available (reduces need to refetch via tools)
            attom = property_data.get('attom', {}) or {}
            attom_prop = attom.get('property') or {}
            attom_avm = attom.get('avm') or {}
            attom_area = attom.get('area_stats') or {}
            attom_trends_v4 = attom.get('sales_trends_v4') or {}
            attom_trends_zip = attom.get('sales_trends') or {}
            attom_comps = attom.get('comparables') or []
            attom_lines = []
            try:
                if attom_prop:
                    attom_lines.append(f"ATTOM Core: {attom_prop.get('address','N/A')} {attom_prop.get('city','')}, {attom_prop.get('state','')} {attom_prop.get('zip','')}")
                    attom_lines.append(f"Beds/Baths/Sqft: {attom_prop.get('bedrooms','?')}/{attom_prop.get('bathrooms','?')}/{attom_prop.get('square_feet','?')}")
                if attom_avm:
                    attom_lines.append(f"AVM: ${attom_avm.get('estimated_value',0):,} (range ${attom_avm.get('value_range_low',0):,}-${attom_avm.get('value_range_high',0):,})")
                if attom_area:
                    mv = attom_area.get('median_home_value')
                    attom_lines.append(f"Area Median Home Value: ${mv:,}" if mv else "Area stats present")
                if (attom_trends_v4 or attom_trends_zip):
                    attom_lines.append("Sales Trends: available (v4 or ZIP)")
                if attom_comps:
                    attom_lines.append(f"Comparables: {len(attom_comps)} candidates")
            except Exception:
                pass
            attom_summary = "\n".join(attom_lines) if attom_lines else "No ATTOM bundle pre-fetched"

            # Create simplified task for CrewAI (faster execution)
            task_description = f"""
Analyze property at: {address}

Property: {property_data.get('bedrooms', 0)} bed, {property_data.get('bathrooms', 0)} bath, {property_data.get('square_footage', 0)} sqft

INSTRUCTIONS:
1. Try ATTOM tools first (Property Search, AVM, Comparables) - these are fastest
2. If ATTOM fails or has limited data, try Multi-Source Scraping
3. If both fail, use Tavily Web Search for general market info
4. DO NOT retry failed tools - move to next option immediately
5. Stop after getting ANY useful data - don't over-analyze

Pre-Fetched Data (use directly; avoid refetching unless missing):
{attom_summary}

Return JSON with:
- price_estimate: {{estimated_value, confidence, value_range_low, value_range_high, reasoning}}
- market_trend: {{trend_direction, appreciation_rate, days_on_market_avg, inventory_level, buyer_demand, insights}}
- investment_analysis: {{investment_score, rental_potential, estimated_rental_income, cap_rate, appreciation_potential, risk_factors[], opportunities[]}}
- comparable_properties: []
- summary: string

Be concise. If data is unavailable, estimate based on property characteristics and note low confidence.
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

            # One-time retry with short backoff on rate limit/quota
            try:
                result = crew.kickoff(inputs={'address': address})
            except Exception as e:
                em = str(e).lower()
                if any(tok in em for tok in ['ratelimit', 'quota', 'resource_exhausted', '429']):
                    print("[CrewAI] Rate limited, retrying in ~2s...")
                    time.sleep(2)
                    result = crew.kickoff(inputs={'address': address})
                else:
                    raise
            
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

            # Compute price_per_sqft deterministically when sqft is available and field missing
            try:
                if (validated.price_estimate.price_per_sqft is None):
                    sqft = property_data.get('square_footage') or 0
                    if not sqft:
                        # Fallback to ATTOM property/details sizes when present
                        attom = property_data.get('attom', {}) or {}
                        sqft = (
                            (attom.get('property') or {}).get('square_feet')
                            or (((attom.get('details') or {}).get('building') or {}).get('size') or {}).get('universalsize')
                            or 0
                        )
                    est = validated.price_estimate.estimated_value or 0
                    if isinstance(sqft, (int, float)) and sqft > 0 and isinstance(est, (int, float)) and est > 0:
                        ppsf = float(est) / float(sqft)
                        validated.price_estimate.price_per_sqft = round(ppsf, 2)
            except Exception:
                pass
            
            print(f"[DEBUG] Validation successful!")
            
            try:
                if len(validated.comparable_properties) < 3:
                    attom = property_data.get('attom', {}) or {}
                    attom_prop = attom.get('property') or {}
                    city = attom_prop.get('city') or ''
                    state = attom_prop.get('state') or ''
                    zip_code = attom_prop.get('zip') or ''
                    # Build a tavily-only agent to force usage of web search tool
                    tavily_agent = Agent(
                        role="Tavily Web Researcher",
                        goal="Find 3-5 recent comparable sales and return strict JSON",
                        backstory=(
                            "You specialize in using the Tavily search tool to find recent residential comparable sales. "
                            "Return only structured JSON suitable for downstream regression."
                        ),
                        tools=[tavily_search_tool],
                        llm=self.llm,
                        verbose=True,
                        allow_delegation=False,
                        max_iter=2,
                        max_rpm=6,
                    )
                    tf_desc = (
                        f"Using Tavily, find 3-5 RECENT comparable residential sales within ~1 mile of: {address} {city} {state} {zip_code}. "
                        "Prefer last 6-12 months and similar bed/bath/sqft to the subject. "
                        "For each comp, include: address, bedrooms, bathrooms, square_feet, last_sale_price, last_sale_date, listing_url. "
                        "Respond with ONLY a JSON array (no prose, no markdown)."
                    )
                    task2 = Task(
                        description=tf_desc,
                        agent=tavily_agent,
                        expected_output="JSON array of comparable properties"
                    )
                    crew2 = Crew(agents=[tavily_agent], tasks=[task2], verbose=True)
                    try:
                        print("[DEBUG] Tavily Stage A: kickoff")
                        res2 = crew2.kickoff(inputs={'address': address})
                        res2_text = str(res2).strip()
                        res2_raw = res2_text
                        print(f"[DEBUG] Tavily Stage A raw result length: {len(res2_text)}")
                        print(f"[DEBUG] Tavily Stage A raw (first 600): {res2_text[:600]}")
                        import re as _re
                        jm = _re.search(r'```(?:json)?\s*\n?(.*?)\n?```', res2_text, _re.DOTALL)
                        if jm:
                            print("[DEBUG] Tavily Stage A: JSON code block detected")
                            res2_text = jm.group(1).strip()
                        else:
                            jm = _re.search(r'\[.*\]', res2_text, _re.DOTALL)
                            if jm:
                                print("[DEBUG] Tavily Stage A: JSON array detected without markdown")
                                res2_text = jm.group(0).strip()
                        comp_list = json.loads(res2_text)
                        if isinstance(comp_list, list) and comp_list:
                            print(f"[DEBUG] Tavily Stage A: parsed comps count {len(comp_list)}")
                            validated.comparable_properties = comp_list[:5]
                        # If JSON parse produced nothing, try text-based extraction from raw
                        if len(validated.comparable_properties) < 3:
                            text_comps = self._extract_comps_from_text(res2_raw)
                            if text_comps:
                                need = max(0, 5 - len(validated.comparable_properties))
                                validated.comparable_properties = (validated.comparable_properties or []) + text_comps[:need]
                                print(f"[DEBUG] Tavily Stage A (text fallback): merged {min(len(text_comps), need)} comps; total now {len(validated.comparable_properties)}")
                    except Exception:
                        print("[DEBUG] Tavily Stage A: exception during kickoff/parse, continuing to Stage B if needed")
                        pass
                    # If still fewer than 3 comps, try direct Tavily+LLM extraction
                    try:
                        if len(validated.comparable_properties) < 3:
                            subject = {
                                'bedrooms': property_data.get('bedrooms') or (attom_prop.get('bedrooms') if attom_prop else None),
                                'bathrooms': property_data.get('bathrooms') or (attom_prop.get('bathrooms') if attom_prop else None),
                                'square_footage': property_data.get('square_footage') or (attom_prop.get('square_feet') if attom_prop else None),
                            }
                            extra = self._tavily_llm_extract_comps(address, city, state, zip_code, subject)
                            if isinstance(extra, list) and extra:
                                # Merge up to 5 total
                                need = max(0, 5 - len(validated.comparable_properties))
                                validated.comparable_properties = (validated.comparable_properties or []) + extra[:need]
                                print(f"[DEBUG] Tavily Stage B: merged {min(len(extra), need)} comps; total now {len(validated.comparable_properties)}")
                            else:
                                print("[DEBUG] Tavily Stage B: no comps extracted by direct path")
                    except Exception:
                        print("[DEBUG] Tavily Stage B: exception during direct extraction")
                        pass
            except Exception:
                pass

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
        
        # Sanitize price_estimate (coerce $ strings to ints)
        if 'price_estimate' in data and data['price_estimate']:
            pe = data['price_estimate']
            # Coerce numeric fields via parse_number
            ev = parse_number(pe.get('estimated_value'))
            vlow = parse_number(pe.get('value_range_low'))
            vhigh = parse_number(pe.get('value_range_high'))
            ppsf = parse_number(pe.get('price_per_sqft'))
            pe['estimated_value'] = int(ev or 0)
            pe['value_range_low'] = int(vlow or 0)
            pe['value_range_high'] = int(vhigh or 0)
            if ppsf is not None:
                try:
                    pe['price_per_sqft'] = float(ppsf)
                except Exception:
                    pe['price_per_sqft'] = None
        
        # Sanitize market_trend
        if 'market_trend' in data and data['market_trend']:
            mt = data['market_trend']
            mt['appreciation_rate'] = parse_number(mt.get('appreciation_rate'))
            mt['days_on_market_avg'] = parse_number(mt.get('days_on_market_avg'))
        
        # Sanitize investment_analysis (coerce numeric-like strings)
        if 'investment_analysis' in data and data['investment_analysis']:
            ia = data['investment_analysis']
            # Score may be given as string labels; map to numeric
            score = ia.get('investment_score')
            if isinstance(score, str):
                m = score.strip().lower()
                mapping = {
                    'very low': 20,
                    'low': 35,
                    'moderate': 60,
                    'good': 75,
                    'excellent': 90,
                }
                ia['investment_score'] = mapping.get(m, 60)
            elif isinstance(score, (int, float)):
                ia['investment_score'] = int(score)
            else:
                ia['investment_score'] = 60
            ia['estimated_rental_income'] = parse_number(ia.get('estimated_rental_income'))
            ia['cap_rate'] = parse_number(ia.get('cap_rate'))
        
        return data
    
    def _tavily_llm_extract_comps(self, address: str, city: str, state: str, zip_code: str, subject: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback: Use Tavily search + Gemini LLM to extract 3-5 comps as JSON."""
        try:
            tv_key = os.getenv('TAVILY_API_KEY')
            gm_key = os.getenv('GEMINI_API_KEY')
            if not tv_key or not gm_key:
                return []
            client = TavilyClient(api_key=tv_key)
            subj_beds = subject.get('bedrooms')
            subj_baths = subject.get('bathrooms')
            subj_sqft = subject.get('square_footage') or subject.get('square_feet')
            # Focused queries to increase precision
            queries = [
                f"recently sold single family homes within 1 mile of {address} {city} {state} {zip_code} last 12 months",
                f"recent sold homes {city} {state} {zip_code} similar beds baths sqft",
                f"site:redfin.com recently-sold {zip_code}",
                f"site:redfin.com 'Recently Sold' {city} {zip_code}",
                f"site:realtor.com realestateandhomes-search/{zip_code}/show-recently-sold",
                f"site:movoto.com/{state.lower()}/{zip_code}/sold/",
                f"site:zillow.com/homes/for_sale/{zip_code}_rb/ 'sold'"
            ]
            snippets = []
            for q in queries:
                try:
                    r = client.search(q, max_results=10)
                    for it in r.get('results', [])[:5]:
                        snippets.append(
                            f"Title: {it.get('title','')}\nURL: {it.get('url','')}\nContent: {it.get('content','')}\n"
                        )
                except Exception:
                    continue
            if not snippets:
                return []
            ctx = ("\n---\n".join(snippets))[:16000]
            try:
                print(f"[DEBUG] Tavily Stage B ctx length: {len(ctx)}")
                print(f"[DEBUG] Tavily Stage B ctx (first 600): {ctx[:600]}")
            except Exception:
                pass
            llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', google_api_key=gm_key, temperature=0.1)
            prompt = (
                "You are an expert real estate analyst. From the CONTEXT, extract 3-5 recent comparable residential sales near the subject address.\n\n"
                f"Subject address: {address} {city} {state} {zip_code}\n"
                f"Subject features: beds={subj_beds}, baths={subj_baths}, sqft={subj_sqft}\n\n"
                "CONTEXT:\n" + ctx + "\n\n"
                "Return ONLY a JSON array of objects with keys: "
                "address, bedrooms, bathrooms, square_feet, last_sale_price, last_sale_date, listing_url."
            )
            res = llm.invoke(prompt)
            text = getattr(res, 'content', str(res))
            import re as _re
            jm = _re.search(r"\[.*\]", text, _re.DOTALL)
            if not jm:
                # Fallback: parse from the Tavily context snippets directly
                fb = self._extract_comps_from_text(ctx)
                return fb[:5] if fb else []
            arr = json.loads(jm.group(0))
            if isinstance(arr, list):
                return arr[:5]
            return []
        except Exception:
            return []

    def _extract_comps_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Best-effort regex extraction of comparable properties from unstructured text.

        Looks for segments containing Title/URL/Content as produced by Tavily tool output and
        extracts address, bedrooms, bathrooms, square_feet, last_sale_price, last_sale_date, listing_url.
        """
        results: List[Dict[str, Any]] = []
        try:
            import re
            if not text or not isinstance(text, str):
                return results
            # Split into chunks by separators used in Tavily output
            chunks = re.split(r"\n\-\-\-\n|\n\s*\-\-\-\s*\n|\n\-\-\-\s*$", text)
            # Helper to coerce numbers
            def to_int(num_str: str):
                if not num_str:
                    return None
                s = re.sub(r"[^0-9]", "", str(num_str))
                if not s:
                    return None
                try:
                    return int(s)
                except Exception:
                    return None
            def to_float(num_str: str):
                if not num_str:
                    return None
                s = re.sub(r"[^0-9\.]", "", str(num_str))
                if not s:
                    return None
                try:
                    return float(s)
                except Exception:
                    return None
            # Address patterns:
            # 1) number + street + city + state + optional zip
            addr_pat_full = re.compile(r"(\d{1,6}[^\n,]*?,\s*[A-Za-z .\-]+,\s*[A-Z]{2}(?:\s*\d{5})?)")
            # 2) fallback: number + street only (will rely on city/state context)
            addr_pat_street = re.compile(r"(\d{1,6}[^\n,]*?\s+[A-Za-z0-9'\-]+\s*(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Ln|Lane|Ct|Court)\b[^\n,]*)", re.I)
            for ch in chunks:
                ch = ch.strip()
                if len(ch) < 30:
                    continue
                # Extract URL
                url = None
                m = re.search(r"URL:\s*(\S+)", ch)
                if m:
                    url = m.group(1).strip()
                # Extract address from Title or Content
                title_line = None
                mt = re.search(r"Title:\s*(.+)", ch)
                if mt:
                    title_line = mt.group(1).strip()
                address = None
                for source in [title_line, ch]:
                    if not source:
                        continue
                    ma = addr_pat_full.search(source)
                    if ma:
                        address = ma.group(1).strip()
                        break
                    # Try street-only fallback
                    ms = addr_pat_street.search(source)
                    if ms and (address is None):
                        address = ms.group(1).strip()
                # Extract content body (for numeric fields)
                mc = re.search(r"Content:\s*(.*)", ch, re.S)
                content = (mc.group(1).strip() if mc else ch)
                # Beds/Baths/Sqft
                beds = None
                mb = re.search(r"(\d+)\s*(?:bed|beds|bedroom|bedrooms)\b", content, re.I)
                if mb:
                    beds = to_int(mb.group(1))
                baths = None
                mba = re.search(r"(\d+\.?\d*)\s*(?:bath|baths|bathroom|bathrooms)\b", content, re.I)
                if mba:
                    baths = to_float(mba.group(1))
                sqft = None
                msq = re.search(r"([\d,]+)\s*(?:sq\s*ft|sqft|square\s*foot|square\s*feet)\b", content, re.I)
                if msq:
                    sqft = to_int(msq.group(1))
                # Last sale price (multiple heuristics)
                price = None
                mp = re.search(r"last\s+sold\s+for\s*\$([\d,]+)", content, re.I)
                if not mp:
                    mp = re.search(r"sold\s+for\s*\$([\d,]+)", content, re.I)
                if not mp:
                    mp = re.search(r"list\s*price\s*(?:of)?\s*\$([\d,]+)", content, re.I)
                if not mp:
                    # Any dollar amount as a fallback (e.g., aggregator bullets)
                    mp = re.search(r"\$\s*([\d,]+)", content)
                if mp:
                    price = to_int(mp.group(1))
                # Sale date (also support 'SOLD <Mon DD, YYYY>' or 'SOLD <Mon YYYY>')
                sale_date = None
                md = re.search(r"(?:on|in)\s*([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4}|[A-Za-z]{3,9}\s+\d{4})", content, re.I)
                if not md:
                    md = re.search(r"SOLD\s+([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4}|[A-Za-z]{3,9}\s+\d{4})", content, re.I)
                if md:
                    sale_date = md.group(1).strip()
                # Aggregator bullet pattern for sqft between price and address: '... $1,998,000 · 3,430 · 4224 164th St, ...'
                if sqft is None:
                    magg = re.search(r"\$\s*[\d,]+\s*[•·]\s*([\d,]+)\s*[•·]\s*\d{1,6}", content)
                    if magg:
                        cand_sqft = to_int(magg.group(1))
                        # Reasonable sqft bounds
                        if cand_sqft and 400 <= cand_sqft <= 10000:
                            sqft = cand_sqft
                # Build comp
                comp = {
                    'address': address,
                    'bedrooms': beds,
                    'bathrooms': baths,
                    'square_feet': sqft,
                    'last_sale_price': price,
                    'last_sale_date': sale_date,
                    'listing_url': url,
                }
                # Include if we at least have an address and one strong signal (price/date/url/sqft)
                if address and any([price, sale_date, url, sqft]):
                    results.append(comp)
                if len(results) >= 5:
                    break
        except Exception:
            return results
        return results
    
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
        
        # Sanitize error for user-facing reasoning
        safe_error = 'External data sources were temporarily unavailable.'
        try:
            em = str(error_message).lower()
            if 'ratelimit' in em or 'quota' in em or 'resource_exhausted' in em:
                safe_error = 'Temporarily rate-limited by the AI service. Please wait about a minute and retry.'
        except Exception:
            pass

        return {
            'price_estimate': {
                'estimated_value': estimated_value,
                'confidence': 'low',
                'value_range_low': int(estimated_value * 0.85),
                'value_range_high': int(estimated_value * 1.15),
                'reasoning': f'Estimate based on square footage only. {safe_error}',
                'price_per_sqft': round(float(estimated_value) / float(sqft), 2) if isinstance(sqft, (int, float)) and sqft > 0 else None
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
