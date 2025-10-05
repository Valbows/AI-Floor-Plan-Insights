# Manual Test Checklist - Floor Plan Analysis Feature

**Date**: October 5, 2025  
**Feature**: Gemini 2.5 Flash Floor Plan Analysis  
**Status**: Ready for Manual Testing

---

## 🎯 **Test Objective**

Verify that the floor plan analysis feature correctly extracts:
- ✅ Accurate bedroom count
- ✅ Accurate bathroom count  
- ✅ Square footage (calculated or estimated)
- ✅ Room details with dimensions
- ✅ Property features
- ✅ No errors in processing

---

## 📋 **Pre-Test Setup**

### **1. Verify Services Running**

```bash
docker-compose ps
```

**Expected Output**:
- ✅ `ai-floorplan-frontend` - Running on port 5173
- ✅ `ai-floorplan-backend` - Running on port 5000
- ✅ `ai-floorplan-celery` - Running (healthy)
- ✅ `ai-floorplan-redis` - Running (healthy)

### **2. Check Logs** (optional)

```bash
# Backend logs
docker logs ai-floorplan-backend --tail 20

# Celery worker logs
docker logs ai-floorplan-celery --tail 20
```

**Look for**: No recent errors, services initialized

---

## 🧪 **Test Procedure**

### **Step 1: Access Application**

1. Open browser
2. Navigate to: **http://localhost:5173**
3. Verify frontend loads

**Expected**: Login page appears

---

### **Step 2: Login**

**Credentials**:
- **Email**: `jane.smith@realestate.com`
- **Password**: `securepass123`

**Expected**: Redirect to dashboard/upload page

---

### **Step 3: Prepare Test Image**

**Option A - Download Sample**:
```bash
python3 test_manual_floor_plan.py
```

**Option B - Use Your Own**:
- Use any clear floor plan image
- Supported formats: PNG, JPG, JPEG
- Recommended: Floor plan with visible room labels

---

### **Step 4: Upload Floor Plan**

1. Click **"Upload Floor Plan"** button
2. Select image file
3. Enter property address (e.g., "47-10 Austell Place, Queens, NY 11101")
4. Click **Submit**

**Expected**: 
- ✅ Upload progress indicator
- ✅ Status changes: `processing` → `parsing_complete` → `enrichment_complete` → `complete`

---

### **Step 5: Verify Results**

#### **Check Property Details**

Navigate to property details page and verify:

| Field | What to Check | Pass/Fail |
|-------|---------------|-----------|
| **Bedrooms** | Shows actual count (not 0) | ⬜ |
| **Bathrooms** | Shows actual count (not 0) | ⬜ |
| **Square Footage** | Shows calculated/estimated value (not 0) | ⬜ |
| **Layout Type** | Shows description (e.g., "open concept", "traditional") | ⬜ |
| **Features** | Lists property features (if visible on plan) | ⬜ |
| **AI Analysis Notes** | **NO ERROR MESSAGES** | ⬜ |

#### **Expected for 2BR/1BA Floor Plan**:
```
Bedrooms: 2
Bathrooms: 1.0 (or 1.5 if half bath)
Sq Ft: ~1000-1500 (estimated if not visible)
Layout: "Traditional layout" or similar
Features: ["closets", "kitchen", etc.]
```

#### **Error States to Check**:

**❌ FAIL if you see**:
```
- "Error analyzing floor plan with CrewAI"
- "LiteLLM Provider NOT provided"
- "Tool object is not callable"
- All 0 values with real floor plan
```

**✅ PASS if you see**:
```
- Actual bedroom/bathroom counts
- Reasonable square footage
- Layout description
- No error messages
```

---

### **Step 6: Check Backend Logs**

```bash
docker logs ai-floorplan-celery --tail 50 | grep "Floor plan\|✅\|❌"
```

**Look for**:
- ✅ `"✅ Floor plan analysis successful: X BR, Y BA, Z sq ft"`
- ❌ No error messages about LiteLLM or model providers

---

## 🔍 **Detailed Verification**

### **Test Case 1: Simple Floor Plan**

**Input**: 2BR/1BA floor plan with room labels  
**Expected Output**:
- Bedrooms: 2
- Bathrooms: 1.0
- Sq Ft: Estimated based on layout
- Rooms: Lists kitchen, living room, bedrooms, bathroom

### **Test Case 2: Complex Floor Plan**

**Input**: 3BR/2.5BA floor plan with dimensions  
**Expected Output**:
- Bedrooms: 3
- Bathrooms: 2.5 (2 full + 1 half)
- Sq Ft: Calculated from dimensions if visible
- Rooms: Detailed list with dimensions
- Features: Garage, patio, walk-in closets, etc.

### **Test Case 3: Floor Plan with Text**

**Input**: Floor plan with address and lot size  
**Expected Output**:
- Address: Extracted from image
- All counts accurate
- Additional details from visible text

---

## ✅ **Success Criteria**

### **Must Pass All**:
- [ ] Bedrooms extracted correctly (matches floor plan)
- [ ] Bathrooms extracted correctly (including half baths)
- [ ] Square footage calculated/estimated (not 0)
- [ ] Room details populated
- [ ] No error messages in UI
- [ ] No LiteLLM errors in logs
- [ ] Process completes in <30 seconds

### **Bonus Points**:
- [ ] Room dimensions extracted (if visible)
- [ ] Property features identified
- [ ] Address extracted from image
- [ ] Layout type described accurately

---

## 🐛 **Troubleshooting**

### **If You See Errors**:

1. **Check Celery Logs**:
   ```bash
   docker logs ai-floorplan-celery --tail 100
   ```

2. **Look for**:
   - LiteLLM errors → Not fixed, needs work
   - JSON parsing errors → Schema issue
   - Timeout errors → API key issue

3. **Verify Environment**:
   ```bash
   docker exec ai-floorplan-celery printenv | grep GEMINI
   ```
   Should show: `GOOGLE_GEMINI_API_KEY=...`

4. **Restart Services**:
   ```bash
   docker-compose restart backend celery-worker
   ```

---

## 📊 **Test Results Form**

Fill out after testing:

```
Test Date: _______________________
Tester: __________________________

Floor Plan Details:
- Type: ___BR / ___BA
- Source: ___________________________

Results:
- Bedrooms Detected: _____ (Expected: _____)
- Bathrooms Detected: _____ (Expected: _____)
- Sq Ft: _____ (Reasonable? Yes/No)
- Layout: _____________________________
- Errors: _____________________________

Overall Result:  ✅ PASS  /  ❌ FAIL

Notes:
_____________________________________________
_____________________________________________
_____________________________________________

Ready to Push to GitHub?  ✅ YES  /  ❌ NO
```

---

## 🚀 **After Testing**

### **If PASS**:
```bash
# Commit and push
git add -A
git commit -m "✅ Manual test passed - Floor plan analysis working"
git push origin Dev-Branch
```

### **If FAIL**:
- Document the issue in notes
- Share error logs with team
- DO NOT push to GitHub until fixed

---

## 📝 **Quick Commands**

```bash
# View services
docker-compose ps

# Restart if needed
docker-compose restart backend celery-worker

# View logs
docker logs ai-floorplan-celery --tail 100

# Download sample floor plan
python3 test_manual_floor_plan.py

# Run automated test (for comparison)
python3 test_phase2_workflow.py
```

---

**Remember**: Manual testing is the final gate before pushing to GitHub. Take your time and verify thoroughly! 🎯
