# Client Information - Charney (Andrew Epstein)

**Company:** Charney  
**Contact:** Andrew Epstein  
**Project:** AI Floor Plan Parsing & Market Insights  
**Date:** January 2025

---

## 📂 Quick Reference

| Document | Purpose | Key Info |
|----------|---------|----------|
| [charney-intake-form.md](charney-intake-form.md) | Official project requirements | Problem statement, deliverables, success criteria |
| [andrew-meeting-transcript.md](andrew-meeting-transcript.md) | Full meeting conversation | Verbatim transcript with Val, Ariel, Robert, Lee |
| [andrew-requirements-summary.md](andrew-requirements-summary.md) | Organized requirements | Pain points, must-haves, use cases, quotes |

---

## 🎯 Project Summary

### The Problem
Andrew's team at Charney manually analyzes floor plans to determine optimal unit layouts for new developments. This process:
- Takes **2-3 months** with an intern typing dimensions
- Requires manual entry of every room dimension
- Runs regression analysis in Excel to correlate dimensions to PPSF
- Can't scale when intern leaves

### The Solution
AI-powered floor plan analysis that:
- Automatically extracts room dimensions
- Correlates layouts to Price Per Square Foot (PPSF)
- Analyzes entire neighborhoods (bulk/comp sets)
- Identifies optimal layouts automatically
- Reduces 3-month analysis to under 1 day

---

## 🔑 Key Insights

### What They Discovered (Manual Analysis)
From analyzing 2,320+ Brooklyn condo sales:

| Dimension | Impact on PPSF | Insight |
|-----------|----------------|---------|
| Living room 17' x 21' | ⭐⭐⭐⭐⭐ HIGHEST | Sweet spot for maximum value |
| Living room size | ⭐⭐⭐⭐ HIGH | More important than bedrooms |
| Second bedroom size | ⭐ LOW | Doesn't matter much (home offices) |

**Strategy:** Allocate more space to living room, shrink bedrooms → Higher PPSF → More profit

### Business Impact
- **Better design decisions** based on data from 500+ comparable units
- **Competitive advantage** when pitching investors: *"We know exactly what the market wants"*
- **Revenue optimization:** +$300/sqft can mean +$300,000 per unit!

---

## 📊 Their Manual Data (Reference Files)

### Analysis Files:
- **`BK Sales Tracker.csv`** (2,320 rows)
  - Every condo sale in Brooklyn
  - Tracks: Living room width, living room length, bedroom dimensions, kitchen type, PPSF
  - Used for regression analysis

- **`Gowanus Comps Unit Mix (p1).csv`**
  - Compares 16 buildings in Gowanus
  - Unit mix analysis (Studio %, 1BR %, 2BR %, 3BR %)
  - Average square footage by unit type

- **`Gowanus Comps Unit Mix (p2).csv`**
  - Active inventory (16 listings)
  - Tracks: Price, PPSF, Days on Market, price drops

- **`Gowanus Comps Unit Mix (p3).csv`**
  - Deep dive: 450 Union Street (119 units)
  - Every unit number with square footage
  - Unit mix: 18% Studio, 60% 1BR, 13% 2BR, 8% 3BR

---

## ✅ Must-Have Features (P0)

1. **Extract detailed room dimensions** (width x length)
   - Not just "2BR 1BA" but "Living: 17x21, BR1: 12x14"

2. **Bulk analysis** (comp sets)
   - "Analyze all units in Gowanus" not one-by-one

3. **Correlate dimensions to PPSF**
   - Show which dimensions matter most
   - Visual charts with regression lines

4. **Export to CSV**
   - For their own statistical analysis

---

## 🚧 Implementation Status

### ✅ What We Have
- Google Vision API for floor plan parsing
- Extract bedrooms, bathrooms, square footage, room types
- Basic price estimates from ATTOM API
- Agent Tools page for analysis

### 🚧 In Progress
- Dimension extraction (width x length for each room)
- Price correlation charts
- Neighborhood comparison dashboards

### ❌ Not Yet Implemented
- Bulk/comp set analysis tool
- Built-in regression analysis
- DOB filings integration
- Market gap analysis
- MLS integration (REMNY for NY)

---

## 📈 Success Criteria (From Intake Form)

A successful project will:
1. ✅ Automatically parse floor plans into structured data
2. ✅ Show correlation between layouts and PPSF
3. ✅ Dashboard comparing unit mixes across neighborhoods
4. ✅ Replicate insights that currently take weeks

### Key Questions to Answer:
- How reliable are OCR/vision tools at parsing architectural plans?
- What's the best way to visualize neighborhood-level insights?
- Can we replicate or improve on their manual analysis?

---

## 🎬 Current Project: Gowanus

Andrew's team is building a new development in Gowanus, Brooklyn. They want to use our platform to:
1. Pull all comparable floor plans in Gowanus
2. Extract dimensions from each floor plan
3. Correlate dimensions to actual rents/sale prices
4. Identify optimal layouts
5. Design their building based on data
6. Pitch investors with data-driven confidence

---

## 🔄 How This Differs from Original Use Case

| Original Vision (Broker) | Andrew's Needs (Developer) |
|--------------------------|---------------------------|
| Marketing to buyers | Internal design decisions |
| One property at a time | Bulk comp set analysis |
| Highlight features | Optimize dimensions |
| Generate listing copy | Predict PPSF correlation |
| Client-facing reports | Internal analysis/data |

**Key Pivot:** From marketing tool → analytical tool for development decisions

---

## 📝 Key Quotes

> "The biggest pain point is you literally have to manually go floor plan by floor plan and then type into a spreadsheet every single dimension."

> "Living rooms with length and width of 17 and 21 had the highest correlation to price per square foot."

> "What we're trying to solve for is: what are the optimal dimensions of each layout and what correlates the highest to price per square foot."

> "That's a big selling point... if we were to pitch our third party brokerage... we could say look, like we know your market, like we know exactly what you should be building because we have all the data."

---

## 🚀 Next Steps

1. **Validate dimension extraction accuracy**
   - Test with NYC floor plans (they show dimensions on plans)
   - Aim for 95%+ accuracy

2. **Build comp set analysis tool**
   - "Analyze all units in [neighborhood]"
   - Bulk import from StreetEasy/MLS

3. **Add PPSF correlation charts**
   - Scatter plots: dimension vs PPSF
   - Regression lines showing trends
   - Heatmap: which dimensions matter most

4. **Pilot with Gowanus project**
   - Use as test case for full workflow
   - Validate against their manual analysis

5. **Integration roadmap**
   - Phase 1: StreetEasy API
   - Phase 2: REMNY (NYC MLS)
   - Phase 3: DOB filings (architectural plans)

---

**Last Updated:** January 2025

**Files in this folder:**
- `charney-intake-form.md` - Official project requirements
- `andrew-meeting-transcript.md` - Full meeting conversation
- `andrew-requirements-summary.md` - Detailed requirements & analysis
- `BK Sales Tracker.csv` - 2,320 Brooklyn sales data
- `Gowanus Comps Unit Mix (p1).csv` - Market comparison data
- `Gowanus Comps Unit Mix (p2).csv` - Active inventory data
- `Gowanus Comps Unit Mix (p3).csv` - 450 Union St unit breakdown
- `README.md` - This file (overview)

