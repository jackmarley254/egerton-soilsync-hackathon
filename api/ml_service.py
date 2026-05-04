import os
import joblib
import pandas as pd
from django.conf import settings

# Paths to your brain and memory bank
MODEL_PATH = os.path.join(settings.BASE_DIR, 'soilsync_ai_model.pkl')
DATA_PATH = os.path.join(settings.BASE_DIR, 'advanced_soil_data.csv')

# 1. Load the AI Model
try:
    soilsync_model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    soilsync_model = None
    print("WARNING: soilsync_ai_model.pkl not found!")

# 2. Load the Memory Bank (Rich Advice)
try:
    # We load this into memory once when the server starts so it's lightning fast
    advice_db = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    advice_db = None
    print("WARNING: advanced_soil_data.csv not found!")


def generate_recommendation(ph, nitrogen, moisture, crop_type_code):
    if soilsync_model is None:
        return {"fertilizer": "Model Offline", "confidence": 0.0, "advice": "Please contact extension officer."}

    # Safe baselines for the extra minerals the model expects
    baseline_P = 20.0   
    baseline_K = 0.5    
    baseline_C = 1.5    
    baseline_Ca = 3.0   
    baseline_Mg = 1.5   

    input_features = pd.DataFrame(
        [[ph, nitrogen, baseline_P, baseline_K, baseline_C, baseline_Ca, baseline_Mg, crop_type_code]], 
        columns=['soil_pH', 'nitrogen', 'phosphorus', 'potassium', 'organic_carbon', 'calcium', 'magnesium', 'crop_code']
    )
    
    # Run the prediction
    prediction = soilsync_model.predict(input_features)[0]
    probabilities = soilsync_model.predict_proba(input_features)[0]
    confidence = round(max(probabilities) * 100, 2)
    
    # 3. Fetch the Rich Advice!
    expert_advice = "Standard application recommended based on region." # Fallback
    
    if advice_db is not None:
        # Find all historical records where KALRO recommended this exact fertilizer
        matching_rows = advice_db[advice_db['target_fertilizer'] == prediction]
        
        if not matching_rows.empty:
            # Grab the first rich paragraph we find for this chemical
            raw_text = matching_rows['rich_advice_text'].iloc[0]
            
            # Clean up the text (remove messy \r\n characters from the raw CSV)
            expert_advice = str(raw_text).replace('\r', '').replace('\n', ' ').strip()
            
            # For USSD, we truncate it to ~120 characters so it fits on a small feature phone screen
            if len(expert_advice) > 120:
                expert_advice = expert_advice[:117] + "..."
    
    return {
        "fertilizer": prediction,
        "confidence": confidence,
        "advice": expert_advice
    }