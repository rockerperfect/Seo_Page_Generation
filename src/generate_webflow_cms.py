import pandas as pd
from pathlib import Path
import yaml
from slugify import slugify

# Path Setup
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
WEBFLOW_DIR = BASE_DIR / "webflow_export"
DATA_FILE = DATA_DIR / "solar_companies.csv"
REGIONS_FILE = Path(__file__).parent / "regions.yml"

def load_regions():
    """Load region configuration from YAML file"""
    try:
        with open(REGIONS_FILE, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('regions', [])
    except Exception as e:
        print(f"❌ Error loading regions config: {str(e)}")
        return []

def parse_rating(rating_str):
    """Parse rating from 'X.X/5.0' format"""
    if pd.isna(rating_str):
        return None
    try:
        if isinstance(rating_str, str) and '/' in rating_str:
            rating = float(rating_str.split('/')[0])
        else:
            rating = float(rating_str)
        return rating
    except (ValueError, TypeError):
        return None

def generate_webflow_cms_files():
    """Generate Webflow CMS compatible CSV files"""
    try:
        # Create export directory
        WEBFLOW_DIR.mkdir(parents=True, exist_ok=True)
        
        # Read source data
        if not DATA_FILE.exists():
            raise FileNotFoundError(f"Data file not found: {DATA_FILE}")
            
        df = pd.read_csv(DATA_FILE)
        regions = load_regions()
        
        if not regions:
            raise ValueError("No regions defined in regions.yml")
        
        # Prepare companies data for Webflow
        companies_data = []
        for _, company in df.iterrows():
            companies_data.append({
                'Name': company['Company Name'],
                'Slug': slugify(company['Company Name']),
                'City': company['City'],
                'State': company['State'],
                'Website': company.get('Website', ''),
                'Description': company.get('Description', ''),
                'Rating': parse_rating(company.get('Rating')),
                'Years in Business': company.get('Years in Business', ''),
                'Published': 'true',  # Webflow requires this field
                'Created On': pd.Timestamp.now().strftime('%Y-%m-%d'),
                'Updated On': pd.Timestamp.now().strftime('%Y-%m-%d')
            })
        
        # Create companies CSV
        companies_df = pd.DataFrame(companies_data)
        companies_csv = WEBFLOW_DIR / "solar_companies.csv"
        companies_df.to_csv(companies_csv, index=False)
        print(f"✅ Generated Webflow companies CSV: {companies_csv}")
        print(f"   Total companies: {len(companies_data)}")
        
        # Prepare regions data for Webflow
        regions_data = []
        for region in regions:
            state_name = region['name']
            state_companies = df[df['State'].str.lower() == state_name.lower()]
            
            if len(state_companies) == 0:
                continue
            
            # Get companies in this region
            company_refs = [
                slugify(name)
                for name in state_companies['Company Name'].tolist()
            ]
            
            regions_data.append({
                'Region Name': state_name,
                'Slug': slugify(state_name),
                'Priority': region.get('priority', 99),
                'Company References': '|'.join(company_refs),  # Webflow's multi-reference format
                'Total Companies': len(company_refs),
                'Cities': '|'.join(sorted(state_companies['City'].unique())),
                'Published': 'true',
                'Created On': pd.Timestamp.now().strftime('%Y-%m-%d'),
                'Updated On': pd.Timestamp.now().strftime('%Y-%m-%d')
            })
        
        # Create regions CSV
        regions_df = pd.DataFrame(regions_data)
        regions_csv = WEBFLOW_DIR / "solar_company_regions.csv"
        regions_df.to_csv(regions_csv, index=False)
        print(f"✅ Generated Webflow regions CSV: {regions_csv}")
        print(f"   Total regions: {len(regions_data)}")
        
        # Generate README with instructions
        readme_content = """# Webflow CMS Import Files

This directory contains CSV files ready for import into Webflow CMS.

## Files

1. solar_companies.csv
   - Contains individual company profiles
   - Fields: Name, Slug, City, State, Website, Description, Rating, Years in Business

2. solar_company_regions.csv
   - Contains region/state listings
   - Fields: Region Name, Slug, Priority, Company References, Total Companies, Cities

## Import Instructions

1. In Webflow, create two CMS Collections:
   - "Solar Companies" for company profiles
   - "Solar Company Regions" for region listings

2. Set up the fields in each collection to match the CSV structure

3. Import the CSVs in this order:
   1. First import solar_companies.csv
   2. Then import solar_company_regions.csv

4. For the Company References field in regions:
   - Use Webflow's Multi-reference field type
   - After import, verify the references are correctly linked

5. Create your templates in Webflow:
   - Company profile template
   - Region listing template
   - Main landing page

6. Bind the CMS data to your templates

7. Publish your site

Note: The 'Slug' field is used for URL generation in Webflow.
"""
        readme_file = WEBFLOW_DIR / "README.md"
        readme_file.write_text(readme_content)
        print(f"✅ Generated import instructions: {readme_file}")
        
        print("\n✨ Webflow export completed successfully!")
        
    except Exception as e:
        print(f"❌ Error generating Webflow files: {str(e)}")
        raise

if __name__ == "__main__":
    print("🔄 Generating Webflow CMS files...")
    generate_webflow_cms_files() 