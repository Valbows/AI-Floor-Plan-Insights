-- ================================================================
-- Create Missing Tables (Phase 1 Tables)
-- Run this in Supabase SQL Editor
-- ================================================================

-- First, let's see what tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- ================================================================
-- Create floor_plan_measurements table
-- ================================================================

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

-- ================================================================
-- Create other missing Phase 1 tables
-- ================================================================

-- ATTOM API Property Cache
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

-- Web Scraping Data
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

-- Comparable Properties
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

-- Property Analysis History
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
-- Create Indexes
-- ================================================================

CREATE INDEX IF NOT EXISTS idx_floor_plan_measurements_property_id ON public.floor_plan_measurements(property_id);
CREATE INDEX IF NOT EXISTS idx_attom_cache_attom_id ON public.attom_property_cache(attom_id);
CREATE INDEX IF NOT EXISTS idx_attom_cache_address ON public.attom_property_cache(address_line1, city, state, zip_code);
CREATE INDEX IF NOT EXISTS idx_attom_cache_expires_at ON public.attom_property_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_web_scraping_property_id ON public.web_scraping_data(property_id);
CREATE INDEX IF NOT EXISTS idx_web_scraping_source ON public.web_scraping_data(source);
CREATE INDEX IF NOT EXISTS idx_web_scraping_scraped_at ON public.web_scraping_data(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_comparables_property_id ON public.comparable_properties(property_id);
CREATE INDEX IF NOT EXISTS idx_comparables_similarity ON public.comparable_properties(similarity_score DESC);
CREATE INDEX IF NOT EXISTS idx_comparables_sale_date ON public.comparable_properties(sale_date DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_history_property_id ON public.property_analysis_history(property_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_type ON public.property_analysis_history(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at ON public.property_analysis_history(created_at DESC);

-- ================================================================
-- Enable RLS and Create Policies
-- ================================================================

ALTER TABLE public.floor_plan_measurements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.attom_property_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.web_scraping_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.comparable_properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.property_analysis_history ENABLE ROW LEVEL SECURITY;

-- Floor plan measurements policies
DROP POLICY IF EXISTS "Service role can manage floor plan measurements" ON public.floor_plan_measurements;
CREATE POLICY "Service role can manage floor plan measurements"
    ON public.floor_plan_measurements FOR ALL
    USING (true);

DROP POLICY IF EXISTS "Agents can view measurements for own properties" ON public.floor_plan_measurements;
CREATE POLICY "Agents can view measurements for own properties"
    ON public.floor_plan_measurements FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.properties
            WHERE properties.id = floor_plan_measurements.property_id
            AND properties.agent_id = auth.uid()
        )
    );

-- ATTOM cache policies
DROP POLICY IF EXISTS "Service role can manage ATTOM cache" ON public.attom_property_cache;
CREATE POLICY "Service role can manage ATTOM cache"
    ON public.attom_property_cache FOR ALL
    USING (true);

-- Web scraping policies
DROP POLICY IF EXISTS "Service role can manage web scraping data" ON public.web_scraping_data;
CREATE POLICY "Service role can manage web scraping data"
    ON public.web_scraping_data FOR ALL
    USING (true);

DROP POLICY IF EXISTS "Agents can view scraping data for own properties" ON public.web_scraping_data;
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
DROP POLICY IF EXISTS "Service role can manage comparables" ON public.comparable_properties;
CREATE POLICY "Service role can manage comparables"
    ON public.comparable_properties FOR ALL
    USING (true);

DROP POLICY IF EXISTS "Agents can view comparables for own properties" ON public.comparable_properties;
CREATE POLICY "Agents can view comparables for own properties"
    ON public.comparable_properties FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.properties
            WHERE properties.id = comparable_properties.property_id
            AND properties.agent_id = auth.uid()
        )
    );

-- Analysis history policies
DROP POLICY IF EXISTS "Service role can manage analysis history" ON public.property_analysis_history;
CREATE POLICY "Service role can manage analysis history"
    ON public.property_analysis_history FOR ALL
    USING (true);

DROP POLICY IF EXISTS "Agents can view analysis history for own properties" ON public.property_analysis_history;
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
-- Create Triggers
-- ================================================================

DROP TRIGGER IF EXISTS update_floor_plan_measurements_updated_at ON public.floor_plan_measurements;
CREATE TRIGGER update_floor_plan_measurements_updated_at
    BEFORE UPDATE ON public.floor_plan_measurements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_attom_cache_updated_at ON public.attom_property_cache;
CREATE TRIGGER update_attom_cache_updated_at
    BEFORE UPDATE ON public.attom_property_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_web_scraping_updated_at ON public.web_scraping_data;
CREATE TRIGGER update_web_scraping_updated_at
    BEFORE UPDATE ON public.web_scraping_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ================================================================
-- Reload Schema Cache
-- ================================================================

NOTIFY pgrst, 'reload schema';
NOTIFY pgrst, 'reload config';

-- ================================================================
-- Verify
-- ================================================================

-- Show all Phase 1 tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'floor_plan_measurements',
    'attom_property_cache',
    'web_scraping_data',
    'comparable_properties',
    'property_analysis_history'
)
ORDER BY table_name;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Phase 1 tables created successfully!';
    RAISE NOTICE 'Tables: floor_plan_measurements, attom_property_cache, web_scraping_data, comparable_properties, property_analysis_history';
    RAISE NOTICE 'PostgREST cache reloaded.';
END $$;
