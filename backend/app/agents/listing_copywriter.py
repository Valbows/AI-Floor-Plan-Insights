"""
Listing Copywriter Agent
AI Agent #3 - Generates MLS-ready listing copy and marketing materials
Uses Gemini AI to create compelling property descriptions
"""

import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from pydantic import BaseModel, Field, field_validator

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))


# ================================
# Structured Output Schemas
# ================================

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
# Listing Copywriter Agent
# ================================

class ListingCopywriter:
    """
    AI Agent specialized in real estate copywriting
    
    Capabilities:
    - MLS listing descriptions
    - Property highlights and features
    - Social media captions
    - Email campaign copy
    - SEO keyword optimization
    - Tone customization (luxury, family-friendly, investor-focused)
    
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
        """Initialize Listing Copywriter"""
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Agent persona and expertise
        self.role = "Professional Real Estate Copywriter"
        self.expertise = """You are an award-winning real estate copywriter with 15 years of experience 
        creating high-converting property listings. You specialize in MLS descriptions, luxury marketing, 
        and digital campaigns. Your copy is known for being compelling, SEO-optimized, and results-driven, 
        with a proven track record of generating buyer interest and faster sales."""
    
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
            
            # Build comprehensive prompt
            prompt = self._build_prompt(
                address=address,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                sqft=sqft,
                features=features,
                layout=layout,
                price=price_estimate.get('estimated_value', 0),
                market_trend=market_trend.get('trend_direction', 'stable'),
                investment_score=investment.get('investment_score', 0),
                tone=tone,
                target_audience=target_audience
            )
            
            # Generate listing copy
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=ListingCopy
                )
            )
            
            # Parse and return structured copy
            import json
            listing_copy = json.loads(response.text)
            
            return listing_copy
            
        except Exception as e:
            print(f"Listing generation error: {str(e)}")
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
