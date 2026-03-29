from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User authentication endpoints
    path('register/', views.register_user, name='register'),
    path('profile/', views.get_profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Detailed profile (intake form) endpoints
    path('profile/details/', views.get_user_profile_details, name='profile_details'),
    path('profile/details/update/', views.update_profile_details, name='update_profile_details'),
]
