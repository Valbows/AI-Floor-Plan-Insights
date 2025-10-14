-- ================================================================
-- Fix Supabase Schema Cache Issue
-- Run this in Supabase SQL Editor to refresh the schema cache
-- ================================================================

-- Notify PostgREST to reload the schema cache
NOTIFY pgrst, 'reload schema';

-- Verify the foreign key exists
SELECT
    tc.table_schema, 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'floor_plan_measurements'
    AND tc.table_schema = 'public';

-- If no results above, the foreign key is missing. Run this:
-- ALTER TABLE public.floor_plan_measurements 
--   DROP CONSTRAINT IF EXISTS floor_plan_measurements_property_id_fkey;
-- 
-- ALTER TABLE public.floor_plan_measurements
--   ADD CONSTRAINT floor_plan_measurements_property_id_fkey 
--   FOREIGN KEY (property_id) 
--   REFERENCES public.properties(id) 
--   ON DELETE CASCADE;

-- Notify again after any changes
NOTIFY pgrst, 'reload schema';
