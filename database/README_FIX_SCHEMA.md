# Fix Supabase Schema Cache Issue

## Problem
Getting error: `Could not find a relationship between 'properties' and 'floor_plan_measurements'`

## Cause
Supabase's PostgREST API caches the database schema. When you add new tables or foreign keys, the cache doesn't automatically refresh.

## Solution

### Option 1: Refresh via SQL Editor (Recommended)

1. Open Supabase Dashboard
2. Go to **SQL Editor**
3. Run this command:

```sql
NOTIFY pgrst, 'reload schema';
```

### Option 2: Run the Fix Script

1. Open Supabase Dashboard
2. Go to **SQL Editor**  
3. Copy and paste the contents of `fix_schema_cache.sql`
4. Click **Run**

### Option 3: Restart Supabase Project

1. Go to Supabase Dashboard
2. Settings → General
3. Click "Pause project"
4. Wait 30 seconds
5. Click "Resume project"

## Verification

After refreshing, test the API endpoint:

```bash
curl -X POST "http://localhost:5001/api/analytics/compare" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property_a_id": "uuid-1",
    "property_b_id": "uuid-2"
  }'
```

Should return 404 (properties not found) instead of 500 (schema error).

## Why This Happens

PostgREST (Supabase's API layer) caches foreign key relationships for performance. When you:
- Add new tables
- Add foreign keys
- Modify relationships

The cache needs to be manually refreshed with `NOTIFY pgrst, 'reload schema';`

## Prevention

Run `NOTIFY pgrst, 'reload schema';` after:
- Running migration scripts
- Adding new tables
- Modifying foreign keys
- Changing table structures

---

**Note:** This is a Supabase-specific issue and doesn't affect the application code. The foreign key IS properly defined in the schema - Supabase just needs to refresh its cache to see it.
