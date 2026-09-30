from django.urls import path, include

urlpatterns = [
    path('auth/', include('allauth.headless.urls')),  # <-- Include the headless auth URLs
    path('social/', include('allauth.socialaccount.urls')),  # <-- Add this line to include social account URLs
]