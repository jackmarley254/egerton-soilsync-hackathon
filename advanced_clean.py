import pandas as pd
import numpy as np
import re

def extract_fertilizer(text):
    """Extracts the primary fertilizer class for the AI to predict."""
    if pd.isna(text): return np.nan
    text = str(text).upper()
    if "23:23:0" in text: return "NPK 23:23:0"
    elif "17:17:17" in text: return "NPK 17:17:17"
    elif "DAP" in text or "DIAMMONIUM PHOSPHATE" in text: return "DAP"
    elif "CAN" in text or "CALCIUM AMMONIUM NITRATE" in text: return "CAN"
    elif "UREA" in text: return "Urea"
    elif "MANURE" in text or "COMPOST" in text: return "Manure / Compost"
    return "Custom Blend"

print("Loading raw dataset...")
df = pd.read_csv('soil_dataset_4_counties.csv')

# ==========================================
# PHASE 1: SMART GPS IMPUTATION
# ==========================================
print("Running geographic triangulation...")

# Hardcoded centroids just in case a county has absolutely zero GPS data
county_centroids = {
    'Uasin Gishu': {'lat': 0.5143, 'lon': 35.2697},
    'Trans Nzoia': {'lat': 1.0581, 'lon': 34.9593},
    'Bungoma': {'lat': 0.5695, 'lon': 34.5584},
    'Kericho': {'lat': -0.3689, 'lon': 35.2889}
}

# Fill missing final_Latitude/Longitude using the hardcoded centroids
def fill_gps(row):
    if pd.isna(row['final_Latitude']) or pd.isna(row['final_Longitude']):
        county = row['county']
        if county in county_centroids:
            return pd.Series([county_centroids[county]['lat'], county_centroids[county]['lon']])
    return pd.Series([row['final_Latitude'], row['final_Longitude']])

df[['final_Latitude', 'final_Longitude']] = df.apply(fill_gps, axis=1)

# ==========================================
# PHASE 2: FULL SPECTRUM SOIL CHEMISTRY
# ==========================================
print("Extracting full macronutrient profile...")

# We are keeping ALL major nutrients now
numeric_cols = [
    'soil_pH', 'total_Nitrogen_percent_', 'phosphorus_Olsen_ppm', 
    'potassium_meq_percent_', 'total_Org_Carbon_percent_', 
    'calcium_meq_percent_', 'magnesium_meq_percent_'
]

# Advanced Imputation: Fill missing nutrients with the MEDIAN OF THAT SPECIFIC COUNTY
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
    # Group by county and fill NaNs with the county's average for that specific nutrient
    df[col] = df.groupby('county')[col].transform(lambda x: x.fillna(x.median()))
    # If any are still missing (e.g., whole county missing a mineral), use global median
    df[col] = df[col].fillna(df[col].median())

# ==========================================
# PHASE 3: CROP & ADVICE PRESERVATION
# ==========================================
print("Preserving rich agronomic advice...")

# Clean up crops (take the first primary crop)
df['crop_name'] = df['crop'].astype(str).apply(lambda x: x.split(',')[0].strip().title())

# Extract the ML target label
df['target_fertilizer'] = df['fertilizer_Recommendation'].apply(extract_fertilizer)

# Drop rows we can't train on
df_clean = df.dropna(subset=['fertilizer_Recommendation'])
df_clean = df_clean[df_clean['target_fertilizer'] != "Custom Blend"]

# ==========================================
# PHASE 4: THE FINAL EXPORT
# ==========================================
final_columns = [
    'county', 'final_Latitude', 'final_Longitude', 'crop_name',
    'soil_pH', 'total_Nitrogen_percent_', 'phosphorus_Olsen_ppm', 
    'potassium_meq_percent_', 'total_Org_Carbon_percent_', 
    'calcium_meq_percent_', 'magnesium_meq_percent_',
    'target_fertilizer', 'fertilizer_Recommendation' # We keep the raw paragraph!
]

# Rename to clean variable names for Django
df_export = df_clean[final_columns].rename(columns={
    'final_Latitude': 'latitude',
    'final_Longitude': 'longitude',
    'total_Nitrogen_percent_': 'nitrogen',
    'phosphorus_Olsen_ppm': 'phosphorus',
    'potassium_meq_percent_': 'potassium',
    'total_Org_Carbon_percent_': 'organic_carbon',
    'calcium_meq_percent_': 'calcium',
    'magnesium_meq_percent_': 'magnesium',
    'fertilizer_Recommendation': 'rich_advice_text'
})

df_export.to_csv('advanced_soil_data.csv', index=False)

print(f"\n✅ SUCCESS: Preserved {len(df_export)} fully enriched rows.")
print("Saved to 'advanced_soil_data.csv'")
print("\nFeatures now available for AI Training:")
print(['pH', 'N', 'P', 'K', 'C', 'Ca', 'Mg'])