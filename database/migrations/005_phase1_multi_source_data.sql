-- Phase 1: Multi-Source Property Data Migration
-- Date: October 13, 2025
-- Description: Add support for ATTOM API, web scraping, and enhanced market insights

-- ================================
-- 1. ATTOM API Property Cache
-- ================================

CREATE TABLE IF NOT EXISTS public.attom_property_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- ATTOM identifiers
    attom_id BIGINT UNIQUE NOT NULL,
    apn TEXT, -- Assessor Parcel Number
    fips_code TEXT,
    
    -- Address (normalized from ATTOM)
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
    
    -- Raw ATTOM response (for future reference)
    raw_api_response JSONB,
    
    -- Cache metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days')
);

-- ================================
-- 2. Web Scraping Data
-- ================================

CREATE TABLE IF NOT EXISTS public.web_scraping_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE,
    
    -- Source identification
    source TEXT NOT NULL CHECK (source IN ('zillow', 'redfin', 'streeteasy')),
    source_url TEXT,
    source_property_id TEXT,
    
    -- Pricing data
    listing_price NUMERIC(12,2),
    zestimate NUMERIC(12,2), -- Zillow only
    redfin_estimate NUMERIC(12,2), -- Redfin only
    price_per_sqft NUMERIC(8,2),
    
    -- Market metrics
    days_on_market INTEGER,
    views_count INTEGER,
    saves_count INTEGER,
    
    -- Property details (may differ from ATTOM)
    bedrooms INTEGER,
    bathrooms NUMERIC(4,2),
    square_feet INTEGER,
    lot_size_sqft INTEGER,
    year_built INTEGER,
    
    -- Scores
    walk_score INTEGER,
    transit_score INTEGER,
    bike_score INTEGER,
    
    -- Price history
    price_history JSONB DEFAULT '[]'::jsonb,
    -- [{"date": "2024-01-01", "price": 450000, "event": "listed"}]
    
    -- Tax history
    tax_history JSONB DEFAULT '[]'::jsonb,
    -- [{"year": 2024, "amount": 3500}]
    
    -- Amenities and features
    amenities JSONB DEFAULT '[]'::jsonb,
    -- ["hardwood floors", "central ac", "dishwasher"]
    
    -- Nearby schools (Redfin/Zillow)
    nearby_schools JSONB DEFAULT '[]'::jsonb,
    -- [{"name": "Elementary School", "rating": 8, "distance": 0.5}]
    
    -- Raw scraping response
    raw_scraping_data JSONB,
    
    -- Data quality
    data_completeness_score INTEGER CHECK (data_completeness_score BETWEEN 0 AND 100),
    scraping_errors TEXT[],
    
    -- Metadata
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- 3. Enhanced Market Insights
-- ================================

