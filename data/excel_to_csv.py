import pandas as pd

# Read the Excel file
df = pd.read_excel('solar_companies.xlsx')

# Save as CSV
df.to_csv('solar_companies.csv', index=False)

print("Conversion complete! CSV saved as 'solar_companies.csv'")