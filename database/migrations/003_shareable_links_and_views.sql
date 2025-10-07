-- Migration 003: Shareable Links and Property Views
-- Purpose: Add tables for Phase 3.5 (Shareable Links) and Phase 4 (Public Reports & View Tracking)
-- Date: 2025-10-07

-- ============================================
-- Table: shareable_links
-- Purpose: Store shareable tokens for public property reports
-- ============================================
CREATE TABLE IF NOT EXISTS public.shareable_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES public.properties(id) ON DELETE CASCADE,
    token UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
    created_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_shareable_links_token ON public.shareable_links(token);
CREATE INDEX IF NOT EXISTS idx_shareable_links_property_id ON public.shareable_links(property_id);
CREATE INDEX IF NOT EXISTS idx_shareable_links_is_active ON public.shareable_links(is_active);
CREATE INDEX IF NOT EXISTS idx_shareable_links_expires_at ON public.shareable_links(expires_at);

-- ============================================
-- Table: property_views
-- Purpose: Track views of public property reports for analytics
-- ============================================
CREATE TABLE IF NOT EXISTS public.property_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES public.properties(id) ON DELETE CASCADE,
    viewed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_agent TEXT,
    ip_address TEXT,
    referrer TEXT,
    viewport_width INTEGER,
    viewport_height INTEGER
);

-- Create indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_property_views_property_id ON public.property_views(property_id);
CREATE INDEX IF NOT EXISTS idx_property_views_viewed_at ON public.property_views(viewed_at);

-- ============================================
-- Row Level Security (RLS) Policies
-- ============================================

-- Enable RLS on shareable_links
ALTER TABLE public.shareable_links ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own shareable links
CREATE POLICY "Users can view own shareable links"
ON public.shareable_links
FOR SELECT
USING (auth.uid() = created_by);

-- Policy: Users can create shareable links for their own properties
CREATE POLICY "Users can create shareable links"
ON public.shareable_links
FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.properties
        WHERE id = property_id
        AND agent_id = auth.uid()
    )
);

-- Policy: Users can update their own shareable links
CREATE POLICY "Users can update own shareable links"
ON public.shareable_links
FOR UPDATE
USING (auth.uid() = created_by);

-- Policy: Users can delete their own shareable links
CREATE POLICY "Users can delete own shareable links"
ON public.shareable_links
FOR DELETE
USING (auth.uid() = created_by);

-- Enable RLS on property_views
ALTER TABLE public.property_views ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anonymous inserts (public report views)
CREATE POLICY "Allow public to log property views"
ON public.property_views
FOR INSERT
WITH CHECK (true);

-- Policy: Property owners can view analytics
CREATE POLICY "Property owners can view analytics"
ON public.property_views
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.properties
        WHERE id = property_id
        AND agent_id = auth.uid()
    )
);

-- ============================================
-- Comments for documentation
-- ============================================
COMMENT ON TABLE public.shareable_links IS 'Stores shareable tokens for public property reports (Phase 3.5)';
COMMENT ON TABLE public.property_views IS 'Tracks views of public property reports for analytics (Phase 4.1)';

COMMENT ON COLUMN public.shareable_links.token IS 'Unique UUID token used in shareable URLs';
COMMENT ON COLUMN public.shareable_links.expires_at IS 'Expiration timestamp (default: 30 days from creation)';
COMMENT ON COLUMN public.shareable_links.is_active IS 'Flag to deactivate links without deleting them';

COMMENT ON COLUMN public.property_views.user_agent IS 'Browser user agent string for analytics';
COMMENT ON COLUMN public.property_views.ip_address IS 'IP address of viewer (privacy-compliant tracking)';
COMMENT ON COLUMN public.property_views.referrer IS 'Referrer URL (where the view came from)';
