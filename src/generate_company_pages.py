from pathlib import Path
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from slugify import slugify

# Path Setup
BASE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output" / "solar-company"
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "solar_companies.csv"

def generate_slug(company_name):
    """Generate a URL-friendly slug from company name"""
    return slugify(company_name)

def parse_rating(rating_str):
    """Parse rating from 'X.X/5.0' format"""
    if pd.isna(rating_str):
        return None
    try:
        # Handle 'X.X/5.0' format
        if isinstance(rating_str, str) and '/' in rating_str:
            rating = float(rating_str.split('/')[0])
        else:
            rating = float(rating_str)
        return rating
    except (ValueError, TypeError):
        return None

def generate_company_pages():
    """Generates all company profile pages"""
    # Setup directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
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
                'slug': generate_slug(company['Company Name'])
            }
            
            # Generate HTML
            html = template.render(company=context)
            
            # Save file with proper URL structure
            company_dir = OUTPUT_DIR / context['slug']
            company_dir.mkdir(parents=True, exist_ok=True)
            output_file = company_dir / "index.html"
            output_file.write_text(html, encoding='utf-8')
            
            print(f"✅ Generated profile: /solar-company/{context['slug']}/")
        
        print(f"\n✨ Successfully generated {len(df)} company profiles")
        
    except Exception as e:
        print(f"❌ Error generating company pages: {str(e)}")
        raise

if __name__ == "__main__":
    generate_company_pages()