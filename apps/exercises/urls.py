from django.urls import path
from . import views

app_name = 'exercises'

urlpatterns = [
    # Exercise endpoints
    path('', views.list_exercises, name='list'),
    path('filtered/', views.get_filtered_exercises, name='filtered'),
    path('check-safety/', views.check_exercise_safety, name='check_safety'),
    path('recommendations/', views.get_exercise_recommendations, name='recommendations'),
]