-- Add new columns to existing market_insights table
ALTER TABLE public.market_insights 
    ADD COLUMN IF NOT EXISTS attom_property_id UUID REFERENCES public.attom_property_cache(id),
    ADD COLUMN IF NOT EXISTS agent_analysis_version TEXT DEFAULT 'v2.0',
    
    -- Price estimate (from Agent #2)
    ADD COLUMN IF NOT EXISTS estimated_value NUMERIC(12,2),
    ADD COLUMN IF NOT EXISTS value_range_low NUMERIC(12,2),
    ADD COLUMN IF NOT EXISTS value_range_high NUMERIC(12,2),
    ADD COLUMN IF NOT EXISTS confidence_level TEXT CHECK (confidence_level IN ('High', 'Medium', 'Low')),
    ADD COLUMN IF NOT EXISTS pricing_reasoning TEXT,
    
    -- Market trend analysis
    ADD COLUMN IF NOT EXISTS market_trend_direction TEXT,
    ADD COLUMN IF NOT EXISTS appreciation_rate NUMERIC(5,2), -- Percentage
    ADD COLUMN IF NOT EXISTS days_on_market_avg INTEGER,
    ADD COLUMN IF NOT EXISTS inventory_level TEXT,
    ADD COLUMN IF NOT EXISTS buyer_demand TEXT,
    ADD COLUMN IF NOT EXISTS market_insights_text TEXT,
    
    -- Investment analysis
    ADD COLUMN IF NOT EXISTS investment_score INTEGER CHECK (investment_score BETWEEN 0 AND 100),
    ADD COLUMN IF NOT EXISTS rental_potential TEXT,
    ADD COLUMN IF NOT EXISTS estimated_rental_income NUMERIC(10,2),
    ADD COLUMN IF NOT EXISTS cap_rate NUMERIC(5,2), -- Percentage
    ADD COLUMN IF NOT EXISTS appreciation_potential TEXT,
    ADD COLUMN IF NOT EXISTS risk_factors JSONB DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS opportunities JSONB DEFAULT '[]'::jsonb,
    
    -- Analysis summary
    ADD COLUMN IF NOT EXISTS analysis_summary TEXT,
    
    -- Data sources used
    ADD COLUMN IF NOT EXISTS data_sources JSONB DEFAULT '[]'::jsonb,
    -- ["attom_api", "zillow", "redfin", "tavily_search"]
    
    -- Multi-source aggregation
    ADD COLUMN IF NOT EXISTS price_consensus NUMERIC(12,2),
    ADD COLUMN IF NOT EXISTS price_sources_count INTEGER,
    ADD COLUMN IF NOT EXISTS data_quality_score INTEGER CHECK (data_quality_score BETWEEN 0 AND 100);

-- ================================
-- 4. Comparable Properties
-- ================================

CREATE TABLE IF NOT EXISTS public.comparable_properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL,
    
    -- Comparable property details
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
    
    -- Similarity metrics
    distance_miles NUMERIC(6,2),
    similarity_score INTEGER CHECK (similarity_score BETWEEN 0 AND 100),
    adjustments JSONB,
    -- {"bedroom_diff": -10000, "sqft_diff": 5000, "age_diff": -2000}
    
    -- Source
    data_source TEXT NOT NULL CHECK (data_source IN ('attom_api', 'zillow', 'redfin', 'mls')),
    source_id TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- 5. Floor Plan Measurements
-- ================================

CREATE TABLE IF NOT EXISTS public.floor_plan_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL UNIQUE,
    
    -- Overall measurements
    total_square_feet INTEGER,
    total_square_feet_confidence NUMERIC(4,2), -- 0-1 confidence score
    measurement_method TEXT CHECK (measurement_method IN ('ai_estimation', 'labeled_dimensions', 'hybrid')),
    
    -- Room-by-room measurements
    rooms JSONB DEFAULT '[]'::jsonb,
    -- [
    --   {
    --     "type": "bedroom",
    --     "name": "Master Bedroom",
    --     "length_ft": 12,
    --     "width_ft": 14,
    --     "sqft": 168,
    --     "features": ["closet", "window"]
    --   }
    -- ]
    
    -- Quality metrics
    quality_score INTEGER CHECK (quality_score BETWEEN 0 AND 100),
    quality_factors JSONB,
    -- {
    --   "clarity": 85,
    --   "completeness": 90,
    --   "label_quality": 75,
    --   "scale_accuracy": 80
    -- }
    
    -- Detected features
    detected_features JSONB DEFAULT '[]'::jsonb,
    -- ["windows", "doors", "closets", "stairs", "fireplace"]
    
    -- AI model metadata
    model_version TEXT,
    processing_time_seconds NUMERIC(6,2),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- 6. Property Analysis History
-- ================================

CREATE TABLE IF NOT EXISTS public.property_analysis_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID REFERENCES public.properties(id) ON DELETE CASCADE NOT NULL,
    
    -- Analysis metadata
    analysis_type TEXT NOT NULL CHECK (analysis_type IN ('floor_plan', 'market_insights', 'listing_copy', 'full_analysis')),
    agent_version TEXT,
    
    -- Input parameters
    input_data JSONB,
    
    -- Output results
    output_data JSONB,
    
    -- Performance metrics
    processing_time_seconds NUMERIC(6,2),
    api_calls_made INTEGER,
    cost_estimate NUMERIC(8,4), -- USD
    
    -- Status
    status TEXT NOT NULL CHECK (status IN ('processing', 'completed', 'failed', 'timeout')),
    error_message TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- INDEXES FOR PERFORMANCE
-- ================================

-- ATTOM cache indexes
CREATE INDEX IF NOT EXISTS idx_attom_cache_attom_id ON public.attom_property_cache(attom_id);
CREATE INDEX IF NOT EXISTS idx_attom_cache_address ON public.attom_property_cache(address_line1, city, state, zip_code);
CREATE INDEX IF NOT EXISTS idx_attom_cache_expires_at ON public.attom_property_cache(expires_at);

-- Web scraping data indexes
CREATE INDEX IF NOT EXISTS idx_web_scraping_property_id ON public.web_scraping_data(property_id);
CREATE INDEX IF NOT EXISTS idx_web_scraping_source ON public.web_scraping_data(source);
CREATE INDEX IF NOT EXISTS idx_web_scraping_scraped_at ON public.web_scraping_data(scraped_at DESC);

-- Comparable properties indexes
CREATE INDEX IF NOT EXISTS idx_comparables_property_id ON public.comparable_properties(property_id);
CREATE INDEX IF NOT EXISTS idx_comparables_similarity ON public.comparable_properties(similarity_score DESC);
CREATE INDEX IF NOT EXISTS idx_comparables_sale_date ON public.comparable_properties(sale_date DESC);

-- Floor plan measurements indexes
CREATE INDEX IF NOT EXISTS idx_floor_plan_measurements_property_id ON public.floor_plan_measurements(property_id);

-- Analysis history indexes
CREATE INDEX IF NOT EXISTS idx_analysis_history_property_id ON public.property_analysis_history(property_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_type ON public.property_analysis_history(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at ON public.property_analysis_history(created_at DESC);

-- ================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ================================

-- ATTOM property cache (service role only - internal cache)
ALTER TABLE public.attom_property_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage ATTOM cache"
    ON public.attom_property_cache FOR ALL
    USING (true);

-- Web scraping data (service role and property owners)
ALTER TABLE public.web_scraping_data ENABLE ROW LEVEL SECURITY;

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

-- Comparable properties
ALTER TABLE public.comparable_properties ENABLE ROW LEVEL SECURITY;

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

-- Floor plan measurements
ALTER TABLE public.floor_plan_measurements ENABLE ROW LEVEL SECURITY;

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

-- Property analysis history
ALTER TABLE public.property_analysis_history ENABLE ROW LEVEL SECURITY;

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

-- ================================
-- TRIGGERS
-- ================================

-- Update triggers for new tables
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

-- ================================
-- UTILITY FUNCTIONS
-- ================================

-- Function to check if ATTOM cache is expired
CREATE OR REPLACE FUNCTION is_attom_cache_valid(cache_row public.attom_property_cache)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN cache_row.expires_at > NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to calculate data quality score for web scraping
CREATE OR REPLACE FUNCTION calculate_scraping_quality_score(scraping_data public.web_scraping_data)
RETURNS INTEGER AS $$
DECLARE
    score INTEGER := 0;
BEGIN
    -- Price data available (20 points)
    IF scraping_data.listing_price IS NOT NULL THEN
        score := score + 20;
    END IF;
    
    -- Property details (20 points)
    IF scraping_data.bedrooms IS NOT NULL AND scraping_data.bathrooms IS NOT NULL AND scraping_data.square_feet IS NOT NULL THEN
        score := score + 20;
    END IF;
    
    -- Market metrics (15 points)
    IF scraping_data.days_on_market IS NOT NULL THEN
        score := score + 15;
    END IF;
    
    -- Scores available (15 points)
    IF scraping_data.walk_score IS NOT NULL OR scraping_data.transit_score IS NOT NULL THEN
        score := score + 15;
    END IF;
    
    -- Price history (15 points)
    IF jsonb_array_length(scraping_data.price_history) > 0 THEN
        score := score + 15;
    END IF;
    
    -- Amenities (15 points)
    IF jsonb_array_length(scraping_data.amenities) > 0 THEN
        score := score + 15;
    END IF;
    
    RETURN score;
END;
$$ LANGUAGE plpgsql;

-- ================================
-- COMMENTS
-- ================================

COMMENT ON TABLE public.attom_property_cache IS 'Cache for ATTOM API responses to minimize API calls and costs';
COMMENT ON TABLE public.web_scraping_data IS 'Multi-source web scraping data from Zillow, Redfin, and StreetEasy';
COMMENT ON TABLE public.comparable_properties IS 'Comparable properties for market analysis';
COMMENT ON TABLE public.floor_plan_measurements IS 'Enhanced floor plan measurements with AI-estimated room dimensions';
COMMENT ON TABLE public.property_analysis_history IS 'Audit trail of all AI agent analyses performed';

COMMENT ON COLUMN public.market_insights.estimated_value IS 'AI-generated price estimate from Agent #2';
COMMENT ON COLUMN public.market_insights.investment_score IS 'Investment potential score (0-100) based on rental yield, appreciation, and market factors';
COMMENT ON COLUMN public.market_insights.data_quality_score IS 'Overall data quality score based on number and reliability of sources';

-- ================================
-- MIGRATION COMPLETE
-- ================================

-- Log migration
DO $$
BEGIN
    RAISE NOTICE 'Phase 1 Migration Complete: Multi-Source Property Data';
    RAISE NOTICE 'Tables created: attom_property_cache, web_scraping_data, comparable_properties, floor_plan_measurements, property_analysis_history';
    RAISE NOTICE 'market_insights table enhanced with Agent #2 output fields';
END $$;
