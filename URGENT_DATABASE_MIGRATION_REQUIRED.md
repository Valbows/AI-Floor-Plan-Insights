# ⚠️ URGENT: Database Migration Required

## 🔴 Critical Issue Identified

**Problem**: Phase 3.5 (Shareable Links) and Phase 4.1-4.2 (Public Reports) are **NOT WORKING** due to missing database tables.

**Root Cause**: The following tables do not exist in your Supabase database:
- `shareable_links` - Required for Phase 3.5
- `property_views` - Required for Phase 4 view tracking

**Impact**:
- ❌ Shareable link generation returns 500 errors
- ❌ Analytics endpoint returns 500 errors
- ❌ Public report pages cannot log views
- ❌ Dashboard loads slowly (401/500 errors in console)

---

## ✅ SOLUTION: Apply Database Migration

### **Step 1: Open Supabase Dashboard**

1. Go to: https://supabase.com/dashboard
2. Select your project: **AI Floor Plan Insights**
3. Click: **SQL Editor** (in left sidebar)

### **Step 2: Run Migration SQL**

1. Click: **"+ New Query"**
2. Open file: `database/migrations/003_shareable_links_and_views.sql`
3. **Copy ALL SQL content** (124 lines)
4. **Paste into Supabase SQL Editor**
5. Click: **"Run"** (or press Cmd/Ctrl + Enter)

### **Step 3: Verify Success**

You should see:
```
Success. No rows returned
```

If you see errors about tables already existing, that's OK - the migration is idempotent.

### **Step 4: Restart Backend**

```bash
cd /Users/valrene/CascadeProjects/ai-floor-plan-insights
docker-compose restart backend
```

### **Step 5: Test**

1. Login to dashboard
2. Open any property
3. Click "Share" button → Should generate link successfully ✅
4. Click "Analytics" tab → Should load without errors ✅

---

## 📋 Errors Fixed by This Migration

### Before Migration:
```
Error: Could not find the table 'public.shareable_links' in the schema cache
Error: Could not find the table 'public.property_views' in the schema cache
```

### After Migration:
```
✅ Shareable links work
✅ Analytics loads correctly
✅ Public reports function
✅ View tracking enabled
```

---

## 🗄️ What This Migration Creates

### Table: `shareable_links`
- Stores UUID tokens for shareable property reports
- Links expire after 30 days (configurable)
- Can be deactivated without deleting
- Row Level Security (RLS) enabled

**Columns**:
- `id` (UUID, PK)
- `property_id` (UUID, FK → properties)
- `token` (UUID, unique)
- `created_by` (UUID, FK → auth.users)
- `created_at` (timestamp)
- `expires_at` (timestamp)
- `is_active` (boolean)

### Table: `property_views`
- Tracks views of public property reports
- Captures analytics metadata
- Privacy-compliant (no PII beyond standard web analytics)

**Columns**:
- `id` (UUID, PK)
- `property_id` (UUID, FK → properties)
- `viewed_at` (timestamp)
- `user_agent` (text)
- `ip_address` (text)
- `referrer` (text)
- `viewport_width` (integer)
- `viewport_height` (integer)

### Security Policies (RLS)
- ✅ Only property owners can create/view their shareable links
- ✅ Public can log views (anonymous insert)
- ✅ Only property owners can read view analytics
- ✅ All policies prevent unauthorized data access

---

## 🚨 IMPORTANT

**DO NOT PROCEED WITH TESTING** until this migration is applied!

All Phase 3.5 and Phase 4 features depend on these tables existing.

---

## ℹ️ Additional Resources

- **Migration File**: `database/migrations/003_shareable_links_and_views.sql`
- **README**: `database/README.md`
- **Rollback Instructions**: See `database/README.md` (if needed)

---

## 📞 Support

If you encounter any issues applying this migration:
1. Check Supabase project status
2. Verify you have admin/owner permissions
3. Review error messages carefully
4. Contact support if needed

---

**Once migration is applied, all features will work correctly!** ✨
