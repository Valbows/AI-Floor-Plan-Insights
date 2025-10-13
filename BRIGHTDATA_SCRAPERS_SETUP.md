# Bright Data Scrapers Library Setup Guide

## ✅ This is the SIMPLER approach (No Browser API needed!)

Instead of using Browser API (Playwright + WebSocket), we're using Bright Data's **pre-built Scrapers Library** which is:
- ✅ Simpler (REST API calls)
- ✅ Available in Playground mode (free tier)
- ✅ No zone setup required
- ✅ Automatic unblocking & CAPTCHA solving

---

## 📋 Step-by-Step Setup

### Step 1: Access Web Scrapers Library

You're already there! From the page you showed in the screenshot:

1. Navigate to: https://brightdata.com/cp/scrapers/browse?category=all
2. Or click **"Web Scrapers Library"** in your dashboard
3. Filter by **"Real-estate"** category

### Step 2: Find the Scrapers You Need

Look for these scrapers:

#### **Zillow Scrapers**:
- ✅ **Zillow properties listing information** - Get property listings
- ✅ **Zillow Full Properties Information** - Complete property details
- ✅ **Zillow price history** - Historical pricing data

#### **Other Real Estate Scrapers** (if available):
- **Redfin properties**
- **Realtor.com properties**
- **Apartments.com**

### Step 3: Get Dataset IDs

For each scraper you want to use:

1. Click on the scraper (e.g., "Zillow Full Properties Information")
2. Look for the **Dataset ID** or **Scraper ID**
   - Format: `gd_xxxxxxxxxxxxx`
   - Example: `gd_l7q7dkf244hwxwzta`
3. Copy this ID - you'll need it for the API calls

**Where to find it**:
- Usually shown in the scraper details page
- Or in the API documentation section
- Or in the code examples they provide

### Step 4: Test with a Simple API Call

You can test directly with curl:

```bash
curl -X POST "https://api.brightdata.com/datasets/v3/trigger" \
  -H "Authorization: Bearer de3475621a753a33c5b8da6a2da5db338841d8684527f1ac30776b038f7cd2c1" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "gd_l7q7dkf244hwxwzta",
    "endpoint": "trigger",
    "discover_by": "search_url",
    "url": "https://www.zillow.com/homes/123-main-st-los-angeles-ca_rb/"
  }'
```

**Expected Response**:
```json
{
  "snapshot_id": "sp_xxxxxxxxxxxxx",
  "status": "running"
}
```

### Step 5: Check Status

```bash
curl "https://api.brightdata.com/datasets/v3/snapshot/sp_xxxxxxxxxxxxx" \
  -H "Authorization: Bearer de3475621a753a33c5b8da6a2da5db338841d8684527f1ac30776b038f7cd2c1"
```

### Step 6: Get Results

Once status is "ready":

```bash
curl "https://api.brightdata.com/datasets/v3/snapshot/sp_xxxxxxxxxxxxx?format=json" \
  -H "Authorization: Bearer de3475621a753a33c5b8da6a2da5db338841d8684527f1ac30776b038f7cd2c1"
```

---

## 💻 Integration with Our Code

### Option A: Use the New Scrapers Client

```python
from app.clients.brightdata_scrapers_client import BrightDataScrapersClient

# Initialize client
client = BrightDataScrapersClient()

# Scrape Zillow
result = client.scrape_zillow_by_address(
    address='123 Main St',
    city='Los Angeles',
    state='CA',
    zip_code='90001'
)

print(result)
```

### Option B: Update Existing Scrapers

We can modify the existing `ZillowScraper`, `RedfinScraper`, etc. to use the Scrapers Library API instead of Playwright.

---

## 🔧 Configuration

### Update .env file (Already done!)

```bash
BRIGHTDATA_API_KEY=de3475621a753a33c5b8da6a2da5db338841d8684527f1ac30776b038f7cd2c1
```

### Get Dataset IDs from Dashboard

You need to find and add these to your configuration:

```python
# backend/app/clients/brightdata_scrapers_client.py

SCRAPER_IDS = {
    'zillow_properties': 'gd_xxxxxxxxxxxxxxx',  # Replace with actual ID
    'zillow_full_info': 'gd_xxxxxxxxxxxxxxx',   # Replace with actual ID
    'zillow_price_history': 'gd_xxxxxxxxxxxxxxx', # Replace with actual ID
    'redfin_properties': 'gd_xxxxxxxxxxxxxxx',  # If available
    'realtor_properties': 'gd_xxxxxxxxxxxxxxx',  # If available
}
```

---

## 📊 What You'll Get

### Zillow Data Example:

```json
{
  "property_url": "https://www.zillow.com/homedetails/...",
  "address": "123 Main St, Los Angeles, CA 90001",
  "price": 450000,
  "bedrooms": 3,
  "bathrooms": 2.0,
  "square_feet": 1500,
  "zestimate": 455000,
  "price_history": [...],
  "tax_history": [...],
  "nearby_schools": [...],
  "property_type": "Single Family",
  "year_built": 1985,
  "lot_size": 5000,
  "days_on_zillow": 15
}
```

---

## 🆚 Comparison: Scrapers Library vs Browser API

| Feature | Scrapers Library ✅ | Browser API ❌ |
|---------|-------------------|---------------|
| **Complexity** | Simple REST API | WebSocket + Playwright |
| **Free Tier** | ✅ Available | ❌ Requires paid plan |
| **Setup** | Just API key | Zone setup required |
| **Maintenance** | Maintained by Bright Data | You maintain scraper code |
| **Speed** | Optimized | Depends on implementation |
| **Reliability** | High (managed service) | Depends on code quality |

---

## 🎯 Next Steps

1. **Go to Web Scrapers Library**: https://brightdata.com/cp/scrapers/browse?category=real-estate
2. **Find Zillow scraper** and copy the Dataset ID
3. **Test with curl** (see Step 4 above)
4. **Update the code** with actual Dataset IDs
5. **Run integration test**:

```bash
docker-compose exec backend python -c "
from app.clients.brightdata_scrapers_client import BrightDataScrapersClient

client = BrightDataScrapersClient()
result = client.scrape_zillow_by_address(
    address='4529 Winona Ct',
    city='Denver',
    state='CO',
    zip_code='80212'
)
print(result)
"
```

---

## 📖 Documentation References

- **Scrapers Library Overview**: https://docs.brightdata.com/datasets/scrapers
- **API Reference**: https://docs.brightdata.com/api-reference/authentication
- **Zillow Scraper**: https://brightdata.com/products/web-scraper/zillow
- **Real Estate Scrapers**: https://brightdata.com/products/web-scraper/real-estate

---

## ⚠️ Important Notes

1. **Dataset IDs are required**: You must get the actual IDs from the dashboard
2. **Free tier limits**: Check your available credits in the dashboard
3. **Rate limits**: Respect API rate limits (typically shown in dashboard)
4. **Data format**: Results are returned as JSON arrays
5. **Async processing**: Most scrapes are asynchronous (trigger → wait → fetch results)

---

## 💡 Why This is Better

1. **No Browser Setup**: No need for Playwright, CDP, or WebSocket connections
2. **Maintained Scrapers**: Bright Data updates scrapers when sites change
3. **Better Reliability**: Professional infrastructure with 99.99% uptime
4. **Automatic Unblocking**: Built-in proxy rotation and CAPTCHA solving
5. **Simpler Code**: REST API instead of complex browser automation

---

**Ready to test?** Start with Step 1 above! 🚀
