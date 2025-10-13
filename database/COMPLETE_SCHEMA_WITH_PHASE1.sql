-- ================================================================
-- COMPLETE DATABASE SCHEMA WITH PHASE 1 ENHANCEMENTS
-- Execute this ONCE in a fresh Supabase project
-- Date: October 13, 2025
-- ================================================================

-- This file combines:
-- 1. Base schema (users, properties, market_insights, view_analytics)
-- 2. Phase 1 migration (multi-source data tables)

-- ================================================================
-- PART 1: BASE SCHEMA
-- ================================================================

-- Users table (extends Supabase Auth)
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
    
    -- Extracted data from AI Agent #1
    extracted_data JSONB DEFAULT '{}'::jsonb,
    
    -- Generated listing text from AI Agent #3
    generated_listing_text TEXT,
    
    -- Shareable report URL token
    share_token TEXT UNIQUE,
    share_token_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Market insights table
CREATE TABLE IF NOT EXISTS public.market_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL UNIQUE,
    
    -- CoreLogic identifiers (legacy - being replaced with ATTOM)
    clip_id TEXT,
    
    -- CoreLogic data (legacy)
    corelogic_data JSONB DEFAULT '{}'::jsonb,
    
    -- Comparables data
    comparables JSONB DEFAULT '[]'::jsonb,
    
    -- AI-generated price suggestion
    suggested_price_range TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- View analytics table
CREATE TABLE IF NOT EXISTS public.view_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL,
    
    -- View tracking
    viewed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_agent TEXT,
    ip_address INET,
    
    -- Geographic data
    country TEXT,
    city TEXT,
    
    -- Session tracking
    session_id TEXT
);

-- ================================================================
-- PART 2: PHASE 1 - MULTI-SOURCE DATA TABLES
-- ================================================================

-- 1. ATTOM API Property Cache
CREATE TABLE IF NOT EXISTS public.attom_property_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- ATTOM identifiers
    attom_id BIGINT UNIQUE NOT NULL,
    apn TEXT,
    fips_code TEXT,
    
    -- Address
    address_line1 TEXT NOT NULL,
    address_line2 TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    
    -- Property details
    property_type TEXT,
    bedrooms INTEGER,
    bathrooms NUMERIC(4,2),
    square_feet INTEGER,
    lot_size_sqft INTEGER,
    year_built INTEGER,
    stories INTEGER,
    
    -- Market data
    last_sale_date DATE,
    last_sale_price NUMERIC(12,2),
    last_sale_recording_date DATE,
    
    -- Valuation (AVM)
    avm_value NUMERIC(12,2),
    avm_value_low NUMERIC(12,2),
    avm_value_high NUMERIC(12,2),
    avm_confidence_score NUMERIC(5,2),
    avm_last_updated DATE,
    
    -- Tax assessment
    tax_assessed_value NUMERIC(12,2),
    tax_assessed_year INTEGER,
    tax_amount NUMERIC(10,2),
    
    -- Location
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    
    -- Raw API response
    raw_api_response JSONB,
    
    -- Cache metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days')
);

-- 2. Web Scraping Data
CREATE TABLE IF NOT EXISTS public.web_scraping_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE,
    
    -- Source
    source TEXT NOT NULL CHECK (source IN ('zillow', 'redfin', 'streeteasy')),
    source_url TEXT,
    source_property_id TEXT,
    
    -- Pricing
    listing_price NUMERIC(12,2),
    zestimate NUMERIC(12,2),
    redfin_estimate NUMERIC(12,2),
    price_per_sqft NUMERIC(8,2),
    
    -- Market metrics
    days_on_market INTEGER,
    views_count INTEGER,
    saves_count INTEGER,
    
    -- Property details
    bedrooms INTEGER,
    bathrooms NUMERIC(4,2),
    square_feet INTEGER,
    lot_size_sqft INTEGER,
    year_built INTEGER,
    
    -- Scores
    walk_score INTEGER,
    transit_score INTEGER,
    bike_score INTEGER,
    
    -- Historical data
    price_history JSONB DEFAULT '[]'::jsonb,
    tax_history JSONB DEFAULT '[]'::jsonb,
    amenities JSONB DEFAULT '[]'::jsonb,
    nearby_schools JSONB DEFAULT '[]'::jsonb,
    
    -- Raw data
    raw_scraping_data JSONB,
    
    -- Quality
    data_completeness_score INTEGER CHECK (data_completeness_score BETWEEN 0 AND 100),
    scraping_errors TEXT[],
    
    -- Metadata
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Comparable Properties
CREATE TABLE IF NOT EXISTS public.comparable_properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL,
    
    -- Comparable details
    address TEXT NOT NULL,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    
    -- Property characteristics
    bedrooms INTEGER,
    bathrooms NUMERIC(4,2),
    square_feet INTEGER,
    lot_size_sqft INTEGER,
    year_built INTEGER,
    property_type TEXT,
    
    -- Sale information
    sale_date DATE,
    sale_price NUMERIC(12,2),
    price_per_sqft NUMERIC(8,2),
    
    -- Similarity
    distance_miles NUMERIC(6,2),
    similarity_score INTEGER CHECK (similarity_score BETWEEN 0 AND 100),
    adjustments JSONB,
    
    -- Source
    data_source TEXT NOT NULL CHECK (data_source IN ('attom_api', 'zillow', 'redfin', 'mls')),
    source_id TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Floor Plan Measurements
