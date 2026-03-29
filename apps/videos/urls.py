from django.urls import path
from . import views

app_name = 'videos'

urlpatterns = [
    # Video endpoints
    path('upload/', views.upload_video, name='upload'),
]
