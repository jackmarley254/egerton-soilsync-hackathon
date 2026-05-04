from django.urls import path
from .views import FertilizerRecommendationView, ussd_callback

urlpatterns = [
    path('v1/recommendation/', FertilizerRecommendationView.as_view(), name='get_recommendation'),
    path('ussd/', ussd_callback, name='ussd_callback'),
]