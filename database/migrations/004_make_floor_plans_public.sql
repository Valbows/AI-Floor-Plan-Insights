-- ============================================
-- Migration 004: Make Floor Plans Bucket Public
-- Purpose: Enable public URLs for improved performance
-- Date: October 7, 2025
-- ============================================

-- Make the floor-plans storage bucket public
UPDATE storage.buckets
SET public = true
WHERE id = 'floor-plans';

-- Verify the change
SELECT id, name, public
FROM storage.buckets
WHERE id = 'floor-plans';
