from django.contrib import admin
from .models import Farmer, Farm, SoilHealthSnapshot, FertilizerRecommendation

# Customizing the admin view for better readability
@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'region', 'created_at')
    search_fields = ('name', 'phone_number')

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('farm_name', 'farmer', 'primary_crop', 'latitude', 'longitude')
    list_filter = ('primary_crop',)

@admin.register(SoilHealthSnapshot)
class SoilHealthSnapshotAdmin(admin.ModelAdmin):
    list_display = ('farm', 'ph_level', 'nitrogen_content', 'timestamp')

@admin.register(FertilizerRecommendation)
class FertilizerRecommendationAdmin(admin.ModelAdmin):
    list_display = ('farm', 'recommended_fertilizer_type', 'confidence_score', 'created_at')
    list_filter = ('recommended_fertilizer_type',)