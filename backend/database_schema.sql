-- AI Floor Plan and Market Insights - Database Schema
-- Execute this in Supabase SQL Editor to create all necessary tables and policies

-- ================================
-- TABLES
-- ================================

-- Users table (Supabase Auth integration)
-- Note: Supabase Auth handles the auth.users table automatically
-- This table extends user data
CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    agent_license_number TEXT,
    phone TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Properties table - Central table for listings
CREATE TABLE IF NOT EXISTS public.properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    
    -- Input method
    input_type TEXT NOT NULL CHECK (input_type IN ('upload', 'search')),
    
    -- Status workflow
    status TEXT NOT NULL DEFAULT 'processing' 
        CHECK (status IN ('processing', 'parsing_complete', 'enrichment_complete', 'complete', 'failed')),
    
    -- Floor plan data
    image_url TEXT,
    image_storage_path TEXT,
    
    -- Extracted data from AI Agent #1 (Floor Plan Analyst)
    extracted_data JSONB DEFAULT '{}'::jsonb,
    -- Expected structure:
    -- {
    --   "address": "string",
    --   "bedrooms": number,
    --   "bathrooms": number,
    --   "square_footage": number,
    --   "features": ["windows", "doors", "closets"],
    --   "rooms": [{"type": "bedroom", "dimensions": "12x14"}]
    -- }
    
    -- Generated listing text from AI Agent #3 (Listing Copywriter)
    generated_listing_text TEXT,
    
    -- Shareable report URL token
    share_token TEXT UNIQUE,
    share_token_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Market insights table - Linked to properties
CREATE TABLE IF NOT EXISTS public.market_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL UNIQUE,
    
    -- CoreLogic identifiers
    clip_id TEXT,
    
    -- CoreLogic data from AI Agent #2 (Market Insights Analyst)
    corelogic_data JSONB DEFAULT '{}'::jsonb,
    -- Expected structure:
    -- {
    --   "property_detail": {...},
    --   "ownership": {...},
    --   "tax_assessment": {...},
    --   "last_sale": {...}
    -- }
    
    -- Comparables data
    comparables JSONB DEFAULT '[]'::jsonb,
    -- Expected structure: array of comparable properties
    -- [
    --   {
    --     "address": "string",
    --     "sale_date": "date",
    --     "sale_price": number,
    --     "bedrooms": number,
    --     "bathrooms": number,
    --     "square_footage": number,
    --     "distance_miles": number
    --   }
    -- ]
    
    -- AI-generated price suggestion
    suggested_price_range TEXT,
    -- Expected format: "$450,000 - $475,000"
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- View analytics table - Track report views
CREATE TABLE IF NOT EXISTS public.view_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL,
    
    -- View tracking
    viewed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_agent TEXT,
    ip_address INET,
    
    -- Geographic data (optional)
    country TEXT,
    city TEXT,
    
    -- Session tracking
    session_id TEXT
);

-- ================================
-- INDEXES FOR PERFORMANCE
-- ================================

CREATE INDEX IF NOT EXISTS idx_properties_agent_id ON public.properties(agent_id);
CREATE INDEX IF NOT EXISTS idx_properties_status ON public.properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_share_token ON public.properties(share_token);
CREATE INDEX IF NOT EXISTS idx_properties_created_at ON public.properties(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_market_insights_property_id ON public.market_insights(property_id);
CREATE INDEX IF NOT EXISTS idx_view_analytics_property_id ON public.view_analytics(property_id);
CREATE INDEX IF NOT EXISTS idx_view_analytics_viewed_at ON public.view_analytics(viewed_at DESC);

-- ================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ================================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.view_analytics ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view own profile"
    ON public.users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.users FOR UPDATE
    USING (auth.uid() = id);

-- Properties table policies
CREATE POLICY "Agents can view own properties"
    ON public.properties FOR SELECT
    USING (auth.uid() = agent_id);

CREATE POLICY "Agents can insert own properties"
    ON public.properties FOR INSERT
    WITH CHECK (auth.uid() = agent_id);

CREATE POLICY "Agents can update own properties"
    ON public.properties FOR UPDATE
    USING (auth.uid() = agent_id);

CREATE POLICY "Agents can delete own properties"
    ON public.properties FOR DELETE
    USING (auth.uid() = agent_id);

CREATE POLICY "Public can view properties via valid share token"
    ON public.properties FOR SELECT
    USING (
        share_token IS NOT NULL 
        AND share_token_expires_at > NOW()
    );

-- Market insights table policies
CREATE POLICY "Agents can view insights for own properties"
    ON public.market_insights FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.properties
            WHERE properties.id = market_insights.property_id
            AND properties.agent_id = auth.uid()
        )
    );

CREATE POLICY "Service role can manage all market insights"
    ON public.market_insights FOR ALL
    USING (true);

-- View analytics table policies
CREATE POLICY "Agents can view analytics for own properties"
    ON public.view_analytics FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.properties
            WHERE properties.id = view_analytics.property_id
            AND properties.agent_id = auth.uid()
        )
    );

CREATE POLICY "Public can insert view analytics"
    ON public.view_analytics FOR INSERT
    WITH CHECK (true);

-- ================================
-- STORAGE BUCKET FOR FLOOR PLANS
-- ================================

-- Create storage bucket (run this in Supabase Dashboard -> Storage)
-- Bucket name: 'floor-plans'
-- Public: false
-- Allowed MIME types: image/png, image/jpeg, image/jpg, application/pdf
-- Max file size: 10MB

-- Storage policies (apply in Supabase Dashboard)
-- 1. "Agents can upload floor plans"
--    Operation: INSERT
--    Policy: (bucket_id = 'floor-plans' AND auth.uid() IS NOT NULL)
--
-- 2. "Agents can view own uploads"
--    Operation: SELECT
--    Policy: (bucket_id = 'floor-plans' AND auth.uid() IS NOT NULL)
--
-- 3. "Agents can delete own uploads"
--    Operation: DELETE
--    Policy: (bucket_id = 'floor-plans' AND auth.uid() IS NOT NULL)

-- ================================
-- FUNCTIONS & TRIGGERS
-- ================================

-- Function to update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to properties table
CREATE TRIGGER update_properties_updated_at
    BEFORE UPDATE ON public.properties
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to market_insights table
CREATE TRIGGER update_market_insights_updated_at
    BEFORE UPDATE ON public.market_insights
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ================================
-- GRANTS (if needed)
-- ================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO anon, authenticated;

-- Grant table access to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON public.users TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.properties TO authenticated;
GRANT SELECT ON public.market_insights TO authenticated;
GRANT SELECT, INSERT ON public.view_analytics TO authenticated;

-- Grant anonymous users access to public endpoints
GRANT SELECT ON public.properties TO anon;
GRANT INSERT ON public.view_analytics TO anon;

-- ================================
-- SAMPLE DATA (Optional - for testing)
-- ================================

-- Insert sample agent user (after creating user via Supabase Auth)
-- INSERT INTO public.users (id, email, full_name)
-- VALUES ('user-uuid-here', 'agent@example.com', 'Jane Smith');

COMMENT ON TABLE public.properties IS 'Central table storing all property listings with AI-extracted data';
COMMENT ON TABLE public.market_insights IS 'Market data and price analysis from CoreLogic API';
COMMENT ON TABLE public.view_analytics IS 'Tracking views of shared property reports';
