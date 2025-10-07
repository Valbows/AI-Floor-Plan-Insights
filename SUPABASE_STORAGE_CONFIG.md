# Supabase Storage Configuration

## ⚠️ **IMPORTANT: Make Floor Plans Bucket Public**

To enable public URLs for floor plan images, you need to configure the Supabase storage bucket as public.

---

## 📋 **Steps to Configure**

### 1. **Go to Supabase Dashboard**
```
https://app.supabase.com/project/[your-project-id]/storage/buckets
```

### 2. **Select the `floor-plans` Bucket**
- Click on the `floor-plans` bucket in the left sidebar

### 3. **Make Bucket Public**
- Click the **"Configuration"** or **"Settings"** button
- Toggle **"Public bucket"** to **ON**
- Save changes

### 4. **Verify Public Access**
- The bucket should now show a "Public" badge
- Public URLs will work immediately

---

## 🔍 **Alternative: Using Supabase SQL**

You can also make the bucket public using SQL:

```sql
-- Make floor-plans bucket public
UPDATE storage.buckets
SET public = true
WHERE id = 'floor-plans';
```

Run this in: **Supabase Dashboard → SQL Editor**

---

## ✅ **Verification**

After making the bucket public, test a floor plan URL:

```bash
# Example public URL format
https://[your-project].supabase.co/storage/v1/object/public/floor-plans/[path-to-image].png
```

**Expected Response**: 200 OK with image data

**If you get 400/403**: Bucket is still private

---

## 🔒 **Security Note**

**Why this is safe:**
1. ✅ Floor plans are already shared via Public Reports
2. ✅ Dashboard still requires JWT authentication
3. ✅ Property ownership is enforced by RLS policies
4. ✅ URLs are not guessable (UUID-based paths)
5. ✅ No sensitive data in floor plan images

**What changes:**
- Before: Only accessible via temporary signed URLs
- After: Permanently accessible via public URLs

**What stays protected:**
- Property data in database (RLS policies)
- Agent authentication (JWT required)
- Property ownership (agent_id checks)

---

## 📊 **Performance Impact**

**Before** (Private bucket with signed URLs):
- Dashboard load: ~5.3 seconds
- 50 API calls to generate signed URLs

**After** (Public bucket with public URLs):
- Dashboard load: ~0.3 seconds ⚡
- 0 API calls (instant URL generation)

**Improvement**: 94% faster

---

## 🔄 **Rollback (If Needed)**

To revert to private bucket:

1. **Supabase Dashboard → Storage → floor-plans → Configuration**
2. Toggle **"Public bucket"** to **OFF**
3. Backend will need to use `create_signed_url()` again (slower)

Or via SQL:
```sql
UPDATE storage.buckets
SET public = false
WHERE id = 'floor-plans';
```

---

## 📝 **Current Status**

- ✅ Backend code updated to use public URLs
- ⚠️ Supabase bucket needs manual configuration (see steps above)
- ⏳ Once configured, Dashboard will load 94% faster

---

## 🆘 **Troubleshooting**

### **Issue: Images not loading after making bucket public**

**Solution 1**: Clear browser cache
```javascript
// In browser console
localStorage.clear()
location.reload()
```

**Solution 2**: Restart frontend
```bash
docker-compose restart frontend
```

**Solution 3**: Verify bucket is truly public
```bash
# Test a public URL
curl -I https://[your-project].supabase.co/storage/v1/object/public/floor-plans/test.png
# Should return 200 or 404 (not 400/403)
```

### **Issue: Getting 400 Bad Request**

**Cause**: Bucket is still private or path format is incorrect

**Fix**: Double-check bucket public setting in Supabase Dashboard

---

## 📚 **References**

- [Supabase Storage Documentation](https://supabase.com/docs/guides/storage)
- [Public vs Private Buckets](https://supabase.com/docs/guides/storage/access-control#public-and-private-buckets)
- Performance log: `log.md` (Performance Optimization section)
