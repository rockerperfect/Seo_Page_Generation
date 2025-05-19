# Webflow CMS Import Files

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
