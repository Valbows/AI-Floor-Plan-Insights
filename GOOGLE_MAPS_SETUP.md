# Google Maps API Setup Guide

## 🗺️ **Setting Up Google Maps for Property Reports**

This guide will help you configure Google Maps integration for the public property reports feature.

---

## 📋 **Prerequisites**

- Google Cloud Platform account
- Credit card (required for Google Cloud, but free tier available)
- Project with billing enabled

---

## 🚀 **Step 1: Create Google Cloud Project**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a Project"** → **"New Project"**
3. Name your project (e.g., "AI Floor Plan Insights")
4. Click **"Create"**

---

## 🔑 **Step 2: Enable Required APIs**

Navigate to: [APIs & Services → Library](https://console.cloud.google.com/apis/library)

Enable these 3 APIs:

### 1. **Maps JavaScript API**
   - Search for "Maps JavaScript API"
   - Click **"Enable"**
   - Used for: Displaying interactive maps

### 2. **Geocoding API**
   - Search for "Geocoding API"
   - Click **"Enable"**
   - Used for: Converting addresses to coordinates

### 3. **Places API**
   - Search for "Places API"  
   - Click **"Enable"**
   - Used for: Finding nearby schools and stores

---

## 🔐 **Step 3: Create API Key**

1. Go to [APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **"+ CREATE CREDENTIALS"** → **"API key"**
3. Copy the API key (you'll need this for Step 5)

---

## 🛡️ **Step 4: Restrict API Key (Recommended)**

For security, restrict your API key:

### **Application Restrictions:**
1. Click on your newly created API key
2. Under "Application restrictions", select **"HTTP referrers (websites)"**
3. Add referrers:
   ```
   localhost:5173/*
   localhost:5000/*
   https://yourdomain.com/*
   ```

### **API Restrictions:**
1. Under "API restrictions", select **"Restrict key"**
2. Select only the enabled APIs:
   - Maps JavaScript API
   - Geocoding API
   - Places API

3. Click **"Save"**

---

## ⚙️ **Step 5: Configure Environment Variable**

### **Local Development:**

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your API key:
   ```env
   VITE_GOOGLE_MAPS_API_KEY=AIzaSy...your_actual_key_here
   ```

4. Restart the frontend:
   ```bash
   docker-compose restart frontend
   ```

### **Production Deployment:**

Set the environment variable in your hosting platform:

- **Vercel**: Settings → Environment Variables
- **Netlify**: Site settings → Build & deploy → Environment
- **Docker**: Add to `docker-compose.yml` or `.env` file

---

## ✅ **Step 6: Verify Setup**

1. **Check if API key is loaded:**
   ```bash
   # In frontend container
   docker exec -it ai-floorplan-frontend sh
   echo $VITE_GOOGLE_MAPS_API_KEY
   ```

2. **Test the map:**
   - Navigate to a public report: `http://localhost:5173/report/{token}`
   - Scroll to the "Location" section
   - Map should load with:
     - ✅ Property marker (green)
     - ✅ Nearby schools (blue)
     - ✅ Nearby stores (red)
     - ✅ Map controls (zoom, satellite/street view)

3. **Check browser console:**
   - Open DevTools (F12)
   - No Google Maps errors should appear
   - If you see errors, check the troubleshooting section below

---

## 💰 **Pricing & Free Tier**

### **Monthly Free Credits:**
- **$200 free credit** per month (covers ~28,000 map loads)
- First **$200 of usage is free** every month

### **Estimated Costs:**
For 1,000 public report views per month:
- Maps JavaScript API: ~$7
- Geocoding API: ~$5  
- Places API: ~$17
- **Total: ~$29/month**
- **With $200 credit: FREE** ✅

### **Usage Limits:**
To avoid unexpected charges, set usage limits:

1. Go to [Quotas](https://console.cloud.google.com/apis/api/maps-backend.googleapis.com/quotas)
2. Set daily quotas for each API
3. Recommended limits:
   - Maps JavaScript API: 1,000 requests/day
   - Geocoding API: 1,000 requests/day
   - Places API: 1,000 requests/day

---

## 🔍 **Troubleshooting**

### **Error: "Google Maps API key not configured"**

**Cause**: Environment variable not set

**Fix**:
1. Check `.env` file exists in `frontend/` directory
2. Verify `VITE_GOOGLE_MAPS_API_KEY=your_key` is present
3. Restart frontend: `docker-compose restart frontend`

---

### **Error: "This API project is not authorized to use this API"**

**Cause**: Required APIs not enabled

**Fix**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable all 3 required APIs (see Step 2)
3. Wait 2-3 minutes for changes to propagate

---

### **Error: "RefererNotAllowedMapError"**

**Cause**: API key restrictions blocking localhost

**Fix**:
1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click your API key
3. Under "Application restrictions", add:
   ```
   localhost:5173/*
   localhost:5000/*
   ```
4. Save and wait 2-3 minutes

---

### **Map loads but no property marker**

**Cause**: Geocoding failed (invalid address)

**Fix**:
1. Check browser console for geocoding errors
2. Verify property address is valid and complete
3. Test address in [Google Maps](https://www.google.com/maps) first

---

### **No nearby schools/stores markers**

**Cause**: Places API not enabled or area has no POIs

**Fix**:
1. Verify Places API is enabled
2. Check if area is rural (fewer POIs)
3. Increase search radius in `PropertyMap.jsx` (currently 1600m = 1 mile)

---

## 🧪 **Testing Without API Key**

If you don't have a Google Maps API key yet, the map component will:
- ✅ Show a friendly error message
- ✅ Not crash the page
- ✅ Allow testing other features

The map will display:
> "Google Maps API key not configured"

---

## 📚 **Resources**

- [Google Maps Platform Documentation](https://developers.google.com/maps/documentation)
- [Maps JavaScript API Guide](https://developers.google.com/maps/documentation/javascript)
- [Geocoding API Guide](https://developers.google.com/maps/documentation/geocoding)
- [Places API Guide](https://developers.google.com/maps/documentation/places/web-service)
- [Pricing Calculator](https://mapsplatform.google.com/pricing/)
- [Usage Limits](https://developers.google.com/maps/documentation/javascript/usage-and-billing)

---

## 🔒 **Security Best Practices**

1. ✅ **Never commit API keys to Git**
   - Add `.env` to `.gitignore`
   - Use `.env.example` for templates

2. ✅ **Use API key restrictions**
   - Limit to specific domains/IPs
   - Limit to specific APIs only

3. ✅ **Set usage quotas**
   - Prevent unexpected charges
   - Monitor usage regularly

4. ✅ **Rotate keys periodically**
   - Generate new keys every 90 days
   - Delete old unused keys

5. ✅ **Monitor API usage**
   - Set up billing alerts
   - Review quotas dashboard weekly

---

## ✨ **Features Enabled**

With Google Maps integration, your public reports now include:

- 📍 **Property Location** - Interactive map centered on property
- 🏫 **Nearby Schools** - Up to 5 schools within 1 mile (blue markers)
- 🛒 **Nearby Stores** - Up to 5 supermarkets within 1 mile (red markers)
- 🗺️ **Map Types** - Roadmap, Satellite, Hybrid views
- 👁️ **Street View** - Google Street View integration
- 🔍 **Zoom Controls** - Interactive zoom and pan
- ℹ️ **Property Info** - Click property marker for details
- 📐 **Coordinates** - Latitude/longitude display

---

## 🚀 **Next Steps**

After setup:
1. ✅ Test maps on public reports
2. ✅ Verify all markers display correctly
3. ✅ Check map controls work (zoom, satellite view)
4. ✅ Monitor API usage in Google Cloud Console
5. ✅ Set up billing alerts

---

**Need help?** Check the [Google Maps Platform Support](https://developers.google.com/maps/support)
