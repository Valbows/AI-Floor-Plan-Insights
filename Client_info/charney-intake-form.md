# AI Native Demo Day Project Intake Form

**Company:** Charney  
**Contact Person:** Andrew Epstein  
**Submitted:** January 2025

---

## 01. Partner Information

**Company Name:** Charney

**Contact Person:** Andrew Epstein

---

## 02. Project Overview

**Project Title:** AI Floor Plan Parsing & Market Insights

### Short Description
This project aims to transform how developers analyze architectural floor plans. Instead of manually reviewing plans, the system will use AI parsing or computer vision to extract meaningful insights.

### Problem Statement
**What problem is this project addressing, and why does it matter to your organization?**

Manual floor plan analysis can take weeks. Automating this process speeds up research and creates data-driven insights for developers, enabling faster and more strategic decisions.

---

## 03. Project Scope

### Two Main Approaches:

#### 1. Price Correlation Tool
Analyze layouts (bedroom counts, square footage, orientation) and correlate them with price per square foot.

#### 2. Competitive Market Analysis
Extract data from architectural plan PDFs (e.g., DOB filings) to detect unit mixes, layouts, and square footage, then compare against existing buildings to highlight market gaps.

### Builder Focus:
- Experiment with OCR/computer vision tools (Tesseract, Google Vision API, Hugging Face models)
- Build structured outputs like tables of unit types and sizes
- Design dashboards for neighborhood comparisons and market gaps

### Suggested Deliverables:
1. A prototype that parses architectural floor plans into structured data
2. Automated correlation reports linking layouts with price per square foot
3. A dashboard comparing unit mixes across neighborhoods to reveal gaps/opportunities
4. Documentation of methods, tools, and limitations

### Known Constraints:
Floor plans vary widely in format; parsing accuracy may depend on input quality.

### Desired Technologies/Tools:
*(Not specified in form)*

### Skills Preferred:
*(Not specified in form)*

---

## 04. Success Criteria

### What would a successful project outcome look like?
A demo that shows how floor plans can be automatically parsed into structured data, with dashboards surfacing correlations and market gaps.

### Specific Questions to Explore:

1. **How reliable are current OCR/computer vision tools at parsing architectural plans?**

2. **What's the best way to visualize neighborhood-level insights from parsed data?**

3. **How can this tool replicate or improve on insights that currently take weeks of manual analysis?**

### Example for Inspiration:
A past project showed how manual floor plan analysis revealed untapped demand in a neighborhood. Builders should aim to replicate this insight using automation.

---

## 📋 Notes & Cross-References

### Related Documents:
- `andrew-meeting-transcript.md` - Full conversation with Andrew
- `andrew-requirements-summary.md` - Detailed requirements breakdown
- `BK Sales Tracker.csv` - Their manual analysis (2,320 sales)
- `Gowanus Comps Unit Mix (p1-p3).csv` - Example of their manual comp analysis

### Key Insights from Meeting:
The intake form's "Price Correlation Tool" directly aligns with Andrew's main pain point:
- They manually tracked dimensions and correlated to PPSF
- Found living rooms 17x21' = highest correlation
- Process took 2-3 months with an intern
- Our AI should automate this entirely

### Implementation Status:
- ✅ **Floor Plan Parsing:** Currently implemented with Google Vision API
- ✅ **Structured Data:** Extracting bedrooms, bathrooms, square footage, room types
- 🚧 **Dimension Extraction:** Partially implemented (needs improvement)
- 🚧 **Price Correlation:** Basic price estimates, needs correlation analysis
- 🚧 **Dashboards:** Agent Tools page has basic charts, needs neighborhood comparison
- ❌ **DOB Filings Integration:** Not yet implemented
- ❌ **Market Gap Analysis:** Not yet implemented

---

**Last Updated:** January 2025

