-- ================================================================
-- Verify and Fix Foreign Key Relationship
-- Run this in Supabase SQL Editor
-- ================================================================

-- Step 1: Check if foreign key exists
SELECT 
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS references_table,
    ccu.column_name AS references_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu 
    ON tc.constraint_name = ccu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
    AND tc.table_name = 'floor_plan_measurements';

-- Step 2: If no results above, create the foreign key
-- Uncomment and run if Step 1 shows no results:

-- ALTER TABLE public.floor_plan_measurements 
--   DROP CONSTRAINT IF EXISTS floor_plan_measurements_property_id_fkey CASCADE;

-- ALTER TABLE public.floor_plan_measurements
--   ADD CONSTRAINT floor_plan_measurements_property_id_fkey 
--   FOREIGN KEY (property_id) 
--   REFERENCES public.properties(id) 
--   ON DELETE CASCADE;

-- Step 3: Reload schema cache (run this regardless)
NOTIFY pgrst, 'reload schema';
NOTIFY pgrst, 'reload config';

-- Step 4: Verify again
SELECT 
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS references_table,
    ccu.column_name AS references_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu 
    ON tc.constraint_name = ccu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
    AND tc.table_name = 'floor_plan_measurements';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Schema verification complete!';
    RAISE NOTICE 'If you see a foreign key above, the schema is correct.';
    RAISE NOTICE 'PostgREST cache has been reloaded.';
END $$;
