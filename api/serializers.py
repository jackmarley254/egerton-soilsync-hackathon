from rest_framework import serializers

class RecommendationRequestSerializer(serializers.Serializer):
    """
    Validates the incoming JSON payload from the frontend.
    """
    farmer_name = serializers.CharField(max_length=100, required=True)
    phone_number = serializers.CharField(max_length=15, required=True)
    region = serializers.CharField(max_length=100, default="Nakuru")
    farm_name = serializers.CharField(max_length=100, default="Main Plot")
    
    # We need highly precise decimals for GPS coordinates
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    
    crop_type_name = serializers.CharField(max_length=50, required=True)
    crop_type_code = serializers.IntegerField(required=True)

    def validate_phone_number(self, value):
        """
        Custom validation to ensure the phone number looks somewhat realistic
        for our future USSD/SMS integration.
        """
        if len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        return value