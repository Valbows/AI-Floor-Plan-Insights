# Andrew's Requirements Summary

**Client:** Andrew (Real Estate Development Company)
**Current Project:** Building in Gowanus, Brooklyn
**Meeting Date:** January 2025

---

## 🎯 Primary Goal
Determine optimal unit layouts and room dimensions for new developments by correlating floor plan features to Price Per Square Foot (PPSF)

---

## 🔴 Critical Pain Points

### 1. Manual Data Entry (Biggest Pain Point)
- **Current Process:** Intern manually types dimensions from every floor plan into spreadsheet
- **Data Tracked:** Living room width, living room length, bedroom 1 width, bedroom 1 length, bedroom 2 dimensions, kitchen size, etc.
- **Scale:** Did this for "every condo in Brooklyn" 
- **Result:** BK Sales Tracker with 2,320+ sales records
- **Time:** 2-3 months per analysis
- **Problem:** When intern left, they couldn't continue this analysis

### 2. One-by-One Upload
- **Current:** Must upload floor plans one at a time
- **Needed:** Bulk import - "analyze all floor plans in Gowanus"
- **Preferred:** Auto-pull from MLS/websites, not manual upload

### 3. Limited Dimension Data
- **Current:** Only get room counts (2BR, 1BA)
- **Needed:** Precise dimensions for EVERY room (width x length)

---

## ✅ What They Currently Do (Manually)

### Their Analysis Process:
1. **Data Collection** (2-3 months)
   - Find floor plans on StreetEasy/Zillow
   - Manually measure/read every room dimension
   - Type into Excel spreadsheet
   - Record sale/rent prices and calculate PPSF

2. **Regression Analysis** (1 week)
   - Run correlations: each dimension vs PPSF
   - Example dimensions tracked:
     - Living room width
     - Living room length
     - Bedroom 1 width
     - Bedroom 1 length
     - Bedroom 2 width
     - Bedroom 2 length
     - Kitchen size
     - etc.

3. **Identify Optimal Layouts**
   - Determine which dimensions correlate highest to PPSF
   - Use insights to design new units

### Key Insights They Found:
- **Living rooms 17' x 21'** → highest correlation to PPSF
- **Living room size** → MORE important than bedroom size
- **Second bedroom size** → LESS important (home offices, young children)
- **Strategy:** Allocate more space to living room, shrink bedrooms → higher PPSF

---

## 📋 Required Features

### Must Have (P0)
1. **Extract detailed room dimensions** (width x length for each room)
   - Living room: 17' x 21'
   - Bedroom 1: 12' x 14'
   - Bedroom 2: 10' x 12'
   - Kitchen: 8' x 10'

2. **Bulk analysis (comp sets)**
   - "Analyze all units in Gowanus"
   - Pull 100+ floor plans at once
   - Not one-by-one upload

3. **Correlate dimensions to PPSF**
   - Show which dimensions matter most
   - Example: "Living rooms 17-21' width = $1,500/sqft avg"

4. **Export to spreadsheet**
   - CSV with all dimensions + pricing
   - For their own regression analysis

### Should Have (P1)
5. **Auto-pull from MLS/websites**
   - Integration: REMNY (New York's MLS)
   - StreetEasy, Zillow, Redfin

6. **Built-in regression analysis**
   - Show correlation charts
   - Identify optimal dimensions automatically

7. **Comp set selection tool**
   - Filter by neighborhood, building type, etc.

### Nice to Have (P2)
8. **Forecasting system**
   - "Design a unit, we'll predict PPSF"
   - Market trend analysis

9. **Optimization suggestions**
   - "Expand living room by 50sf → +$200/sqft"

---

## 💼 Use Case Flow

### Current Project: Gowanus Development

1. Andrew's team is designing a new building in Gowanus
2. They want to know: What unit layouts will maximize PPSF?
3. **Our Platform Should:**
   - Pull all comparable floor plans in Gowanus
   - Extract dimensions from each floor plan (AI)
   - Get actual rent/sale prices for each unit
   - Run correlation: dimensions vs PPSF
   - Show insights: "17x21' living rooms = +12% PPSF"
4. Design team uses insights to optimize floor plans
5. **Pitch to investors:** "We know exactly what the market wants based on data from 500+ comparable units"

---

## 📊 Data They Track (Reference)

From their Excel sheets:
- Address
- Close Date
- Sale Price
- Neighborhood
- Square Footage
- PPSF (Price Per Square Foot)
- Type (Condo/Co-op/House)
- Beds
- Baths
- **Living Room Width**
- **Living Room Length**
- **Bedroom 1 Width**
- **Bedroom 1 Length**
- **Bedroom 2 Width**
- **Bedroom 2 Length**
- **Bedroom 3 Width** (if applicable)
- **Bedroom 3 Length** (if applicable)
- **Kitchen Type** (Line, L-shape, Island, Galley)
- Closets (count)
- Walk In Closet (Living Room)
- Walk In Closet (Master Bedroom)

---

## 🎯 Success Metrics

### Time Savings
- **Current:** 2-3 months per market analysis
- **Target:** Under 1 day (ideally under 1 hour)

### Accuracy
- Must match or exceed manual analysis accuracy

### Adoption
- Used for every new development project
- Becomes standard workflow

### Business Impact
- **Internal:** Better design decisions based on data
- **External:** Competitive advantage when pitching investors
- **Quote:** *"We know exactly what you should be building because we have all the data"*

---

## 🔑 Key Quotes

> "The biggest pain point is you literally have to manually go floor plan by floor plan and then type into a spreadsheet every single dimension."

> "Living rooms with length and width of 17 and 21 had the highest correlation to price per square foot."

> "Second bedrooms, the sizing doesn't matter too much... because people are using them as home offices now."

> "If you're attributing more space to the living room and shrinking the bedroom, we were able to see that data."

> "What we're trying to solve for is: what are the optimal dimensions of each layout and what correlates the highest to price per square foot."

---

## 🔄 How This Differs from Original Use Case

| Original (Broker/Marketing) | Andrew (Developer/Internal) |
|----------------------------|----------------------------|
| Marketing to buyers | Internal design decisions |
| One property at a time | Bulk comp set analysis |
| Highlight features | Optimize dimensions |
| Generate listing copy | Predict PPSF correlation |
| Client-facing reports | Internal analysis/data |

---

## 📂 Reference Files

Located in `Client_info/` folder:
- `BK Sales Tracker.csv` - 2,320 Brooklyn sales they manually tracked
- `Gowanus Comps Unit Mix (p1).csv` - Market analysis for Gowanus area
- `Gowanus Comps Unit Mix (p2).csv` - Active inventory tracking
- `Gowanus Comps Unit Mix (p3).csv` - Detailed unit-by-unit breakdown (450 Union St)

---

## 🚀 Implementation Priority

**Phase 1: Match Their Manual Process**
- Extract all dimensions AI can read
- Export to CSV matching their Excel format
- Let them run regression in Excel (for now)

**Phase 2: Build Analytics Into Platform**
- Add regression charts
- Correlation heatmap showing which dimensions matter
- Comp set selector tool

**Phase 3: Predictive Features**
- "Design a unit and we'll predict PPSF"
- Optimization suggestions
- Market trend forecasting

---

## ✅ Next Steps

1. Review accuracy of current dimension extraction
2. Test: Can we read dimensions from typical NYC floor plans?
3. Build comp set bulk analysis tool
4. Add PPSF correlation charts
5. Pilot with Andrew's Gowanus project

---

**Last Updated:** January 2025

