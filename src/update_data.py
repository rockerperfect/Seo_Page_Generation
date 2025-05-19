import pandas as pd
from pathlib import Path
import argparse
import sys

# Path Setup
DATA_DIR = Path(__file__).parent.parent / "data"
COMPANY_DATA = DATA_DIR / "solar_companies.csv"
REGION_DIR = DATA_DIR / "regions"

def load_or_create_csv(file_path):
    """Loads a CSV file or creates it with headers if missing"""
    if file_path.exists():
        return pd.read_csv(file_path)
    else:
        # Create new DataFrame with expected columns
        return pd.DataFrame(columns=[
            'name', 
            'city', 
            'state', 
            'website', 
            'description'
        ])

def add_company(name, city, state, website, description):
    """Adds/updates a company with validation"""
    df = load_or_create_csv(COMPANY_DATA)
    
    # Validation (fixed comparison logic)
    mask = df['name'].str.lower() == name.lower()
    if mask.any():
        print(f"⚠️ Updating existing company: {name}")
        df.loc[mask, ['name', 'city', 'state', 'website', 'description']] = [
            name, city, state, website, description
        ]
    else:
        new_row = pd.DataFrame([[name, city, state, website, description]], 
                             columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
    
    df.to_csv(COMPANY_DATA, index=False)
    update_regional_files(state)
    print(f"✅ Saved {name} to database")

def update_regional_files(state):
    """Updates region-specific CSV files"""
    REGION_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(COMPANY_DATA)
    region_df = df[df['state'].str.lower() == state.lower()]
    region_df.to_csv(REGION_DIR / f"{state.lower()}_companies.csv", index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    
    # Company Subcommand
    company_parser = subparsers.add_parser('company')
    company_parser.add_argument('--name', required=True)
    company_parser.add_argument('--city', required=True)
    company_parser.add_argument('--state', required=True)
    company_parser.add_argument('--website', default="")
    company_parser.add_argument('--description', default="")
    
    args = parser.parse_args()
    
    if args.command == 'company':
        add_company(args.name, args.city, args.state, 
                   args.website, args.description)
    else:
        parser.print_help()