from django.urls import path
from . import views

app_name = 'programs'

urlpatterns = [
    # Program endpoints
    path('current/', views.get_current_program, name='current'),
]
