# Phase 1 Database Schema - Multi-Source Property Data

**Migration**: `005_phase1_multi_source_data.sql`  
**Date**: October 13, 2025  
**Status**: Ready for deployment

---

## 📋 Overview

This migration enhances the database to support:
- ✅ **ATTOM API data caching** (cost optimization)
- ✅ **Multi-source web scraping** (Zillow, Redfin, StreetEasy)
- ✅ **Enhanced market insights** from Agent #2
- ✅ **Floor plan measurements** with AI-estimated room dimensions
- ✅ **Analysis history** and audit trails

---

## 🆕 New Tables

### 1. `attom_property_cache`
**Purpose**: Cache ATTOM API responses to minimize API calls and reduce costs

**Key Fields**:
- `attom_id` - ATTOM's unique property identifier
- `address_*` - Normalized address components
- `bedrooms`, `bathrooms`, `square_feet` - Property characteristics
- `avm_value`, `avm_value_low`, `avm_value_high` - Valuation estimates
- `last_sale_date`, `last_sale_price` - Sales history
- `tax_assessed_value`, `tax_amount` - Tax data
- `expires_at` - Cache expiration (default: 7 days)

**Use Case**:
```sql
-- Check if property is in cache
SELECT * FROM attom_property_cache
WHERE address_line1 = '4529 Winona Ct'
AND city = 'Denver'
AND state = 'CO'
AND expires_at > NOW();
```

**Benefits**:
- ✅ Reduce API costs (ATTOM charges per request)
- ✅ Faster response times
- ✅ Offline analysis capability

---

### 2. `web_scraping_data`
**Purpose**: Store data scraped from Zillow, Redfin, and StreetEasy

**Key Fields**:
- `source` - Data source ('zillow', 'redfin', 'streeteasy')
- `listing_price`, `zestimate`, `redfin_estimate` - Price data
- `walk_score`, `transit_score`, `bike_score` - Livability metrics
- `price_history` - JSONB array of historical prices
- `amenities` - JSONB array of features
- `data_completeness_score` - Quality metric (0-100)

**Use Case**:
```sql
-- Get all scraping data for a property
SELECT 
    source,
    listing_price,
    zestimate,
    walk_score,
    data_completeness_score
FROM web_scraping_data
WHERE property_id = 'property-uuid';
```

**Data Quality Scoring**:
The `calculate_scraping_quality_score()` function automatically scores data:
- Price data available: +20 points
- Property details complete: +20 points
- Market metrics available: +15 points
- Scores available: +15 points
- Price history: +15 points
- Amenities: +15 points

---

### 3. `comparable_properties`
**Purpose**: Store comparable properties found via ATTOM API or web scraping

**Key Fields**:
- `property_id` - Reference to main property
- `address`, `city`, `state` - Comparable location
- `sale_date`, `sale_price` - Transaction details
- `distance_miles` - Distance from main property
- `similarity_score` - How similar (0-100)
- `adjustments` - JSONB of price adjustments
- `data_source` - Where comparable was found

**Use Case**:
```sql
-- Get best comparables for pricing analysis
SELECT * FROM comparable_properties
WHERE property_id = 'property-uuid'
ORDER BY similarity_score DESC, distance_miles ASC
LIMIT 5;
```

**Benefits**:
- ✅ Support Agent #2's pricing analysis
- ✅ Enable statistical regression models
- ✅ Historical tracking of comparables

---

### 4. `floor_plan_measurements`
**Purpose**: Store detailed measurements extracted from floor plans

**Key Fields**:
- `total_square_feet` - Overall square footage
- `total_square_feet_confidence` - Confidence in measurement (0-1)
- `measurement_method` - How measured ('ai_estimation', 'labeled_dimensions', 'hybrid')
- `rooms` - JSONB array of individual room measurements
- `quality_score` - Overall quality (0-100)
- `detected_features` - JSONB array of features found

**Room Data Structure**:
```json
[
  {
    "type": "bedroom",
    "name": "Master Bedroom",
    "length_ft": 12,
    "width_ft": 14,
    "sqft": 168,
    "features": ["closet", "window"]
  },
  {
    "type": "living_room",
    "name": "Living Room",
    "length_ft": 16,
    "width_ft": 14,
    "sqft": 224,
    "features": ["fireplace", "window"]
  }
]
```

**Quality Factors**:
```json
{
  "clarity": 85,        // Image clarity (0-100)
  "completeness": 90,   // How complete the plan is
  "label_quality": 75,  // Quality of dimension labels
  "scale_accuracy": 80  // Accuracy of scale estimation
}
```

---

### 5. `property_analysis_history`
**Purpose**: Audit trail of all AI agent analyses

