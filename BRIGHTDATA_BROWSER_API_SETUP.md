# Bright Data Browser API - Quick Setup Guide

## ✅ You're Creating the Zone Now!

Perfect! You found the Browser API option. Here's what to do:

---

## 🚀 Step-by-Step

### Step 1: Complete Zone Creation (You're here!)

1. ✅ **Browser API** is selected (correct!)
2. Click **"Continue"**
3. **Name your zone**: `ai-floor-plan-scraper` (or any name you prefer)
4. Use default settings
5. Click **"Add"** or **"Create Zone"**

### Step 2: Copy Your Credentials

After creating the zone, you'll see:

```
Zone: ai-floor-plan-scraper
Username: brd-customer-hl_xxxxxx-zone-ai_floor_plan
Password: de3475621a753a33c5b8da6a2da5db338841d8684527f1ac30776b038f7cd2c1
Endpoint: wss://brd.superproxy.io:9222
```

**Copy the Username** - you'll need it!

### Step 3: Update Your `.env` File

Add this line to `backend/.env`:

```bash
BRIGHTDATA_USERNAME=brd-customer-hl_xxxxxx-zone-ai_floor_plan
```

*(Replace with your actual username)*

Your full `.env` should look like:

```bash
# Bright Data Browser API
BRIGHTDATA_API_KEY=de3475621a753a33c5b8da6a2da5db338841d8684527f1ac30776b038f7cd2c1
BRIGHTDATA_USERNAME=brd-customer-hl_xxxxxx-zone-ai_floor_plan  # <-- ADD THIS
```

### Step 4: Test the Connection

```bash
docker-compose exec backend python tests/manual/test_brightdata_scrapers.py
```

**Expected Output:**
```
============================================================
Bright Data Web Scraper Test
============================================================
✅ Bright Data Multi-Source Scraper initialized
   API Key: de34756...
   Username: brd-customer-hl_xxxxxx-zone-ai_floor_plan

------------------------------------------------------------
Test: Scraping 123 Main St, New York, NY
------------------------------------------------------------

✅ Multi-source scrape complete!
   Sources Available: 3
   Sources: Zillow, Redfin, StreetEasy
   Data Quality Score: 95/100
   
   Price Consensus: $455,000
   Price Range: $450,000 - $460,000
```

---

## 🔧 If You Get Errors

### Error: "Connection refused"
- Double-check the username in `.env`
- Make sure it starts with `brd-customer-`
- Verify you clicked "Add" to complete zone creation

### Error: "Authentication failed"
- Verify your API key is correct
- Check that username matches exactly (copy-paste from dashboard)

### Error: "Zone not found"
- Wait 1-2 minutes after creating the zone
- Try refreshing the dashboard
- Zone might still be provisioning

---

## ✅ Once It's Working

You can then run the full integration:

```bash
# Test a single property
docker-compose exec backend python -c "
from app.scrapers.multi_source_scraper import MultiSourceScraper
import asyncio

async def test():
    async with MultiSourceScraper() as scraper:
        result = await scraper.scrape_property(
            address='4529 Winona Ct',
            city='Denver',
            state='CO'
        )
        print(f'Price Consensus: \${result[\"price_consensus\"]:,}')
        print(f'Sources: {result[\"sources_available\"]}')
        print(f'Quality Score: {result[\"data_quality_score\"]}/100')

asyncio.run(test())
"
```

---

## 📊 What You'll Get

With Browser API working, your scrapers will:
- ✅ Access Zillow, Redfin, StreetEasy in real-time
- ✅ Get current market prices
- ✅ Handle CAPTCHAs automatically
- ✅ Rotate IPs to avoid blocking
- ✅ Parse and normalize data automatically

Combined with ATTOM API (already working), you'll have:
- **ATTOM**: Official property records, tax data, sales history
- **Web Scraping**: Current market listings, real-time prices, estimated values

**This gives Agent #2 the most comprehensive property data available!**

---

## 🎯 Next: Continue the Build Plan

Once Bright Data is working, you'll have:
- ✅ ATTOM API (verified working)
- ✅ Bright Data Browser API (verified working)
- ✅ Multi-source data aggregation
- ✅ Agent #2 with all tools operational

**Then proceed to:**
1. Database schema updates
2. Enhanced floor plan analysis
3. Statistical regression models

---

**Questions?** Check the [Bright Data Browser API Docs](https://docs.brightdata.com/scraping-automation/scraping-browser/quickstart)

**Ready?** Click "Continue" on that setup page! 🚀
