from django.db import models

class Farmer(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True, help_text="Used for SMS/USSD routing")
    region = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

class Farm(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='farms')
    farm_name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    primary_crop = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.farm_name} - {self.primary_crop}"

class SoilHealthSnapshot(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='soil_snapshots')
    timestamp = models.DateTimeField(auto_now_add=True)
    ph_level = models.FloatField(null=True, blank=True)
    nitrogen_content = models.FloatField(null=True, blank=True)
    soil_moisture = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Snapshot: {self.farm.farm_name} on {self.timestamp.strftime('%Y-%m-%d')}"

class FertilizerRecommendation(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='recommendations')
    recommended_fertilizer_type = models.CharField(max_length=100)
    application_rate_per_acre = models.CharField(max_length=50)
    confidence_score = models.FloatField(help_text="AI model confidence percentage")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recommended_fertilizer_type} for {self.farm.farm_name}"