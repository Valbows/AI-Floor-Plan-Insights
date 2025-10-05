"""
Listing Copywriter Agent
AI Agent #3 - Generates MLS-ready listing copy and marketing materials
Uses CrewAI with Gemini AI + Web Search for compelling property descriptions
"""

import os
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from crewai import Agent, Task, Crew
from crewai_tools import tool, SerperDevTool
from langchain_google_genai import ChatGoogleGenerativeAI

class ListingCopy(BaseModel):
    """MLS-ready listing copy"""
    headline: str = Field(description="Attention-grabbing headline (60 chars max)")
    description: str = Field(description="Full property description (500-800 words)")
    highlights: list[str] = Field(description="Key selling points (5-8 bullet points)")
    call_to_action: str = Field(description="Compelling CTA")
    social_media_caption: Optional[str] = Field(default="", description="Instagram/Facebook caption (150 chars)")
    email_subject: Optional[str] = Field(default="", description="Email campaign subject line")
    seo_keywords: list[str] = Field(description="SEO keywords for online listings")
    
    @field_validator('headline', 'description', 'call_to_action', 'social_media_caption', 'email_subject', mode='before')
    @classmethod
    def validate_strings(cls, v):
        """Convert None to empty string"""
        return v if v is not None else ""


# ================================
# CrewAI Tools for Copywriting
# ================================

@tool("Neighborhood Research")
def research_neighborhood(location: str) -> str:
    """
    Research neighborhood features, amenities, and selling points.
    
    Args:
        location: City, neighborhood, or zip code
    
    Returns:
        str: Neighborhood highlights, schools, amenities, local attractions
    """
    # This would typically use web search or local database
    # For now, return a template
    return f"""Neighborhood research for {location}:
- Well-established residential area
- Highly rated schools nearby
- Close to shopping, dining, and entertainment
- Easy access to major highways
- Family-friendly community with parks
- Growing property values in the area"""


# ================================
# Listing Copywriter Agent (CrewAI)
# ================================

