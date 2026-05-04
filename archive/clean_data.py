import pandas as pd
import numpy as np
import re

def extract_fertilizer(text):
    """
    Scans the recommendation paragraph and extracts the primary fertilizer.
    Prioritizes NPK and DAP (planting fertilizers) over CAN/Urea (top-dressing),
    but captures whatever is available.
    """
    if pd.isna(text):
        return np.nan
        
    text = str(text).upper()
    
    # Priority 1: Compound / Planting Fertilizers
    if "23:23:0" in text:
        return "NPK 23:23:0"
    elif "17:17:17" in text:
        return "NPK 17:17:17"
    elif "DAP" in text or "DIAMMONIUM PHOSPHATE" in text:
        return "DAP"
    
    # Priority 2: Top Dressing
    elif "CAN" in text or "CALCIUM AMMONIUM NITRATE" in text:
        return "CAN"
    elif "UREA" in text:
        return "Urea"
        
    # Priority 3: Organic/Others
    elif "MANURE" in text or "COMPOST" in text:
        return "Manure / Compost"
    
    return "Custom Blend" # Fallback if no standard keyword is found

def clean_soil_data(input_csv, output_csv):
    print(f"Loading raw data from {input_csv}...")
    df = pd.read_csv(input_csv)
    
    # 1. Feature Selection: Keep only what the ML model actually needs
    core_columns = [
        'county', 'crop', 'soil_pH', 'total_Nitrogen_percent_', 
        'total_Org_Carbon_percent_', 'phosphorus_Olsen_ppm', 
        'potassium_meq_percent_', 'fertilizer_Recommendation'
    ]
    
    # Safely select columns that exist in the dataframe
    existing_cols = [col for col in core_columns if col in df.columns]
    df_clean = df[existing_cols].copy()
    
    print(f"Initial rows: {len(df_clean)}")
    
    # 2. Drop rows where we have no target recommendation (useless for AI training)
    df_clean = df_clean.dropna(subset=['fertilizer_Recommendation'])
    print(f"Rows after dropping missing recommendations: {len(df_clean)}")
    
    # 3. Clean the 'crop' column
    # Some rows have "Capsicum, tomato, passion fruits". We'll grab the first primary crop.
    df_clean['crop'] = df_clean['crop'].astype(str).apply(lambda x: x.split(',')[0].strip().title())
    
    # 4. Handle Missing Soil Data (Imputation)
    # We replace missing numbers with the median value so it doesn't break the ML model
    numeric_cols = ['soil_pH', 'total_Nitrogen_percent_', 'total_Org_Carbon_percent_', 'potassium_meq_percent_']
    for col in numeric_cols:
        if col in df_clean.columns:
            # Convert to numeric just in case there are hidden text characters
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            median_val = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(median_val)
            
    # Phosphorus Olsen has some text like "Trace", let's force it to numeric
    if 'phosphorus_Olsen_ppm' in df_clean.columns:
        df_clean['phosphorus_Olsen_ppm'] = pd.to_numeric(df_clean['phosphorus_Olsen_ppm'], errors='coerce')
        df_clean['phosphorus_Olsen_ppm'] = df_clean['phosphorus_Olsen_ppm'].fillna(df_clean['phosphorus_Olsen_ppm'].median())
        
    # 5. Extract the AI Target Labels from the paragraphs
    print("Extracting exact fertilizer targets using NLP rules...")
    df_clean['target_fertilizer'] = df_clean['fertilizer_Recommendation'].apply(extract_fertilizer)
    
    # Drop rows that fell into "Custom Blend" or missing to keep the AI focused on major fertilizers
    df_clean = df_clean[df_clean['target_fertilizer'] != "Custom Blend"]
    
    # Rename columns for easier use in our ML script later
    df_clean = df_clean.rename(columns={
        'total_Nitrogen_percent_': 'nitrogen',
        'potassium_meq_percent_': 'potassium',
        'total_Org_Carbon_percent_': 'organic_carbon',
        'phosphorus_Olsen_ppm': 'phosphorus'
    })
    
    # Save the polished dataset
    df_clean.to_csv(output_csv, index=False)
    
    print("\n--- Cleaning Complete! ---")
    print(f"Final clean rows ready for AI: {len(df_clean)}")
    print("\nFertilizer Distribution:")
    print(df_clean['target_fertilizer'].value_counts())
    print(f"\nSaved clean dataset to {output_csv}")

if __name__ == "__main__":
    # Ensure your raw dataset is named exactly this in the same folder
    clean_soil_data('soil_dataset_4_counties.csv', 'clean_soil_data.csv')