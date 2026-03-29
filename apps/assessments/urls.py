from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    # Exercise reference data (no auth required)
    path('exercises/', views.get_exercise_scoring_criteria, name='exercises'),
    # Assessment endpoints
    path('submit/', views.submit_assessment, name='submit'),
    path('list/', views.get_assessments, name='list'),
    path('latest/', views.get_latest_assessment, name='latest'),
    path('<int:assessment_id>/', views.get_assessment_by_id, name='detail'),
    path('contraindications/', views.get_contraindications, name='contraindications'),
]
