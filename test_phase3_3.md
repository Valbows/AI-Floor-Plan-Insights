# Phase 3.3 Testing Checklist - Editable Listing & Toast Notifications

**Date**: October 5, 2025  
**Feature**: Property Management - Edit Listing Copy  
**Tester**: _________________

---

## 🎯 **Test Objectives**

Verify that:
1. Edit button toggles edit mode correctly
2. Headline and description are editable
3. Save functionality works (PUT endpoint)
4. Cancel functionality resets changes
5. Toast notifications appear and dismiss
6. Copy-to-clipboard triggers toast
7. UI states (loading, disabled) work correctly

---

## 📋 **Pre-Test Setup**

### **1. Services Running**
```bash
docker-compose ps
```
**Expected**: All 4 services running ✅

### **2. Property with Listing Copy**
- Need a property with status "complete"
- Should have listing_copy with headline and description
- If none exist, upload a floor plan first

### **3. Access Dashboard**
```
http://localhost:5173
Login: jane.smith@realestate.com / securepass123
```

---

## 🧪 **Test Cases**

### **Test 1: Dashboard → Property Navigation** ✅

**Steps**:
1. Login to dashboard
2. Click on a completed property card

**Expected Results**:
- [ ] PropertyDetail page loads
- [ ] Status shows "All Complete" (green badge)
- [ ] Listing copy section visible
- [ ] "Edit Listing" button visible at top of listing section

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 2: Enter Edit Mode** ✅

**Steps**:
1. On PropertyDetail page, locate "Edit Listing" button
2. Click "Edit Listing" button

**Expected Results**:
- [ ] "Edit Listing" button disappears
- [ ] "Cancel" and "Save Changes" buttons appear
- [ ] Headline becomes editable textarea (2 rows, blue border)
- [ ] Description becomes editable textarea (8 rows, gray border)
- [ ] Copy buttons disappear (hidden in edit mode)
- [ ] Textareas show current content

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 3: Edit Headline** ✅

**Steps**:
1. In edit mode, click in headline textarea
2. Modify the text (add/remove/change words)
3. Verify focus styling

**Expected Results**:
- [ ] Textarea is clickable and editable
- [ ] Blue focus ring appears when focused
- [ ] Text changes are visible
- [ ] Textarea grows if needed (up to 2 rows)
- [ ] Placeholder text if empty: "Enter listing headline..."

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 4: Edit Description** ✅

**Steps**:
1. In edit mode, click in description textarea
2. Modify the text significantly
3. Try adding line breaks (Enter key)

**Expected Results**:
- [ ] Textarea is clickable and editable
- [ ] Focus ring appears (primary color)
- [ ] Text changes are visible
- [ ] Line breaks are preserved
- [ ] Textarea scrolls if content > 8 rows
- [ ] Placeholder text if empty: "Enter property description..."

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 5: Cancel Changes** ✅

**Steps**:
1. Make edits to headline and description
2. Click "Cancel" button
3. Observe the result

**Expected Results**:
- [ ] Exit edit mode immediately
- [ ] "Edit Listing" button reappears
- [ ] Headline shows original text (not edited version)
- [ ] Description shows original text (not edited version)
- [ ] Copy buttons reappear
- [ ] No toast notification

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 6: Save Changes** ✅

**Steps**:
1. Enter edit mode
2. Change headline to: "TEST UPDATED HEADLINE"
3. Change description to: "TEST UPDATED DESCRIPTION"
4. Click "Save Changes" button
5. Observe the process

**Expected Results**:
- [ ] Button text changes to "Saving..."
- [ ] Spinner icon appears (rotating)
- [ ] Buttons are disabled during save
- [ ] Toast notification appears (top-right corner)
  - [ ] Green background
  - [ ] CheckCircle icon
  - [ ] Text: "Listing updated successfully! copied!"
- [ ] Toast auto-dismisses after 2-3 seconds
- [ ] Exit edit mode automatically
- [ ] Updated text persists in view mode
- [ ] Copy buttons reappear

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 7: Verify Save Persistence** ✅

**Steps**:
1. After saving changes, refresh the page (F5)
2. Or navigate away and back to the property

**Expected Results**:
- [ ] Property loads with updated headline
- [ ] Property loads with updated description
- [ ] Changes are persistent (saved to database)

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 8: Copy-to-Clipboard (View Mode)** ✅

**Steps**:
1. In view mode (not editing), locate copy buttons
2. Click "Copy" button next to headline
3. Wait for toast notification
4. Click "Copy" button next to description

**Expected Results**:
For each copy:
- [ ] Toast notification appears (top-right)
- [ ] Toast shows: "Headline copied!" or "Description copied!"
- [ ] Toast auto-dismisses after 2 seconds
- [ ] Content is actually in clipboard (paste to verify)
- [ ] Multiple toasts don't stack (new replaces old)

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 9: Copy Social Media Captions** ✅

**Steps**:
1. Scroll to Social Media section (if exists)
2. Click copy button for Instagram caption
3. Click copy button for Facebook post
4. Click copy button for Twitter/X

**Expected Results**:
- [ ] Each click shows toast notification
- [ ] Toast shows correct label (e.g., "Instagram caption copied!")
- [ ] Content is copied to clipboard
- [ ] Toast dismisses automatically

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 10: Copy Email Subject** ✅

