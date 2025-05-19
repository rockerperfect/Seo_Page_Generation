from pathlib import Path
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from slugify import slugify

# Path Setup
BASE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output" / "solar-companies"
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "solar_companies.csv"

def generate_regional_pages():
    """Generate regional list pages for each state"""
    # Setup directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Setup Jinja environment
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("regional_list.jinja")
    
    try:
        # Read and validate data
        if not DATA_FILE.exists():
            raise FileNotFoundError(f"Data file not found: {DATA_FILE}")
            
        df = pd.read_csv(DATA_FILE)
        required_cols = ['Company Name', 'City', 'State', 'Description']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
        
        # Group companies by state
        states = df['State'].unique()
        
        # Generate pages for each state
        for state in states:
            state_companies = df[df['State'] == state]
            
            # Create state context
            companies_data = []
            for _, company in state_companies.iterrows():
                companies_data.append({
                    'name': company['Company Name'],
                    'city': company['City'],
                    'state': company['State'],
                    'description': company.get('Description', ''),
                    'website': company.get('Website', ''),
                    'slug': slugify(company['Company Name']),
                    'rating': parse_rating(company.get('Rating')),
                    'years_in_business': company.get('Years in Business', None)
                })
            
            # Sort companies by rating (if available), then by name
            companies_data.sort(
                key=lambda x: (-1 * (x['rating'] or 0), x['name'])
            )
            
            # Get unique cities
            cities = sorted(set(c['city'] for c in companies_data))
            
            # Get nearby states (simple implementation - could be improved)
            nearby_states = []
            for other_state in states:
                if other_state != state:
                    nearby_states.append({
                        'name': other_state,
                        'slug': slugify(other_state)
                    })
            
            # Prepare template context
            context = {
                'state_name': state,
                'state_slug': slugify(state),
                'companies': companies_data,
                'cities': cities,
                'total_companies': len(companies_data),
                'nearby_states': nearby_states[:5],  # Show up to 5 nearby states
                'year': '2024'  # Could be made dynamic
            }
            
            # Generate HTML
            html = template.render(**context)
            
            # Save as index.html in state directory
            state_dir = OUTPUT_DIR / slugify(state).lower()
            state_dir.mkdir(parents=True, exist_ok=True)
            output_file = state_dir / "index.html"
            output_file.write_text(html, encoding='utf-8')
            
            print(f"✅ Generated regional page: /solar-companies/{slugify(state).lower()}/")
        
        print(f"\n✨ Successfully generated {len(states)} regional pages")
        
    except Exception as e:
        print(f"❌ Error generating regional pages: {str(e)}")
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
    print("Starting regional page generation...")
    generate_regional_pages()
    print(f"\n🏁 Completed! Check output in:\n{OUTPUT_DIR.absolute()}")