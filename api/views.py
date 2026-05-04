from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# Import our custom components
from .serializers import RecommendationRequestSerializer
from .models import Farmer, Farm, SoilHealthSnapshot, FertilizerRecommendation

# Moved this to the top for cleaner architecture!
from .services import get_complete_soil_profile 

# ml_service.py has this function 
from .ml_service import generate_recommendation 

logger = logging.getLogger(__name__)

class FertilizerRecommendationView(APIView):
    """
    POST endpoint to process farm data, fetch soil metrics, 
    and return an AI-driven fertilizer recommendation.
    """

    def post(self, request):
        # 1. Validate the incoming data from the frontend
        serializer = RecommendationRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.error(f"Validation Error: {serializer.errors}")
            return Response({
                "status": "error",
                "message": "Invalid data provided.",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        data = serializer.validated_data

        try:
            # 2. Database Routing: Get or Create Farmer Profile
            farmer, _ = Farmer.objects.get_or_create(
                phone_number=data['phone_number'],
                defaults={'name': data['farmer_name'], 'region': data['region']}
            )

            # Get or Create Farm Profile
            farm, _ = Farm.objects.get_or_create(
                farmer=farmer,
                farm_name=data['farm_name'],
                defaults={
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                    'primary_crop': data['crop_type_name']
                }
            )

            # 3. Fetch Live External Data
            lat, lon = float(data['latitude']), float(data['longitude'])
            soil_data = get_complete_soil_profile(lat, lon)

            # 4. Save the snapshot to the database
            SoilHealthSnapshot.objects.create(
                farm=farm,
                ph_level=soil_data.get('ph'),
                nitrogen_content=soil_data.get('nitrogen'),
                soil_moisture=soil_data['moisture']
            )

            # 5. Run the Machine Learning Model
            ml_result = generate_recommendation(
                ph=soil_data['ph'], 
                nitrogen=soil_data['nitrogen'], 
                moisture=soil_data['moisture'], 
                crop_type_code=data['crop_type_code']
            )

            # 6. Save the Recommendation
            recommendation = FertilizerRecommendation.objects.create(
                farm=farm,
                recommended_fertilizer_type=ml_result['fertilizer'],
                application_rate_per_acre="50kg / Acre", # Hardcoded for MVP speed
                confidence_score=ml_result['confidence']
            )

            # 7. Return the winning JSON payload to the frontend
            return Response({
                "status": "success",
                "farm": farm.farm_name,
                "soil_insights": {
                    "ph_level": round(soil_data['ph'], 2),
                    "nitrogen": round(soil_data['nitrogen'], 2),
                    "moisture_percent": round(soil_data['moisture'], 2),
                    "temperature_c": round(soil_data['temperature'], 2),
                    "is_live_chemistry": soil_data['is_live_chemistry']
                },
                "actionable_recommendation": {
                    "fertilizer": recommendation.recommended_fertilizer_type,
                    "rate": recommendation.application_rate_per_acre,
                    "confidence": f"{recommendation.confidence_score}%"
                }
            }, status=status.HTTP_201_CREATED)

        # THIS IS WHAT WAS MISSING: The catch block!
        except Exception as e:
            logger.error(f"Internal Server Error during processing: {str(e)}")
            return Response({
                "status": "error",
                "message": "An internal processing error occurred.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# USSD APIs require csrf_exempt because Africa's Talking servers 
# don't have a Django CSRF token to send us.
@csrf_exempt
def ussd_callback(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        
        # 1. PRINT THE INCOMING DATA TO YOUR TERMINAL
        print("\n--- NEW USSD SESSION ---")
        print(f"Incoming AT Text: '{text}'")

        inputs = text.split('*') if text else []
        level = len(inputs) if text else 0
        
        print(f"Calculated Level: {level}")

        response = ""

        # 2. Level 0: The First Screen
        if level == 0:
            response = "CON Welcome to SoilSync AI.\nWhat crop are you planting?\n1. Maize\n2. Beans\n3. Wheat"
        
        # 3. Level 1: Ask for Region
        elif level == 1:
            response = "CON Select your region:\n1. Rift Valley\n2. Central\n3. Western"
            
        # 4. Level 2: The Magic (Run the AI)
        elif level == 2:
            crop_choice = inputs[0]
            region_choice = inputs[1]

            # Map user input to our ML codes (1=Maize, 2=Beans, 3=Wheat)
            crop_code = int(crop_choice) if crop_choice in ['1', '2', '3'] else 1
            
            # Map region to demo coordinates (Hackathon speed!)
            # 1: Rift Valley (Egerton), 2: Central (Nyeri), 3: Western (Kakamega)
            if region_choice == '2':
                demo_lat, demo_lon = -0.4167, 36.9500 # Central
            elif region_choice == '3':
                demo_lat, demo_lon = 0.2833, 34.7500 # Western
            else:
                demo_lat, demo_lon = -0.3700, 35.9300 # Rift Valley (Egerton Default)

            # Fetch the soil profile (this uses your resilient simulated fallback if satellites are down)
            from .services import get_complete_soil_profile
            from .ml_service import generate_recommendation
            
            soil_data = get_complete_soil_profile(demo_lat, demo_lon)

            # Run the ML Model!
            ml_result = generate_recommendation(
                ph=soil_data['ph'], 
                nitrogen=soil_data['nitrogen'], 
                moisture=soil_data['moisture'], 
                crop_type_code=crop_code
            )

            fertilizer = ml_result['fertilizer']
            confidence = ml_result['confidence']

            # END the session with the AI result format for SMS
            response = f"END SoilSync AI Result:\nCrop: Option {crop_choice}\nRec: {fertilizer}\nRate: 50kg/Acre\nConf: {confidence}%\nMoisture: {soil_data['moisture']}%"

        # 5. PRINT THE OUTGOING DATA TO YOUR TERMINAL
        print(f"Outgoing Response: '{response}'")
        print("------------------------\n")

        return HttpResponse(response, content_type='text/plain')

    # Fallback for web browser GET requests
    return HttpResponse("USSD Endpoint Active.", content_type='text/plain')