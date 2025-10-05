# Dashboard Testing Checklist

**Date**: October 5, 2025  
**Feature**: Phase 3 - Dashboard Property List & Edit Endpoint  
**Tester**: _________________

---

## 🎯 **Test Objectives**

Verify that:
1. Dashboard loads and displays properties correctly
2. Status badges show accurate states
3. Property cards display correct data
4. Navigation to detail view works
5. Loading/error/empty states work
6. PUT endpoint updates listing copy

---

## 📋 **Pre-Test Setup**

### **1. Verify Services Running**

```bash
docker-compose ps
```

**Expected**: All 4 services (backend, frontend, celery, redis) running ✅

### **2. Access Points**

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Test Credentials**:
  - Email: `jane.smith@realestate.com`
  - Password: `securepass123`

---

## 🧪 **Test Cases**

### **Test 1: Dashboard Loads** ✅

**Steps**:
1. Open browser to http://localhost:5173
2. Login with test credentials
3. Verify redirect to dashboard (`/`)

**Expected Results**:
- [ ] Dashboard page loads without errors
- [ ] Header shows "AI Floor Plan Insights" 
- [ ] User name/email displayed in header
- [ ] "New Property" button visible
- [ ] "My Properties" heading visible

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 2: Empty State** (If no properties exist)

**Steps**:
1. View dashboard when no properties uploaded

**Expected Results**:
- [ ] Gray home icon displayed
- [ ] "No properties yet" message
- [ ] "Create Your First Property" button visible

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 3: Property List Display** (If properties exist)

**Steps**:
1. View dashboard with existing properties
2. Observe property cards

**Expected Results**:
- [ ] Property count displayed (e.g., "3 properties")
- [ ] Properties displayed in grid (1/2/3 columns responsive)
- [ ] Each card shows:
  - [ ] Floor plan image (or placeholder)
  - [ ] Status badge (with color and icon)
  - [ ] Address
  - [ ] Bedrooms count (X BR)
  - [ ] Bathrooms count (X BA)
  - [ ] Square footage (X sq ft)
  - [ ] Created date
- [ ] Cards have hover effect (shadow increases)

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 4: Status Badges**

**Expected Status Colors**:
- **Processing**: Blue badge with Clock icon
- **Analyzing** (parsing_complete): Yellow badge with Loader icon
- **Finalizing** (enrichment_complete): Purple badge with Loader icon
- **Complete**: Green badge with CheckCircle icon
- **Failed**: Red badge with AlertCircle icon

**Steps**:
1. Check status badges on properties
2. Verify colors and icons match status

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 5: Navigation to Detail**

**Steps**:
1. Click on a property card
2. Verify navigation

**Expected Results**:
- [ ] Navigate to `/properties/<property-id>`
- [ ] PropertyDetail page loads
- [ ] Shows full property information
- [ ] Back button or navigation works

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 6: Loading State**

**Steps**:
1. Refresh dashboard
2. Observe loading state (may be brief)

**Expected Results**:
- [ ] Spinner displayed
- [ ] "Loading properties..." message

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 7: Error State**

**Steps**:
1. Stop backend: `docker-compose stop backend`
2. Refresh dashboard
3. Observe error state
4. Click "Try Again"
5. Restart backend: `docker-compose start backend`

**Expected Results**:
- [ ] Red alert icon displayed
- [ ] Error message: "Failed to load properties. Please try again."
- [ ] "Try Again" button visible
- [ ] Clicking "Try Again" re-fetches data

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 8: PUT Endpoint - Edit Listing**

**Steps**:
1. Get property ID from dashboard (click property, check URL)
2. Test endpoint with curl:

```bash
# Replace <TOKEN> with your JWT token from browser DevTools
# Replace <PROPERTY_ID> with actual property ID

curl -X PUT http://localhost:5000/api/properties/<PROPERTY_ID> \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "listing_copy": {
      "headline": "Updated Test Headline",
      "description": "Updated test description for manual testing",
      "highlights": ["Updated feature 1", "Updated feature 2"],
      "call_to_action": "Contact us now!"
    }
  }'
```

**Expected Results**:
- [ ] HTTP 200 status
- [ ] Response includes: `"message": "Property updated successfully"`
- [ ] Response includes updated property data
- [ ] Refresh property detail page shows updated text

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 9: Responsive Design**

**Steps**:
1. Resize browser window to different sizes
2. Check mobile view (< 768px)
3. Check tablet view (768-1024px)
4. Check desktop view (> 1024px)

**Expected Results**:
- [ ] Mobile: 1 column grid
- [ ] Tablet: 2 column grid
- [ ] Desktop: 3 column grid
- [ ] No horizontal scrolling
- [ ] All elements remain visible and usable

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 10: Browser Console Errors**

**Steps**:
1. Open browser DevTools (F12)
2. Check Console tab while using dashboard

**Expected Results**:
- [ ] No JavaScript errors
- [ ] No failed network requests (except during error state test)
- [ ] axios requests show 200 status codes

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

## 🐛 **Known Issues**

Document any bugs found:

1. Issue: _______________________________________
   Severity: ⬜ Critical ⬜ Major ⬜ Minor
   Steps to reproduce: _______________________________________

2. Issue: _______________________________________
   Severity: ⬜ Critical ⬜ Major ⬜ Minor
   Steps to reproduce: _______________________________________

---

## ✅ **Test Summary**

| Test Case | Status | Notes |
|-----------|--------|-------|
| 1. Dashboard Loads | ⬜ PASS ⬜ FAIL | |
| 2. Empty State | ⬜ PASS ⬜ FAIL | |
| 3. Property List | ⬜ PASS ⬜ FAIL | |
| 4. Status Badges | ⬜ PASS ⬜ FAIL | |
| 5. Navigation | ⬜ PASS ⬜ FAIL | |
| 6. Loading State | ⬜ PASS ⬜ FAIL | |
| 7. Error State | ⬜ PASS ⬜ FAIL | |
| 8. PUT Endpoint | ⬜ PASS ⬜ FAIL | |
| 9. Responsive Design | ⬜ PASS ⬜ FAIL | |
| 10. Console Errors | ⬜ PASS ⬜ FAIL | |

**Overall Result**: ⬜ **PASS** (all tests passed) / ⬜ **FAIL** (one or more tests failed)

---

## 📝 **Final Verdict**

**Ready to Push to GitHub?**: ⬜ YES / ⬜ NO

**Reason**: _______________________________________

**Tester Signature**: _________________ **Date**: _______

---

## 🚀 **Quick Test Commands**

```bash
# View all services
docker-compose ps

# View backend logs
docker logs ai-floorplan-backend --tail 50

# View frontend logs
docker logs ai-floorplan-frontend --tail 50

# Restart services if needed
docker-compose restart backend frontend

# Get JWT token (from browser DevTools → Application → Local Storage)
# Key: "token"
```

---

## 💡 **Tips**

1. **Get JWT Token**: Login → F12 → Application tab → Local Storage → Copy "token" value
2. **Check Network Tab**: See all API requests and responses
3. **React DevTools**: Inspect component state and props
4. **Test with Real Data**: Upload a floor plan first if none exist
5. **Multiple Properties**: Upload 2-3 properties to test grid layout properly

---

**Remember**: Manual testing is the final gate before GitHub push. Be thorough! 🎯