**Key Fields**:
- `property_id` - Which property was analyzed
- `analysis_type` - Type of analysis ('floor_plan', 'market_insights', 'listing_copy', 'full_analysis')
- `agent_version` - Which version of agent was used
- `input_data` - JSONB of input parameters
- `output_data` - JSONB of analysis results
- `processing_time_seconds` - Performance metric
- `api_calls_made` - Number of API calls
- `cost_estimate` - Estimated USD cost
- `status` - Processing status

**Use Cases**:
```sql
-- Track all analyses for a property
SELECT 
    analysis_type,
    agent_version,
    status,
    processing_time_seconds,
    created_at
FROM property_analysis_history
WHERE property_id = 'property-uuid'
ORDER BY created_at DESC;

-- Calculate total costs for a property
SELECT 
    SUM(cost_estimate) as total_cost_usd,
    SUM(api_calls_made) as total_api_calls
FROM property_analysis_history
WHERE property_id = 'property-uuid';
```

**Benefits**:
- ✅ Audit compliance
- ✅ Cost tracking
- ✅ Performance monitoring
- ✅ Debugging and error tracking

---

## 🔄 Enhanced Existing Tables

### `market_insights` Enhancements
**New Fields Added**:

#### Price Estimation (from Agent #2):
- `estimated_value` - AI-generated price estimate
- `value_range_low` - Lower bound
- `value_range_high` - Upper bound
- `confidence_level` - 'High', 'Medium', or 'Low'
- `pricing_reasoning` - Text explanation

#### Market Trend Analysis:
- `market_trend_direction` - 'Normalizing', 'Appreciating', 'Depreciating'
- `appreciation_rate` - Annual percentage
- `days_on_market_avg` - Average DOM in area
- `inventory_level` - Market inventory description
- `buyer_demand` - Demand level description
- `market_insights_text` - Narrative insights

#### Investment Analysis:
- `investment_score` - Score (0-100)
- `rental_potential` - 'High', 'Medium', 'Low'
- `estimated_rental_income` - Monthly rental estimate
- `cap_rate` - Capitalization rate percentage
- `appreciation_potential` - Future growth prediction
- `risk_factors` - JSONB array of risks
- `opportunities` - JSONB array of opportunities

#### Data Quality & Sources:
- `data_sources` - JSONB array of sources used
- `price_consensus` - Consensus price from multiple sources
- `price_sources_count` - Number of sources
- `data_quality_score` - Overall quality (0-100)

**Example Query**:
```sql
SELECT 
    p.id,
    p.extracted_data->>'address' as address,
    mi.estimated_value,
    mi.value_range_low,
    mi.value_range_high,
    mi.confidence_level,
    mi.investment_score,
    mi.estimated_rental_income,
    mi.cap_rate,
    mi.data_quality_score,
    mi.data_sources
FROM properties p
JOIN market_insights mi ON mi.property_id = p.id
WHERE p.agent_id = auth.uid()
ORDER BY p.created_at DESC;
```

---

## 🔐 Security (Row Level Security)

All new tables have RLS enabled with policies:

### Service Role Policies
- **Full access** to all cache and internal tables
- Required for backend API operations

### Agent Policies
- **Read-only access** to data for their own properties
- Cannot directly insert/update (backend handles this)

### Public Policies
- **No public access** to internal data
- Only properties table has limited public access via share tokens

---

## 📊 Performance Optimizations

### Indexes Created:
```sql
-- ATTOM cache
idx_attom_cache_attom_id
idx_attom_cache_address
idx_attom_cache_expires_at

-- Web scraping
idx_web_scraping_property_id
idx_web_scraping_source
idx_web_scraping_scraped_at

-- Comparables
idx_comparables_property_id
idx_comparables_similarity
idx_comparables_sale_date

-- Analysis history
idx_analysis_history_property_id
idx_analysis_history_type
idx_analysis_history_created_at
```

### Utility Functions:
- `is_attom_cache_valid(cache_row)` - Check if cache entry is still valid
- `calculate_scraping_quality_score(scraping_data)` - Auto-calculate data quality

---

## 🚀 Deployment Instructions

### 1. Apply Migration
```bash
# In Supabase Dashboard -> SQL Editor
# Paste the contents of 005_phase1_multi_source_data.sql
# Click "Run"
```

