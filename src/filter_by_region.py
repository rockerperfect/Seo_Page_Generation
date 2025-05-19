import pandas as pd
from pathlib import Path
import yaml

# Path Setup
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MAIN_CSV = DATA_DIR / "solar_companies.csv"
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

def filter_companies():
    """Filter companies by region and save to separate files"""
    try:
        # Verify main CSV exists
        if not MAIN_CSV.exists():
            raise FileNotFoundError(f"Main data file not found at: {MAIN_CSV}")
        
        # Create data directory if needed
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load main dataset
        df = pd.read_csv(MAIN_CSV)
        print(f"📊 Loaded {len(df)} companies from main dataset")
        
        # Load region configuration
        regions = load_regions()
        if not regions:
            raise ValueError("No regions defined in regions.yml")
        
        # Process each region
        for region in regions:
            state_name = region['name']
            priority = region.get('priority', 99)
            target_cities = set(city.lower() for city in region.get('cities', []))
            
            # Filter companies for this state
            state_mask = df['State'].str.lower() == state_name.lower()
            state_df = df[state_mask].copy()
            
            if len(state_df) == 0:
                print(f"⚠️ No companies found for {state_name}")
                continue
            
            # Apply city filter if specified
            if target_cities:
                city_mask = state_df['City'].str.lower().isin(target_cities)
                state_df = state_df[city_mask]
            
            # Sort by rating if available, then by name
            if 'Rating' in state_df.columns:
                state_df = state_df.sort_values(['Rating', 'Company Name'], 
                                              ascending=[False, True])
            else:
                state_df = state_df.sort_values('Company Name')
            
            # Save to file
            output_file = DATA_DIR / f"{state_name.lower()}_companies.csv"
            state_df.to_csv(output_file, index=False)
            print(f"✅ Saved {len(state_df)} companies for {state_name}")
            print(f"   Priority: {priority}")
            print(f"   Cities: {', '.join(sorted(target_cities)) if target_cities else 'All'}")
            print(f"   Output: {output_file}")
        
        print("\n✨ Region filtering complete!")
        
    except Exception as e:
        print(f"\n❌ Error during filtering: {str(e)}")
        raise

if __name__ == "__main__":
    filter_companies()