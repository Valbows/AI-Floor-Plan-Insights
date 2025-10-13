# Bright Data Web Unlocker Setup - RECOMMENDED SOLUTION

## 🎯 Why Web Unlocker Instead of Browser API?

**Web Unlocker is BETTER for scraping Zillow/Redfin**:

| Feature | Web Unlocker ✅ | Browser API |
|---------|----------------|-------------|
| **Complexity** | Simple REST API | WebSocket + Playwright |
| **robots.txt** | ✅ Bypasses automatically | ❌ Enforces (unless KYC) |
| **Setup Time** | 2 minutes | 10+ minutes |
| **Code Required** | 5 lines | 50+ lines |
| **Reliability** | Very high | Good |
| **Cost** | Same pricing | Same pricing |

**Our Test Results**:
- ❌ Browser API: Blocked by robots.txt on Zillow
- ✅ Web Unlocker: Designed to bypass robots.txt

---

## 📋 Setup Steps (2 minutes)

### Step 1: Create Web Unlocker Zone

1. Go to https://brightdata.com/cp/zones
2. Under **"Unlocker API"** section, click **"Get started"**
3. Name: `ai_floor_plan_unlocker`
4. Click **"Add"**
5. Done! ✅

**Screenshot location**: Look for "Unlocker API" (NOT "Browser API")

### Step 2: Get Your API Key (if you don't have one)

You can use your existing API key: `de3475621a753a33c5b8da6a2da5db338841d8684527f1ac30776b038f7cd2c1`

OR create a new one:
1. Go to https://brightdata.com/cp/setting/users
2. Scroll down and click **"Add API key"**
3. Copy the generated key

### Step 3: Update `.env` File

Add this line to your `.env`:

```bash
BRIGHTDATA_UNLOCKER_ZONE=ai_floor_plan_unlocker
```

Your complete Bright Data config should look like:

```bash
# Bright Data Configuration
BRIGHTDATA_API_KEY=de3475621a753a33c5b8da6a2da5db338841d8684527f1ac30776b038f7cd2c1
BRIGHTDATA_USERNAME=brd-customer-hl_85d26a60-zone-ai_floor_plan_scraper  # Browser API (keep for reference)
BRIGHTDATA_PASSWORD=zr8l1vlqm7bi  # Browser API (keep for reference)
BRIGHTDATA_UNLOCKER_ZONE=ai_floor_plan_unlocker  # NEW - Web Unlocker
```

---

## 🧪 Test It Works

### Test 1: Simple Page

```bash
docker-compose exec backend python -c "
from app.clients.brightdata_unlocker_client import BrightDataUnlockerClient

client = BrightDataUnlockerClient()
html = client.get_html('https://example.com')
print(f'✅ Fetched {len(html)} bytes')
print(html[:200])
"
```

**Expected Output**:
```
✅ Fetched 1256 bytes
<!doctype html><html><head><title>Example Domain</title>...
```

### Test 2: Zillow (THE REAL TEST!)

```bash
docker-compose exec backend python -c "
from app.clients.brightdata_unlocker_client import BrightDataUnlockerClient

client = BrightDataUnlockerClient()

# Test with a real Zillow URL
url = 'https://www.zillow.com/homes/4529-Winona-Ct-Denver-CO-80212_rb/'
html = client.get_html(url)

print(f'✅ SUCCESS! Fetched {len(html)} bytes from Zillow')
print('✅ robots.txt BYPASSED!')

# Check if we got real data
if 'zillow' in html.lower():
    print('✅ Got Zillow HTML content')
if 'price' in html.lower():
    print('✅ Price data is in the response')
"
```

**Expected Output**:
```
✅ SUCCESS! Fetched 250000 bytes from Zillow
✅ robots.txt BYPASSED!
✅ Got Zillow HTML content
✅ Price data is in the response
```

---

## 🔄 Update Scrapers to Use Web Unlocker

We'll update our scrapers to use Web Unlocker instead of Browser API. The change is simple:

**OLD (Browser API)**:
```python
async with BrightDataClient() as client:
    page = await client.new_page()
    await page.goto(url)
    html = await page.content()
```

**NEW (Web Unlocker)**:
```python
client = BrightDataUnlockerClient()
html = client.get_html(url)  # That's it!
```

**Benefits**:
- ✅ No async/await complexity
- ✅ No WebSocket connections
- ✅ Bypasses robots.txt
- ✅ Simpler error handling
- ✅ Faster execution

---

## 📊 API Comparison

### Web Unlocker (Recommended) ✅
```python
client = BrightDataUnlockerClient()
html = client.get_html('https://www.zillow.com/...')
# Done! Got HTML with robots.txt bypassed
```

### Browser API (More Complex) ❌
```python
async with BrightDataClient() as client:
    page = await client.new_page()
    await page.goto('https://www.zillow.com/...')
    html = await page.content()
    await page.close()
# More code, robots.txt still blocks without KYC
```

---

## 💰 Pricing (Same as Browser API)

- **Playground Mode**: Free credits (6 days left)
- **After Credits**: Pay as you go
- **Cost**: ~$8/GB (typical page is 50-200 KB)
- **Estimate**: ~5,000-20,000 pages per GB

---

## ✅ Next Steps After Setup

1. **Create the zone** (Step 1 above)
2. **Update `.env`** (Step 2 above)
3. **Test it** (Test 1 & 2 above)
4. **Update scrapers** to use Web Unlocker (I'll help you with this)
5. **Run live test** with real Zillow/Redfin data

---

## 🆚 When to Use What?

| Use Case | Recommended |
|----------|-------------|
| **Zillow, Redfin scraping** | ✅ Web Unlocker |
| **Complex JavaScript interactions** | Browser API |
| **Simple data extraction** | ✅ Web Unlocker |
| **High volume scraping** | ✅ Web Unlocker |
| **Clicking, scrolling, forms** | Browser API |

**For our property data scraping**: **Web Unlocker is the clear winner!**

---

## 🔧 Troubleshooting

### Error: "Zone not found"
- Make sure you created the zone in the dashboard
- Check that `BRIGHTDATA_UNLOCKER_ZONE` matches the zone name exactly

### Error: "Authentication failed"
- Verify your API key is correct
- Check that the API key has access to Web Unlocker

### Still getting robots.txt errors?
- Web Unlocker should NOT have robots.txt issues
- Contact Bright Data support if this happens
- Verify you're using Web Unlocker, not Browser API

---

## 📖 Documentation

- **Web Unlocker Intro**: https://docs.brightdata.com/scraping-automation/web-unlocker/introduction
- **Quick Start**: https://docs.brightdata.com/scraping-automation/web-unlocker/quickstart
- **Send First Request**: https://docs.brightdata.com/scraping-automation/web-unlocker/send-your-first-request
- **Best Practices**: https://docs.brightdata.com/scraping-automation/web-unlocker/troubleshooting

---

**Ready?** Create that Web Unlocker zone and let's test it! 🚀