CREATE TABLE IF NOT EXISTS public.floor_plan_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL UNIQUE,
    
    -- Overall measurements
    total_square_feet INTEGER,
    total_square_feet_confidence NUMERIC(4,2),
    measurement_method TEXT CHECK (measurement_method IN ('ai_estimation', 'labeled_dimensions', 'hybrid')),
    
    -- Room details
    rooms JSONB DEFAULT '[]'::jsonb,
    
    -- Quality metrics
    quality_score INTEGER CHECK (quality_score BETWEEN 0 AND 100),
    quality_factors JSONB,
    
    -- Detected features
    detected_features JSONB DEFAULT '[]'::jsonb,
    
    -- AI model metadata
    model_version TEXT,
    processing_time_seconds NUMERIC(6,2),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Property Analysis History
CREATE TABLE IF NOT EXISTS public.property_analysis_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL,
    
    -- Analysis metadata
    analysis_type TEXT NOT NULL CHECK (analysis_type IN ('floor_plan', 'market_insights', 'listing_copy', 'full_analysis')),
    agent_version TEXT,
    
    -- Data
    input_data JSONB,
    output_data JSONB,
    
    -- Performance
    processing_time_seconds NUMERIC(6,2),
    api_calls_made INTEGER,
    cost_estimate NUMERIC(8,4),
    
    -- Status
    status TEXT NOT NULL CHECK (status IN ('processing', 'completed', 'failed', 'timeout')),
    error_message TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================================================
-- PART 3: ENHANCE market_insights TABLE
-- ================================================================

ALTER TABLE public.market_insights 
    ADD COLUMN IF NOT EXISTS attom_property_id UUID REFERENCES public.attom_property_cache(id),
    ADD COLUMN IF NOT EXISTS agent_analysis_version TEXT DEFAULT 'v2.0',
    
    -- Price estimate
    ADD COLUMN IF NOT EXISTS estimated_value NUMERIC(12,2),
    ADD COLUMN IF NOT EXISTS value_range_low NUMERIC(12,2),
    ADD COLUMN IF NOT EXISTS value_range_high NUMERIC(12,2),
    ADD COLUMN IF NOT EXISTS confidence_level TEXT CHECK (confidence_level IN ('High', 'Medium', 'Low')),
    ADD COLUMN IF NOT EXISTS pricing_reasoning TEXT,
    
    -- Market trend
    ADD COLUMN IF NOT EXISTS market_trend_direction TEXT,
    ADD COLUMN IF NOT EXISTS appreciation_rate NUMERIC(5,2),
    ADD COLUMN IF NOT EXISTS days_on_market_avg INTEGER,
    ADD COLUMN IF NOT EXISTS inventory_level TEXT,
    ADD COLUMN IF NOT EXISTS buyer_demand TEXT,
    ADD COLUMN IF NOT EXISTS market_insights_text TEXT,
    
    -- Investment analysis
    ADD COLUMN IF NOT EXISTS investment_score INTEGER CHECK (investment_score BETWEEN 0 AND 100),
    ADD COLUMN IF NOT EXISTS rental_potential TEXT,
    ADD COLUMN IF NOT EXISTS estimated_rental_income NUMERIC(10,2),
    ADD COLUMN IF NOT EXISTS cap_rate NUMERIC(5,2),
    ADD COLUMN IF NOT EXISTS appreciation_potential TEXT,
    ADD COLUMN IF NOT EXISTS risk_factors JSONB DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS opportunities JSONB DEFAULT '[]'::jsonb,
    
    -- Summary
    ADD COLUMN IF NOT EXISTS analysis_summary TEXT,
    
    -- Data sources
    ADD COLUMN IF NOT EXISTS data_sources JSONB DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS price_consensus NUMERIC(12,2),
    ADD COLUMN IF NOT EXISTS price_sources_count INTEGER,
    ADD COLUMN IF NOT EXISTS data_quality_score INTEGER CHECK (data_quality_score BETWEEN 0 AND 100);

-- ================================================================
-- PART 4: INDEXES
-- ================================================================

