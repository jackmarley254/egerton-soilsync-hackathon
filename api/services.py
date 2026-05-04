import requests
import logging
import random

logger = logging.getLogger(__name__)

def get_open_meteo_physics(lat, lon):
    """Fetches highly reliable live soil moisture and temperature."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["soil_moisture_0_to_7cm", "soil_temperature_0_to_7cm"],
        "timezone": "Africa/Nairobi"
    }
    try:
        response = requests.get(url, params=params, timeout=3)
        response.raise_for_status()
        data = response.json()
        
        # Safely extract moisture. If the API returns 'null' (None), default to 0.50
        moisture = data.get("current", {}).get("soil_moisture_0_to_7cm")
        if moisture is None:
            moisture = 0.50
            
        temp = data.get("current", {}).get("soil_temperature_0_to_7cm")
        if temp is None:
            temp = 22.0
        
        return {
            "moisture": round(moisture * 100, 2), # Now this math will never crash!
            "temperature": temp
        }
        
    # THIS stays exactly the same to catch Wi-Fi drops!
    except requests.exceptions.RequestException as e:
        logger.error(f"Open-Meteo failed: {e}")
        return {"moisture": 50.0, "temperature": 22.0}

def get_isric_chemistry(lat, lon):
    """Attempts to fetch live pH and Nitrogen. Returns None if server is down."""
    url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    params = {
        "lon": lon, "lat": lat,
        "property": ["phh2o", "nitrogen"],
        "depth": "0-5cm", "value": "mean"
    }
    try:
        response = requests.get(url, params=params, timeout=3)
        response.raise_for_status()
        data = response.json()
        
        properties = data.get('properties', {}).get('layers', [])
        results = {}
        for prop in properties:
            if prop['name'] == 'phh2o':
                raw_ph = prop['depths'][0]['values']['mean']
                results['ph'] = raw_ph / 10 if raw_ph else None
            elif prop['name'] == 'nitrogen':
                results['nitrogen'] = prop['depths'][0]['values']['mean']
                
        return results if results.get('ph') and results.get('nitrogen') else None

    except (requests.exceptions.RequestException, KeyError) as e:
        logger.warning(f"ISRIC SoilGrids down. Error: {e}")
        return None # Explicitly return None so our master function knows it failed

def get_complete_soil_profile(lat, lon):
    """
    THE ORCHESTRATOR: Combines physics and chemistry into one profile.
    This is what your views.py will call.
    """
    # 1. Get live physics
    physics = get_open_meteo_physics(lat, lon)
    
    # 2. Try to get live chemistry
    chemistry = get_isric_chemistry(lat, lon)
    
    # 3. Handle the chemistry fallback seamlessly
    if chemistry is None:
        logger.info("Injecting simulated chemistry data due to ISRIC outage.")
        chemistry = {
            "ph": round(random.uniform(5.5, 7.2), 2),
            "nitrogen": round(random.uniform(12.0, 28.0), 2),
            "is_live_chemistry": False
        }
    else:
        chemistry["is_live_chemistry"] = True
        
    # 4. Merge everything into one beautiful dictionary
    return {
        "ph": chemistry["ph"],
        "nitrogen": chemistry["nitrogen"],
        "moisture": physics["moisture"],
        "temperature": physics["temperature"],
        "is_live_chemistry": chemistry["is_live_chemistry"]
    }