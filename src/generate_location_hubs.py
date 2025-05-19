from pathlib import Path
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from slugify import slugify
import yaml

# Path Setup
BASE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"
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
        # Handle 'X.X/5.0' format
        if isinstance(rating_str, str) and '/' in rating_str:
            rating = float(rating_str.split('/')[0])
        else:
            rating = float(rating_str)
        return rating
    except (ValueError, TypeError):
        return None

def calculate_avg_rating(ratings):
    """Calculate average rating from a series of ratings"""
    valid_ratings = []
    for rating in ratings:
        parsed = parse_rating(rating)
        if parsed is not None:
            valid_ratings.append(parsed)
    return sum(valid_ratings) / len(valid_ratings) if valid_ratings else None

def generate_location_hubs():
    """Generate location hub pages for states and cities"""
    # Setup directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Setup Jinja environment
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("region_hub.jinja")
    
    try:
        # Read and validate data
        if not DATA_FILE.exists():
            raise FileNotFoundError(f"Data file not found: {DATA_FILE}")
            
        df = pd.read_csv(DATA_FILE)
        regions = load_regions()
        
        if not regions:
            raise ValueError("No regions defined in regions.yml")
        
        # Prepare state data
        states_data = []
        for region in regions:
            state_name = region['name']
            state_companies = df[df['State'].str.lower() == state_name.lower()]
            
            if len(state_companies) == 0:
                continue
                
            # Get cities for this state
            cities = sorted(set(
                city.strip()
                for city in state_companies['City'].unique()
                if pd.notna(city)
            ))
            
            # Calculate state metrics
            avg_rating = calculate_avg_rating(state_companies['Rating']) if 'Rating' in state_companies else None
            
            states_data.append({
                'name': state_name,
                'slug': slugify(state_name),
                'total_companies': len(state_companies),
                'cities': cities,
                'avg_rating': round(avg_rating, 1) if avg_rating else None,
                'priority': region.get('priority', 99)
            })
        
        # Sort states by priority, then name
        states_data.sort(key=lambda x: (x['priority'], x['name']))
        
        # Generate main hub page
        context = {
            'states': states_data,
            'total_companies': len(df),
            'total_states': len(states_data),
            'year': '2024'
        }
        
        # Generate main hub page
        main_hub_dir = OUTPUT_DIR / "solar-companies"
        main_hub_dir.mkdir(parents=True, exist_ok=True)
        
        html = template.render(**context)
        output_file = main_hub_dir / "index.html"
        output_file.write_text(html, encoding='utf-8')
        
        print(f"✅ Generated main hub page: /solar-companies/")
        print(f"   Total States: {len(states_data)}")
        print(f"   Total Companies: {len(df)}")
        
    except Exception as e:
        print(f"❌ Error generating location hubs: {str(e)}")
        raise

if __name__ == "__main__":
    print("🔄 Generating location hubs...")
    generate_location_hubs()