**Steps**:
1. Locate "Email Subject Line" section
2. Click copy button
3. Verify toast

**Expected Results**:
- [ ] Toast shows "Email subject copied!"
- [ ] Content copied to clipboard
- [ ] Toast dismisses after 2 seconds

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 11: Save with Empty Fields** ⚠️

**Steps**:
1. Enter edit mode
2. Delete all text from headline
3. Delete all text from description
4. Try to save

**Expected Results**:
- [ ] Backend returns error (headline/description required)
- [ ] Alert shows error message
- [ ] Stays in edit mode
- [ ] No toast notification for success

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 12: Button States During Save** ✅

**Steps**:
1. Enter edit mode
2. Make a change
3. Click "Save Changes"
4. Observe button states during save

**Expected Results**:
- [ ] "Save Changes" button shows spinner
- [ ] "Save Changes" button is disabled
- [ ] "Cancel" button is disabled
- [ ] Cannot click either button during save
- [ ] Buttons re-enable after save completes

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 13: Responsive Design** ✅

**Steps**:
1. Test edit functionality on different screen sizes
2. Resize browser window

**Expected Results**:
- [ ] Edit buttons stack properly on mobile
- [ ] Textareas resize to container width
- [ ] Toast notification visible on all screen sizes
- [ ] No horizontal scrolling in edit mode

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 14: Browser Console** ✅

**Steps**:
1. Open DevTools (F12)
2. Go to Console tab
3. Perform edit and save operations

**Expected Results**:
- [ ] No JavaScript errors
- [ ] PUT request to `/api/properties/<id>` shows 200 status
- [ ] Response includes updated property data
- [ ] No failed network requests

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

### **Test 15: Network Tab Verification** ✅

**Steps**:
1. Open DevTools → Network tab
2. Enter edit mode (no request expected)
3. Save changes
4. Check the PUT request details

**Expected Results**:
- [ ] PUT request to `/api/properties/<id>` appears
- [ ] Status Code: 200 OK
- [ ] Request Payload contains:
  ```json
  {
    "listing_copy": {
      "headline": "...",
      "description": "..."
    }
  }
  ```
- [ ] Response contains updated property data

**Status**: ⬜ PASS / ⬜ FAIL

**Notes**: _______________________________________

---

## 🐛 **Known Issues / Bugs Found**

Document any issues:

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
| 1. Navigation | ⬜ PASS ⬜ FAIL | |
| 2. Enter Edit Mode | ⬜ PASS ⬜ FAIL | |
| 3. Edit Headline | ⬜ PASS ⬜ FAIL | |
| 4. Edit Description | ⬜ PASS ⬜ FAIL | |
| 5. Cancel Changes | ⬜ PASS ⬜ FAIL | |
| 6. Save Changes | ⬜ PASS ⬜ FAIL | |
| 7. Verify Persistence | ⬜ PASS ⬜ FAIL | |
| 8. Copy Buttons | ⬜ PASS ⬜ FAIL | |
| 9. Copy Social Media | ⬜ PASS ⬜ FAIL | |
| 10. Copy Email | ⬜ PASS ⬜ FAIL | |
| 11. Empty Fields | ⬜ PASS ⬜ FAIL | |
| 12. Button States | ⬜ PASS ⬜ FAIL | |
| 13. Responsive | ⬜ PASS ⬜ FAIL | |
| 14. Console | ⬜ PASS ⬜ FAIL | |
| 15. Network Tab | ⬜ PASS ⬜ FAIL | |

**Overall Result**: ⬜ **PASS** (all tests passed) / ⬜ **FAIL** (one or more tests failed)

---

## 📝 **Final Verdict**

**Ready to Push to GitHub?**: ⬜ YES / ⬜ NO

**Reason**: _______________________________________

**Tester Signature**: _________________ **Date**: _______

---

## 🚀 **Quick Test Commands**

```bash
# View frontend logs
docker logs ai-floorplan-frontend --tail 50

# View backend logs  
docker logs ai-floorplan-backend --tail 50

# Restart if needed
docker-compose restart frontend backend
```

---

## 💡 **Testing Tips**

1. **Upload First**: If no properties exist, upload a floor plan via "New Property"
2. **Wait for Complete**: Property must finish processing (status = "complete")
3. **Test Multiple Properties**: Try editing different properties
4. **Test Clipboard**: Actually paste (Ctrl+V) to verify copy worked
5. **Clear Cache**: Hard refresh (Ctrl+Shift+R) if changes don't appear
6. **Check Toast Position**: Should be top-right corner, not blocking content

---

## 📸 **Visual Checks**

**View Mode**:
- [ ] "Edit Listing" button visible and styled
- [ ] Copy buttons have hover effects
- [ ] Headline displays in large bold blue text
- [ ] Description displays with proper line breaks

**Edit Mode**:
- [ ] Textareas have visible borders
- [ ] Focus rings appear when clicked
- [ ] Save button is primary color (blue)
- [ ] Cancel button is secondary (gray)
- [ ] Copy buttons are hidden

**Toast Notification**:
- [ ] Green background (#10B981 or similar)
- [ ] White text
- [ ] CheckCircle icon visible
- [ ] Rounded corners
- [ ] Shadow effect
- [ ] Fixed position (doesn't scroll)

---

**Remember**: Be thorough! Phase 3.3 is a key user-facing feature. 🎯
