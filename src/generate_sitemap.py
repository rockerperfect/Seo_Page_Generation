from pathlib import Path
import pandas as pd
from slugify import slugify

def generate_sitemap():
    """Generate sitemap.txt with all page URLs"""
    BASE_DIR = Path(__file__).parent.parent
    OUTPUT_DIR = BASE_DIR / "output"
    WEBFLOW_DIR = BASE_DIR / "webflow_export"
    
    # Base URL - this should be configured based on your actual domain
    BASE_URL = "https://solarcompanies.com"  # Replace with your actual domain
    
    urls = set()
    
    # Add homepage
    urls.add(f"{BASE_URL}/")
    
    # Add region pages from webflow export
    regions_csv = WEBFLOW_DIR / "solar_company_regions.csv"
    if regions_csv.exists():
        regions_df = pd.read_csv(regions_csv)
        for _, region in regions_df.iterrows():
            slug = region['Slug']
            urls.add(f"{BASE_URL}/solar-companies/{slug}/")
            
            # Add company pages for this region
            if 'List of companies' in region:
                companies = str(region['List of companies']).split('|')
                for company in companies:
                    if company and company.strip():
                        urls.add(f"{BASE_URL}/solar-company/{company.strip()}/")
    
    # Write sitemap.txt
    sitemap_path = OUTPUT_DIR / "sitemap.txt"
    with open(sitemap_path, 'w') as f:
        for url in sorted(urls):
            f.write(f"{url}\n")
    
    print(f"✅ Generated sitemap at {sitemap_path}")
    print(f"   Total URLs: {len(urls)}")

if __name__ == "__main__":
    generate_sitemap() 