
# Solar SEO Page Generator

## 📂 Data Sources and Assumptions

**Data Source:**  
The solar company data used in this project was collected manually from publicly available business directories and websites such as:
- [SolarReviews.com](https://www.solarreviews.com/)
- [Google Maps](https://maps.google.com/)
- [Yelp.com](https://www.yelp.com/)
- [Company websites]

Each entry includes:
- Company Name  
- City and State  
- Website (if available)  
- A brief description of services offered  
- (Optional) Rating or years in business

**Assumptions Made:**
- Only companies from **Florida** and **Texas** were used to align with the assignment scope.
- The dataset was manually curated and is not guaranteed to be exhaustive or perfectly up to date.
- Ratings were included where available; missing values were left blank.
- Descriptions were simplified to short summaries suitable for SEO purposes.

---

## ▶️ How to Run the Script

### ✅ Prerequisites
- Python 3.10+ installed
- `pip` installed
- All dependencies installed (see below)

### ✅ Step 1: Install Dependencies

First, create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
.env\Scriptsctivate  # Windows
```

Then install required packages:

```bash
pip install pandas jinja2 python-slugify
```

### ✅ Step 2: Run the Filtering Script

This filters your dataset into Florida and Texas CSVs:

```bash
python filter_by_region.py
```

### ✅ Step 3: Run the HTML Generation Script

```bash
python generate_html.py
```

This will automatically generate:
- 20 individual company profile pages
- 2 regional listing pages (Florida and Texas)

Output is saved inside the `output/` folder.

---

## ⚙️ Notes on Scalability and Webflow Integration

### ✅ Scalability
The script is designed to support:
- Adding new companies: Simply append to `solar_companies.csv`
- Adding new regions: The filtering logic is dynamic and can be updated to handle any number of states
- Fully automated page generation: Runs through all companies and regions without hardcoded limits

### ✅ Webflow Integration (Optional)
If integrating with Webflow:
1. Prepare two CSVs:
   - `solar_companies.csv` for individual profile pages
   - `solar_company_regions.csv` for regional listing pages

2. Upload to **Webflow CMS**:
   - Create CMS Collections: “Solar Companies” and “Solar Company Regions”
   - Bind fields to your CMS templates
   - Publish the pages

This setup allows scalable content generation via Python with easy publishing via Webflow.