class ListingCopywriter:
    """
    AI Agent specialized in real estate copywriting using CrewAI
    
    Capabilities:
    - MLS listing descriptions
    - Property highlights and features
    - Social media captions (Instagram, Facebook, Twitter, LinkedIn)
    - Email campaign copy
    - SEO keyword optimization
    - Tone customization (luxury, family-friendly, investor-focused)
    - Neighborhood research via web search
    
    Inputs:
    - Floor plan data (Agent #1)
    - Market insights (Agent #2)
    - Target audience preferences
    
    Usage:
        writer = ListingCopywriter()
        listing = writer.generate_listing(
            property_data={...},
            market_insights={...},
            tone="luxury"
        )
    """
    
    def __init__(self):
        """Initialize Listing Copywriter with CrewAI"""
        # Initialize Gemini LLM for CrewAI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini/gemini-2.0-flash-exp",
            google_api_key=os.getenv('GOOGLE_GEMINI_API_KEY'),
            temperature=0.7  # Higher temperature for creative writing
        )
        
        # Agent persona and expertise
        self.role = "Professional Real Estate Copywriter"
        self.expertise = """You are an award-winning real estate copywriter with 15 years of experience 
        creating high-converting property listings. You specialize in MLS descriptions, luxury marketing, 
        and digital campaigns. Your copy is known for being compelling, SEO-optimized, and results-driven, 
        with a proven track record of generating buyer interest and faster sales."""
        
        # Create web search tool (optional - requires Serper API key)
        self.search_tool = SerperDevTool() if os.getenv('SERPER_API_KEY') else None
        
        # Build tools list
        tools = [research_neighborhood]
        if self.search_tool:
            tools.append(self.search_tool)
        
        # Create CrewAI agent
        self.agent = Agent(
            role=self.role,
            goal="Create compelling, SEO-optimized property listings that convert viewers into buyers",
            backstory=self.expertise,
            tools=tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def generate_listing(self, property_data: Dict[str, Any], 
                        market_insights: Dict[str, Any],
                        tone: str = "professional",
                        target_audience: str = "home_buyers") -> Dict[str, Any]:
        """
        Generate complete listing copy for a property
        
        Args:
            property_data: Floor plan data from Agent #1
                {
                    "address": "123 Main St, Miami, FL",
                    "bedrooms": 3,
                    "bathrooms": 2.0,
                    "square_footage": 1500,
                    "features": ["balcony", "walk-in closet"],
                    "layout_type": "Open concept",
                    "rooms": [...]
                }
            
            market_insights: Market analysis from Agent #2
                {
                    "price_estimate": {...},
                    "market_trend": {...},
                    "investment_analysis": {...}
                }
            
            tone: Writing tone
                - "professional" (default): Balanced, informative
                - "luxury": Upscale, aspirational language
                - "family": Warm, family-focused
                - "investor": ROI-focused, data-driven
                - "modern": Contemporary, minimalist
            
            target_audience: Primary audience
                - "home_buyers" (default): First-time or move-up buyers
                - "investors": Real estate investors
                - "luxury_buyers": High-net-worth individuals
                - "families": Families with children
                - "downsizers": Empty nesters, retirees
        
        Returns:
            {
                "headline": "Stunning 3BR Home with Modern Upgrades",
                "description": "Full MLS description...",
                "highlights": ["Open concept layout", ...],
                "call_to_action": "Schedule your private showing today!",
                "social_media_caption": "Your dream home awaits...",
                "email_subject": "New Listing: 3BR in Prime Location",
                "seo_keywords": ["3 bedroom home", "miami real estate", ...]
            }
        
        Raises:
            Exception: If content generation fails
        """
        try:
            # Extract key property details
            address = property_data.get('address', 'Beautiful Property')
            bedrooms = property_data.get('bedrooms', 0)
            bathrooms = property_data.get('bathrooms', 0)
            sqft = property_data.get('square_footage', 0)
            features = property_data.get('features', [])
            layout = property_data.get('layout_type', '')
            
            # Extract market insights
            price_estimate = market_insights.get('price_estimate', {})
            market_trend = market_insights.get('market_trend', {})
            investment = market_insights.get('investment_analysis', {})
            
            # Create comprehensive task for CrewAI
            task_description = f"""
Create compelling, MLS-ready listing copy for the following property:

PROPERTY DETAILS:
- Address: {address}
- Bedrooms: {bedrooms}
- Bathrooms: {bathrooms}
- Square Footage: {sqft:,} sq ft
- Layout: {layout}
- Features: {', '.join(features) if features else 'Standard features'}

MARKET POSITIONING:
- Estimated Value: ${price_estimate.get('estimated_value', 0):,}
- Market Trend: {market_trend.get('trend_direction', 'stable')}
- Investment Score: {investment.get('investment_score', 0)}/100

TONE: {tone.upper()}
TARGET AUDIENCE: {target_audience.upper()}

REQUIREMENTS:
1. HEADLINE: Create an attention-grabbing headline (max 60 characters)
2. DESCRIPTION: Write a compelling 500-800 word property description that:
   - Starts with a strong opening sentence
   - Highlights unique selling points
   - Describes each room and key features
   - Paints a lifestyle picture
   - Ends with urgency or exclusivity
   - Uses {tone} tone appropriate for {target_audience}

3. HIGHLIGHTS: List 5-8 specific, benefit-focused bullet points
4. CALL TO ACTION: Create a compelling CTA that drives immediate action
5. SOCIAL MEDIA CAPTION: Write a 150-character caption for Instagram/Facebook
6. EMAIL SUBJECT: Write an email subject line (under 60 chars)
7. SEO KEYWORDS: List 8-12 relevant SEO keywords

WRITING GUIDELINES:
- Be specific and concrete (use numbers and details)
- Use power words that evoke emotion
- Focus on benefits, not just features
- Create visual imagery
- Use active voice
- Include location benefits from neighborhood research

Use available tools to enhance the copy (neighborhood research, web search for local amenities).

Respond with complete listing copy in JSON format matching the ListingCopy schema.
"""
            
            task = Task(
                description=task_description,
                agent=self.agent,
                expected_output="JSON object with complete listing copy"
            )
            
            # Create crew and execute
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            print(f"[CrewAI] Generating listing copy for: {address}")
            result = crew.kickoff()
            
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
            listing_copy = json.loads(result_text)
            
            # Validate against schema
            validated = ListingCopy(**listing_copy)
            
            return validated.model_dump()
            
        except Exception as e:
            print(f"CrewAI listing generation error: {str(e)}")
            # Return fallback copy
            return self._generate_fallback_listing(property_data)
    
    def _build_prompt(self, address: str, bedrooms: int, bathrooms: float, sqft: int,
                     features: list, layout: str, price: int, market_trend: str,
                     investment_score: int, tone: str, target_audience: str) -> str:
        """Build comprehensive prompt for listing generation"""
        
        # Tone guidelines
        tone_guidelines = {
            "professional": "Balanced, informative, and trustworthy. Focus on facts and benefits.",
            "luxury": "Sophisticated, aspirational, and exclusive. Use elegant language and emphasize premium features.",
            "family": "Warm, welcoming, and community-focused. Highlight family-friendly amenities and safety.",
            "investor": "Data-driven, ROI-focused, and analytical. Emphasize cash flow, appreciation, and returns.",
            "modern": "Contemporary, minimalist, and design-forward. Use clean language and focus on aesthetics."
        }
        
        # Audience focus
        audience_focus = {
            "home_buyers": "Emphasize lifestyle, comfort, and move-in ready features.",
            "investors": "Highlight rental potential, appreciation, and market position.",
            "luxury_buyers": "Focus on exclusivity, craftsmanship, and prestige.",
            "families": "Emphasize schools, safety, space, and community.",
            "downsizers": "Highlight low maintenance, accessibility, and lifestyle simplification."
        }
        
        prompt = f"""
{self.expertise}

LISTING COPY REQUEST:

PROPERTY DETAILS:
- Address: {address}
- Bedrooms: {bedrooms}
- Bathrooms: {bathrooms}
- Square Footage: {sqft:,} sq ft
- Layout: {layout}
- Features: {', '.join(features) if features else 'Standard features'}

MARKET POSITIONING:
- Estimated Value: ${price:,}
- Market Trend: {market_trend}
- Investment Score: {investment_score}/100

TONE: {tone.upper()}
{tone_guidelines.get(tone, tone_guidelines['professional'])}

TARGET AUDIENCE: {target_audience.upper()}
{audience_focus.get(target_audience, audience_focus['home_buyers'])}

REQUIREMENTS:
1. HEADLINE: Create an attention-grabbing headline (max 60 characters) that captures the property's best feature
2. DESCRIPTION: Write a compelling 500-800 word property description that:
   - Starts with a strong opening sentence
   - Highlights unique selling points
   - Describes each room and key features
   - Paints a lifestyle picture
   - Ends with urgency or exclusivity
   - Uses descriptive, vivid language
   - Avoids clichés and generic phrases
   - Follows {tone} tone guidelines

3. HIGHLIGHTS: List 5-8 key bullet points that are specific and benefit-focused (not just "3 bedrooms")
4. CALL TO ACTION: Create a compelling CTA that drives immediate action
5. SOCIAL MEDIA CAPTION: Write a 150-character caption for Instagram/Facebook
6. EMAIL SUBJECT: Write an email subject line that drives opens (under 60 chars)
7. SEO KEYWORDS: List 8-12 relevant SEO keywords for online listings (location, features, property type)

WRITING GUIDELINES:
- Be specific and concrete (not "spacious" but "1,500 sq ft of living space")
- Use power words that evoke emotion
- Focus on benefits, not just features
- Create visual imagery
- Use active voice
- Vary sentence length for rhythm
- Include location benefits if known

Respond with complete, MLS-ready listing copy in JSON format following the ListingCopy schema.
"""
        
        return prompt
    
    def _generate_fallback_listing(self, property_data: Dict) -> Dict[str, Any]:
        """
        Generate basic listing copy when AI fails
        
        Returns generic but functional copy
        """
        address = property_data.get('address', 'Prime Location')
        bedrooms = property_data.get('bedrooms', 0)
        bathrooms = property_data.get('bathrooms', 0)
        sqft = property_data.get('square_footage', 0)
        features = property_data.get('features', [])
        
        return {
            'headline': f'{bedrooms} Bed, {bathrooms} Bath Home for Sale',
            'description': f"""
Welcome to this {bedrooms} bedroom, {bathrooms} bathroom property offering {sqft:,} square feet of comfortable living space. 

This home features {', '.join(features[:3]) if features else 'quality finishes throughout'} and provides an excellent opportunity for buyers seeking a move-in ready property.

The floor plan offers {bedrooms} bedrooms and {bathrooms} bathrooms, perfect for those seeking space and functionality. Located in a desirable area with convenient access to local amenities, schools, and shopping.

Don't miss this opportunity to own a wonderful property. Contact us today to schedule your private showing and see all this home has to offer.
""".strip(),
            'highlights': [
                f'{bedrooms} spacious bedrooms',
                f'{bathrooms} bathrooms',
                f'{sqft:,} square feet of living space',
                'Move-in ready condition',
                'Convenient location',
                'Quality construction'
            ],
            'call_to_action': 'Schedule your private showing today!',
            'social_media_caption': f'New listing: {bedrooms}BR/{bathrooms}BA home now available! {sqft:,} sq ft of living space. Contact us for details.',
            'email_subject': f'New Listing Alert: {bedrooms}BR Home Available',
            'seo_keywords': [
                f'{bedrooms} bedroom home',
                f'{bathrooms} bathroom property',
                'real estate for sale',
                'move-in ready',
                'residential property',
                f'{sqft} square feet'
            ]
        }
    
    def generate_social_variants(self, listing_copy: Dict[str, Any], 
                                platforms: list[str] = ['instagram', 'facebook', 'twitter']) -> Dict[str, str]:
        """
        Generate platform-specific social media variations
        
        Args:
            listing_copy: Generated listing from generate_listing()
            platforms: List of platforms (instagram, facebook, twitter, linkedin)
        
        Returns:
            {
                "instagram": "Caption optimized for Instagram...",
                "facebook": "Caption optimized for Facebook...",
                "twitter": "Tweet-length copy...",
                "linkedin": "Professional caption..."
            }
        """
        # Platform-specific variations
        variants = {}
        
        base_caption = listing_copy.get('social_media_caption', '')
        headline = listing_copy.get('headline', '')
        highlights = listing_copy.get('highlights', [])
        
        if 'instagram' in platforms:
            variants['instagram'] = f"{headline}\n\n{base_caption}\n\n✨ {highlights[0] if highlights else 'Prime location'}\n🏡 DM for details or link in bio!"
        
        if 'facebook' in platforms:
            variants['facebook'] = f"{headline}\n\n{base_caption}\n\nKey Features:\n" + '\n'.join([f'✓ {h}' for h in highlights[:3]]) + "\n\nClick to learn more or message us to schedule a showing!"
        
        if 'twitter' in platforms:
            # Twitter/X has 280 char limit
            variants['twitter'] = f"🏡 NEW LISTING: {headline}\n\n{highlights[0] if highlights else 'Move-in ready'}\n\nDM for details!"
        
        if 'linkedin' in platforms:
            variants['linkedin'] = f"New Property Listing: {headline}\n\n{base_caption}\n\nExcellent investment opportunity in a prime location. Contact me for more information."
        
        return variants