-- Base indexes
CREATE INDEX IF NOT EXISTS idx_properties_agent_id ON public.properties(agent_id);
CREATE INDEX IF NOT EXISTS idx_properties_status ON public.properties(status);
CREATE INDEX IF NOT EXISTS idx_properties_share_token ON public.properties(share_token);
CREATE INDEX IF NOT EXISTS idx_properties_created_at ON public.properties(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_market_insights_property_id ON public.market_insights(property_id);
CREATE INDEX IF NOT EXISTS idx_view_analytics_property_id ON public.view_analytics(property_id);
CREATE INDEX IF NOT EXISTS idx_view_analytics_viewed_at ON public.view_analytics(viewed_at DESC);

-- Phase 1 indexes
CREATE INDEX IF NOT EXISTS idx_attom_cache_attom_id ON public.attom_property_cache(attom_id);
CREATE INDEX IF NOT EXISTS idx_attom_cache_address ON public.attom_property_cache(address_line1, city, state, zip_code);
CREATE INDEX IF NOT EXISTS idx_attom_cache_expires_at ON public.attom_property_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_web_scraping_property_id ON public.web_scraping_data(property_id);
CREATE INDEX IF NOT EXISTS idx_web_scraping_source ON public.web_scraping_data(source);
CREATE INDEX IF NOT EXISTS idx_web_scraping_scraped_at ON public.web_scraping_data(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_comparables_property_id ON public.comparable_properties(property_id);
CREATE INDEX IF NOT EXISTS idx_comparables_similarity ON public.comparable_properties(similarity_score DESC);
CREATE INDEX IF NOT EXISTS idx_comparables_sale_date ON public.comparable_properties(sale_date DESC);
CREATE INDEX IF NOT EXISTS idx_floor_plan_measurements_property_id ON public.floor_plan_measurements(property_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_property_id ON public.property_analysis_history(property_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_type ON public.property_analysis_history(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at ON public.property_analysis_history(created_at DESC);

-- ================================================================
-- PART 5: ROW LEVEL SECURITY
-- ================================================================

-- Enable RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.view_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.attom_property_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.web_scraping_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comparable_properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.floor_plan_measurements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.property_analysis_history ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users can view own profile"
    ON public.users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.users FOR UPDATE
    USING (auth.uid() = id);

-- Properties policies
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

-- Market insights policies
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

-- View analytics policies
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

-- ATTOM cache policies
CREATE POLICY "Service role can manage ATTOM cache"
    ON public.attom_property_cache FOR ALL
    USING (true);

-- Web scraping policies
CREATE POLICY "Service role can manage web scraping data"
    ON public.web_scraping_data FOR ALL
    USING (true);

CREATE POLICY "Agents can view scraping data for own properties"
    ON public.web_scraping_data FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.properties
            WHERE properties.id = web_scraping_data.property_id
            AND properties.agent_id = auth.uid()
        )
    );

-- Comparables policies
CREATE POLICY "Service role can manage comparables"
    ON public.comparable_properties FOR ALL
    USING (true);

CREATE POLICY "Agents can view comparables for own properties"
    ON public.comparable_properties FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.properties
            WHERE properties.id = comparable_properties.property_id
            AND properties.agent_id = auth.uid()
        )
    );

-- Floor plan measurements policies
CREATE POLICY "Service role can manage floor plan measurements"
    ON public.floor_plan_measurements FOR ALL
    USING (true);

CREATE POLICY "Agents can view measurements for own properties"
    ON public.floor_plan_measurements FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.properties
            WHERE properties.id = floor_plan_measurements.property_id
            AND properties.agent_id = auth.uid()
        )
    );

-- Analysis history policies
CREATE POLICY "Service role can manage analysis history"
    ON public.property_analysis_history FOR ALL
    USING (true);

CREATE POLICY "Agents can view analysis history for own properties"
    ON public.property_analysis_history FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.properties
            WHERE properties.id = property_analysis_history.property_id
            AND properties.agent_id = auth.uid()
        )
    );

-- ================================================================
-- PART 6: FUNCTIONS & TRIGGERS
-- ================================================================

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_updated_at
    BEFORE UPDATE ON public.properties
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_market_insights_updated_at
    BEFORE UPDATE ON public.market_insights
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_attom_cache_updated_at
    BEFORE UPDATE ON public.attom_property_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_web_scraping_updated_at
    BEFORE UPDATE ON public.web_scraping_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_floor_plan_measurements_updated_at
    BEFORE UPDATE ON public.floor_plan_measurements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ================================================================
-- PART 7: GRANTS
-- ================================================================

GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.users TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.properties TO authenticated;
GRANT SELECT ON public.market_insights TO authenticated;
GRANT SELECT, INSERT ON public.view_analytics TO authenticated;
GRANT SELECT ON public.properties TO anon;
GRANT INSERT ON public.view_analytics TO anon;

-- ================================================================
-- COMPLETE! 
-- ================================================================

-- Log success
DO $$
BEGIN
    RAISE NOTICE '✅ Database schema complete!';
    RAISE NOTICE 'Base tables: users, properties, market_insights, view_analytics';
    RAISE NOTICE 'Phase 1 tables: attom_property_cache, web_scraping_data, comparable_properties, floor_plan_measurements, property_analysis_history';
    RAISE NOTICE 'Total tables: 9';
    RAISE NOTICE 'Ready to use!';
END $$;