### 2. Verify Tables Created
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'attom_property_cache',
    'web_scraping_data',
    'comparable_properties',
    'floor_plan_measurements',
    'property_analysis_history'
);
```

### 3. Verify RLS Policies
```sql
SELECT schemaname, tablename, policyname, roles 
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN (
    'attom_property_cache',
    'web_scraping_data',
    'comparable_properties',
    'floor_plan_measurements',
    'property_analysis_history'
);
```

### 4. Test Cache Function
```sql
-- Test ATTOM cache validation
SELECT is_attom_cache_valid(attom_property_cache.*) 
FROM attom_property_cache 
LIMIT 1;
```

---

## 📈 Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                   USER UPLOADS                          │
│                  Floor Plan Image                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Agent #1: Floor Plan Analyzer              │
│                                                         │
│  Extracts: bedrooms, bathrooms, sqft                   │
│  Stores in: properties.extracted_data                  │
│                                                         │
│  NEW: Also estimates room-by-room measurements          │
│  Stores in: floor_plan_measurements                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Agent #2: Market Insights Analyst             │
│                                                         │
│  Step 1: Check ATTOM cache                              │
│  ├─ If found & valid → Use cached data                  │
│  └─ If not found → Call ATTOM API → Store in cache      │
│                                                         │
│  Step 2: Check web scraping data (if KYC approved)      │
│  ├─ Zillow, Redfin, StreetEasy                          │
│  └─ Store in: web_scraping_data                         │
│                                                         │
│  Step 3: Find comparable properties                     │
│  └─ Store in: comparable_properties                     │
│                                                         │
│  Step 4: Generate market insights                       │
│  └─ Store in: market_insights (enhanced fields)         │
│                                                         │
│  Step 5: Log analysis                                   │
│  └─ Store in: property_analysis_history                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  OUTPUT TO FRONTEND                     │
│  - Price estimate with confidence                       │
│  - Market trends                                        │
│  - Investment score                                     │
│  - Comparable properties                                │
│  - Room-by-room measurements                            │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 Usage Examples

### Example 1: Store ATTOM API Response
```python
from app.clients.attom_client import AttomAPIClient

client = AttomAPIClient()
result = client.search_property_data(
    address='4529 Winona Ct',
    city='Denver',
    state='CO'
)

# Store in cache
supabase.table('attom_property_cache').insert({
    'attom_id': result['attomId'],
    'address_line1': result['address'],
    'city': result['city'],
    'state': result['state'],
    'zip_code': result['zipCode'],
    'bedrooms': result['bedrooms'],
    'bathrooms': result['bathrooms'],
    'square_feet': result['squareFeet'],
    'avm_value': result['avmValue'],
    'raw_api_response': result
}).execute()
```

### Example 2: Store Web Scraping Results
```python
from app.scrapers.multi_source_scraper import MultiSourceScraper

async with MultiSourceScraper() as scraper:
    result = await scraper.scrape_property(
        address='4529 Winona Ct',
        city='Denver',
        state='CO'
    )
    
    # Store Zillow data
    if result['sources_available'] and 'Zillow' in result['sources_available']:
        supabase.table('web_scraping_data').insert({
            'property_id': property_id,
            'source': 'zillow',
            'listing_price': result['price_consensus'],
            'bedrooms': result['bedrooms'],
            'bathrooms': result['bathrooms'],
            'square_feet': result['square_feet'],
            'data_completeness_score': result['data_quality_score'],
            'raw_scraping_data': result
        }).execute()
```

### Example 3: Store Agent #2 Analysis
```python
from app.agents.market_insights_analyst import MarketInsightsAnalyst

analyst = MarketInsightsAnalyst()
result = analyst.analyze_property(
    address='4529 Winona Ct, Denver, CO 80212',
    property_data={'bedrooms': 2, 'bathrooms': 1, 'square_footage': 934}
)

# Store market insights
supabase.table('market_insights').update({
    'estimated_value': result['price_estimate']['estimated_value'],
    'value_range_low': result['price_estimate']['value_range_low'],
    'value_range_high': result['price_estimate']['value_range_high'],
    'confidence_level': result['price_estimate']['confidence'],
    'investment_score': result['investment_analysis']['investment_score'],
    'estimated_rental_income': result['investment_analysis']['estimated_rental_income'],
    'cap_rate': result['investment_analysis']['cap_rate'],
    'data_sources': ['attom_api', 'tavily_search'],
    'analysis_summary': result['summary']
}).eq('property_id', property_id).execute()
```

---

## ✅ Migration Checklist

- [ ] Review migration SQL
- [ ] Apply migration in Supabase Dashboard
- [ ] Verify all tables created
- [ ] Verify all indexes created
- [ ] Test RLS policies
- [ ] Update backend models
- [ ] Update API endpoints
- [ ] Update frontend types
- [ ] Test data flow end-to-end
- [ ] Update API documentation

---

**Ready for deployment!** 🚀

*Last Updated: October 13, 2025*  
*Migration: 005_phase1_multi_source_data.sql*
