# 🚀 Next Steps - Phase 0 Completion Checklist

**Status**: Phase 0 is 85% complete. Follow these steps to finish setup and validate the infrastructure.

---

## ✅ Step 1: Execute Database Schema in Supabase

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Open your project: **vuidefwnwsygxkzsjflv**
3. Navigate to **SQL Editor** (left sidebar)
4. Click **New Query**
5. Copy the entire contents of `backend/database_schema.sql`
6. Paste into the SQL Editor
7. Click **Run** to execute the schema

**Expected Result**: You should see:
- ✅ 4 tables created: `users`, `properties`, `market_insights`, `view_analytics`
- ✅ Indexes created
- ✅ RLS policies enabled
- ✅ Triggers created

---

## ✅ Step 2: Create Supabase Storage Bucket

1. In Supabase Dashboard, navigate to **Storage** (left sidebar)
2. Click **Create a new bucket**
3. Configure the bucket:
   - **Name**: `floor-plans`
   - **Public**: ❌ Off (private bucket)
   - **Allowed MIME types**: `image/png`, `image/jpeg`, `image/jpg`, `application/pdf`
   - **File size limit**: 10 MB
4. Click **Create bucket**

5. Set up Storage Policies:
   - Click on the `floor-plans` bucket
   - Go to **Policies** tab
   - Add these policies:

**Policy 1: Agents can upload floor plans**
```sql
CREATE POLICY "Agents can upload floor plans"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'floor-plans' AND auth.uid() IS NOT NULL);
```

**Policy 2: Agents can view own uploads**
```sql
CREATE POLICY "Agents can view own uploads"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'floor-plans' AND auth.uid() IS NOT NULL);
```

**Policy 3: Agents can delete own uploads**
```sql
CREATE POLICY "Agents can delete own uploads"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'floor-plans' AND auth.uid() IS NOT NULL);
```

---

## ✅ Step 3: Validate API Keys

Run the API validation script to ensure all external services are configured correctly:

```bash
cd /Users/valrene/CascadeProjects/ai-floor-plan-insights

# Activate virtual environment (if not using Docker)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run validation script
python backend/tests/manual/test_api_keys.py
```

**Expected Output**:
```
🔍 API Key Validation Test Suite
====================================
✅ Gemini API working!
✅ Tavily API working!
✅ CoreLogic API working!
✅ Google Maps API working!
✅ Supabase connection established

📊 Test Results Summary
====================================
5/5 services configured correctly
🎉 All API keys validated successfully!
```

**If any test fails**, check the corresponding API key in `.env` file.

---

## ✅ Step 4: Start Docker Services

```bash
cd /Users/valrene/CascadeProjects/ai-floor-plan-insights

# Build all Docker images
docker-compose build

# Start all services in detached mode
docker-compose up -d

# View logs (optional)
docker-compose logs -f
```

**Expected Services**:
- `ai-floorplan-redis` - Running on port 6379
- `ai-floorplan-backend` - Running on port 5000
- `ai-floorplan-celery` - Worker running
- `ai-floorplan-frontend` - Running on port 5173

---

## ✅ Step 5: Verify Services are Healthy

```bash
# Check service status
docker-compose ps

# All services should show "Up (healthy)"

# Test backend health endpoint
curl http://localhost:5000/health

# Expected response:
# {"status":"healthy","service":"AI Floor Plan Insights API","version":"1.0.0"}

# Test frontend
open http://localhost:5173
# Should see the login page
```

---

## ✅ Step 6: Set This as Your Active Workspace

Since you don't have an active workspace, set the project directory:

1. In your IDE, go to **File → Open Workspace**
2. Navigate to: `/Users/valrene/CascadeProjects/ai-floor-plan-insights`
3. Open the folder as workspace

This will help with code navigation, autocomplete, and Git integration.

---

## 🎯 Validation Checklist

Before moving to Phase 1, verify:

- [ ] Database schema executed successfully in Supabase
- [ ] Storage bucket `floor-plans` created with policies
- [ ] All 5 API keys validated (run test script)
- [ ] All 4 Docker containers running and healthy
- [ ] Backend health check returns 200 OK
- [ ] Frontend accessible at http://localhost:5173
- [ ] Project set as active workspace in IDE

---

## 🚦 What's Next?

Once all validation steps pass, you're ready for **Phase 1**:

### Phase 1 Objectives:
1. **Authentication System**
   - Implement `/auth/register` endpoint
   - Implement `/auth/login` endpoint
   - Test with Postman/curl

2. **Property Creation Endpoints**
   - Implement floor plan upload endpoint
   - Implement address search endpoint
   - Test file upload to Supabase Storage

3. **AI Agent #1: Floor Plan Analyst**
   - Integrate Gemini Vision API
   - Create structured output schema
   - Test with sample floor plans

4. **Celery Async Workflow**
   - Create property processing task
   - Implement status updates
   - Test task queue

---

## 🆘 Troubleshooting

### Database Schema Errors

**Problem**: "relation already exists"
```bash
# Drop all tables and rerun (CAUTION: deletes data)
DROP TABLE IF EXISTS view_analytics, market_insights, properties, users CASCADE;
```

### Docker Port Conflicts

**Problem**: Port 5000 or 5173 already in use
```bash
# Find process using port
lsof -i :5000

# Kill the process or change port in docker-compose.yml
```

### API Key Validation Fails

**Problem**: One or more APIs return errors
```bash
# Verify the key exists in .env
grep GEMINI .env

# Check for extra spaces or newlines
cat .env | grep -A1 GEMINI_API_KEY
```

### Docker Build Fails

**Problem**: Permission denied or build errors
```bash
# Clean Docker cache
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

---

## 📞 Need Help?

If you encounter issues:

1. Check `log.md` for known issues
2. Review Docker logs: `docker-compose logs -f backend`
3. Test individual components separately
4. Verify all prerequisites are installed

---

**You're doing great! Once these steps are complete, we can begin Phase 1 development.** 🎉
