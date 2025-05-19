import pandas as pd
from pathlib import Path
import re

# Constants
REQUIRED_COLUMNS = ['Company Name', 'City', 'State', 'Description']
OPTIONAL_COLUMNS = ['Website', 'Rating', 'Years in Business']
VALID_STATES = {
    'Texas', 'Florida', 'California', 'Arizona', 'Colorado', 
    'Nevada', 'North Carolina'  # Added more states
}

def load_csv():
    """Load the solar companies CSV file"""
    base_dir = Path(__file__).parent.parent
    attempts = [
        base_dir / 'data' / 'solar_companies.csv',
        base_dir / 'src' / 'solar_companies.csv',
        Path(__file__).parent / 'solar_companies.csv'
    ]
    
    for path in attempts:
        try:
            if path.exists():
                print(f"✅ Found data file at: {path}")
                return pd.read_csv(path)
        except Exception as e:
            print(f"❌ Failed to load {path}: {str(e)}")
    
    raise FileNotFoundError("Could not find solar_companies.csv in any expected location")

def validate_website(url):
    """Validate website URL format"""
    if pd.isna(url) or url == '':
        return True
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

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

def validate_rating(rating_str):
    """Validate rating format"""
    if pd.isna(rating_str):
        return True
        
    rating = parse_rating(rating_str)
    if rating is None:
        return False
        
    return 0 <= rating <= 5

def validate():
    """Validate the solar companies data"""
    try:
        df = load_csv()
        errors = []
        
        # Check required columns
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        
        # Validate each row
        for idx, row in df.iterrows():
            row_num = idx + 2  # Account for 1-based indexing and header row
            
            # Check for empty required fields
            for col in REQUIRED_COLUMNS:
                if col in df.columns and pd.isna(row[col]):
                    errors.append(f"Row {row_num}: Missing value for required field '{col}'")
            
            # Validate state
            if 'State' in df.columns and not pd.isna(row['State']):
                if row['State'] not in VALID_STATES:
                    errors.append(f"Row {row_num}: Invalid state '{row['State']}'")
            
            # Validate website format
            if 'Website' in df.columns and not validate_website(row['Website']):
                errors.append(f"Row {row_num}: Invalid website URL format '{row['Website']}'")
            
            # Validate rating
            if 'Rating' in df.columns and not validate_rating(row['Rating']):
                errors.append(f"Row {row_num}: Invalid rating value '{row['Rating']}' (must be in format X.X or X.X/5.0)")
            
            # Validate years in business
            if 'Years in Business' in df.columns and not pd.isna(row['Years in Business']):
                try:
                    years = int(row['Years in Business'])
                    if years < 0 or years > 200:  # Reasonable range
                        errors.append(f"Row {row_num}: Invalid years in business '{years}'")
                except (ValueError, TypeError):
                    errors.append(f"Row {row_num}: Years in business must be a number")
        
        if errors:
            print("\n❌ Validation failed with the following errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("\n✅ Data validation passed successfully!")
        print(f"Found {len(df)} companies across {df['State'].nunique()} states")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during validation: {str(e)}")
        return False

if __name__ == "__main__":
    validate()