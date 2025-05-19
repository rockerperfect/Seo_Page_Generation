from pathlib import Path
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from slugify import slugify
import os
import shutil

# Path Setup
BASE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "solar_companies.csv"
STATIC_DIR = BASE_DIR / "static"

def copy_static_files():
    """Copy static files to output directory"""
    output_static = OUTPUT_DIR / "static"
    output_static.mkdir(parents=True, exist_ok=True)
    
    # Copy CSS directory
    css_dir = STATIC_DIR / "css"
    output_css = output_static / "css"
    if css_dir.exists():
        if output_css.exists():
            shutil.rmtree(output_css)
        shutil.copytree(css_dir, output_css)
        print("✅ Copied static CSS files")

def generate_profiles():
    """Generate company profile pages"""
    # Setup directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Copy static files
    copy_static_files()
    
    # Setup Jinja environment
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("company_profile.jinja")
    
    try:
        # Read and validate data
        if not DATA_FILE.exists():
            raise FileNotFoundError(f"Data file not found: {DATA_FILE}")
            
        df = pd.read_csv(DATA_FILE)
        required_cols = ['Company Name', 'City', 'State', 'Description']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
        
        # Generate pages for each company
        for _, company in df.iterrows():
            # Create company context with defaults
            context = {
                'name': company['Company Name'],
                'city': company['City'],
                'state': company['State'],
                'description': company.get('Description', ''),
                'website': company.get('Website', ''),
                'rating': parse_rating(company.get('Rating')),
                'years_in_business': company.get('Years in Business', None),
                'slug': slugify(company['Company Name'])
            }
            
            # Get related companies in same state
            related_companies = []
            state_companies = df[df['State'] == company['State']]
            for _, related in state_companies.iterrows():
                if related['Company Name'] != company['Company Name']:
                    related_companies.append({
                        'name': related['Company Name'],
                        'city': related['City'],
                        'slug': slugify(related['Company Name']),
                        'rating': parse_rating(related.get('Rating'))
                    })
            
            # Add related companies to context
            context['related_companies'] = related_companies
            
            # Generate HTML
            html = template.render(company=context)
            
            # Save file with proper URL structure
            company_dir = OUTPUT_DIR / 'solar-company' / context['slug']
            company_dir.mkdir(parents=True, exist_ok=True)
            output_file = company_dir / "index.html"
            output_file.write_text(html, encoding='utf-8')
            
            print(f"✅ Generated profile: /solar-company/{context['slug']}/")
        
        print(f"\n✨ Successfully generated {len(df)} company profiles")
        
    except Exception as e:
        print(f"❌ Error generating profiles: {str(e)}")
        raise

def parse_rating(rating):
    """Parse rating value to float or None"""
    try:
        if pd.isna(rating):
            return None
        return float(rating)
    except (ValueError, TypeError):
        return None

if __name__ == "__main__":
    print("Starting profile generation...")
    generate_profiles()
    print(f"\n🏁 Completed! Check output in:\n{os.path.abspath(OUTPUT_DIR)}")