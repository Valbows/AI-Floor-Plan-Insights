# Database Migrations

This directory contains SQL migration scripts for the Supabase PostgreSQL database.

## How to Apply Migrations

### Via Supabase Dashboard (Recommended)

1. **Login to Supabase** → https://supabase.com/dashboard
2. **Select your project**
3. **Navigate to**: SQL Editor (left sidebar)
4. **Click**: "+ New Query"
5. **Copy and paste** the SQL from the migration file
6. **Click**: "Run" (or press Cmd/Ctrl + Enter)
7. **Verify**: Check for success message

### Via Supabase CLI

```bash
# Install Supabase CLI (if not already installed)
npm install -g supabase

# Login
supabase login

# Link to your project
supabase link --project-ref <your-project-ref>

# Run migration
supabase db push
```

### Via psql (Direct Connection)

```bash
# Get connection string from Supabase → Settings → Database
psql "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:5432/postgres"

# Run migration
\i database/migrations/003_shareable_links_and_views.sql
```

## Migration Files

### 001_initial_schema.sql
- **Status**: ✅ Applied
- **Date**: 2025-09-30
- **Purpose**: Initial database schema (users, properties, agents)
- **Tables**: `properties`, user extensions

### 002_property_status_tracking.sql  
- **Status**: ✅ Applied
- **Date**: 2025-10-01
- **Purpose**: Add property status tracking and metadata
- **Tables**: Modified `properties` table

### 003_shareable_links_and_views.sql
- **Status**: ⏳ PENDING - MUST BE APPLIED
- **Date**: 2025-10-07
- **Purpose**: Shareable links (Phase 3.5) and view tracking (Phase 4)
- **Tables**: `shareable_links`, `property_views`
- **Features Enabled**:
  - Shareable link generation
  - Public property reports
  - View analytics tracking
  - Row Level Security (RLS) policies

**⚠️ CRITICAL**: Phase 3.5 and Phase 4.1-4.2 require this migration to function properly!

## Troubleshooting

### Error: "Could not find the table 'public.shareable_links'"
**Solution**: Run migration `003_shareable_links_and_views.sql`

### Error: "Could not find the table 'public.property_views'"
**Solution**: Run migration `003_shareable_links_and_views.sql`

### Error: "relation already exists"
**Solution**: Migration already applied, safe to ignore

## Security Notes

- All tables have Row Level Security (RLS) enabled
- `shareable_links`: Only property owners can create/manage links
- `property_views`: Public can insert (for tracking), only owners can read
- Policies prevent unauthorized access to sensitive data

## Rollback (if needed)

```sql
-- Rollback migration 003
DROP TABLE IF EXISTS public.property_views CASCADE;
DROP TABLE IF EXISTS public.shareable_links CASCADE;
```

## Support

If you encounter issues applying migrations:
1. Check Supabase project status
2. Verify database connection string
3. Ensure you have admin/owner permissions
4. Contact support if errors persist
