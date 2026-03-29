from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ExerciseSerializer
from .models import Exercise
from .filter_engine import FilterEngine
from .contraindication_engine import ContraindicationEngine
from apps.assessments.models import Assessment


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_exercises(request):
    """
    List all FMS assessment protocol exercises (instructional videos only).
    
    These are videos that teach users how to properly perform and score
    each movement in the 10-movement assessment. This is NOT the workout exercise library.
    
    GET /api/exercises/
    """
    # Only return assessment protocol exercises
    exercises = Exercise.objects.filter(exercise_type='assessment')
    serializer = ExerciseSerializer(exercises, many=True)
    
    return Response({
        'count': exercises.count(),
        'type': 'assessment_protocol',
        'description': 'Videos teaching FMS movement protocol and self-scoring',
        'exercises': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_filtered_exercises(request):
    """
    Get exercises filtered by user's equipment, fitness level, and safety contraindications.
    
    GET /api/exercises/filtered/
    Query params:
        - equipment: comma-separated list (overrides user assessment)
        - fitness_level: beginner/intermediate/advanced (overrides user assessment)
        - include_unsafe: boolean (default: false) - include contraindicated exercises
    """
    # Get query parameters
    equipment_param = request.query_params.get('equipment', None)
    fitness_level_param = request.query_params.get('fitness_level', None)
    include_unsafe = request.query_params.get('include_unsafe', 'false').lower() == 'true'
    
    # Get user's assessment data
    equipment_list = None
    fitness_level = None
    injuries = None
    
    try:
        latest_assessment = Assessment.objects.filter(user=request.user).latest('created_at')
        equipment_list = latest_assessment.equipment
        fitness_level = latest_assessment.fitness_level or latest_assessment.experience_level
        injuries = latest_assessment.injuries
    except Assessment.DoesNotExist:
        pass
    
    # Override with query parameters if provided
    if equipment_param:
        equipment_list = equipment_param
    if fitness_level_param:
        fitness_level = fitness_level_param
    
    # Parse equipment
    if equipment_list:
        if isinstance(equipment_list, str):
            equipment = [e.strip() for e in equipment_list.split(',') if e.strip()]
        else:
            equipment = equipment_list
    else:
        equipment = []
    
    # Get all exercises
    exercises = Exercise.objects.all()
    
    # Apply equipment and fitness level filters
    filter_engine = FilterEngine(available_equipment=equipment)
    filtered_exercises = filter_engine.apply_all_filters(
        exercises,
        fitness_level=fitness_level
    )
    
    # Apply safety filters unless include_unsafe is true
    if not include_unsafe:
        profile = request.user.profile
        contraindication_engine = ContraindicationEngine(
            user_injuries=injuries or profile.injuries,
            medical_conditions=profile.medical_conditions,
            pain_areas=profile.pain_areas
        )
        filtered_exercises = contraindication_engine.filter_exercises(filtered_exercises)
    
    serializer = ExerciseSerializer(filtered_exercises, many=True)
    
    return Response({
        'count': len(filtered_exercises),
        'filters_applied': {
            'equipment': equipment,
            'fitness_level': fitness_level,
            'safety_filtering': not include_unsafe
        },
        'exercises': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_exercise_safety(request):
    """
    Check if specific exercises are safe for the user.
    
    POST /api/exercises/check-safety/
    Body: {
        "exercise_ids": [1, 2, 3]
    }
    """
    exercise_ids = request.data.get('exercise_ids', [])
    
    if not exercise_ids:
        return Response(
            {'error': 'exercise_ids required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get user profile and assessment data
    profile = request.user.profile
    injuries = profile.injuries
    
    try:
        latest_assessment = Assessment.objects.filter(user=request.user).latest('created_at')
        if latest_assessment.injuries:
            injuries = latest_assessment.injuries
    except Assessment.DoesNotExist:
        pass
    
    # Initialize contraindication engine
    engine = ContraindicationEngine(
        user_injuries=injuries,
        medical_conditions=profile.medical_conditions,
        pain_areas=profile.pain_areas
    )
    
    # Check each exercise
    results = []
    for exercise_id in exercise_ids:
        try:
            exercise = Exercise.objects.get(id=exercise_id)
            is_safe = engine.check_exercise_safety(exercise)
            safety_score = engine.get_exercise_safety_score(exercise)
            
            results.append({
                'exercise_id': exercise_id,
                'exercise_name': exercise.name,
                'is_safe': is_safe,
                'safety_score': safety_score,
                'warning': 'Exercise may not be suitable' if not is_safe else None
            })
        except Exercise.DoesNotExist:
            results.append({
                'exercise_id': exercise_id,
                'error': 'Exercise not found'
            })
    
    return Response({
        'results': results,
        'safety_report': engine.get_safety_report()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exercise_recommendations(request):
    """
    Get exercise recommendations based on user's fitness level and goals.
    
    GET /api/exercises/recommendations/
    """
    try:
        latest_assessment = Assessment.objects.filter(user=request.user).latest('created_at')
        fitness_level = latest_assessment.fitness_level or latest_assessment.experience_level
        equipment = latest_assessment.equipment
        injuries = latest_assessment.injuries
    except Assessment.DoesNotExist:
        return Response(
            {'message': 'Please complete an assessment first to get recommendations'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Parse equipment
    if equipment:
        if isinstance(equipment, str):
            equipment_list = [e.strip() for e in equipment.split(',') if e.strip()]
        else:
            equipment_list = equipment
    else:
        equipment_list = []
    
    # Get all exercises
    exercises = Exercise.objects.all()
    
    # Apply filters
    filter_engine = FilterEngine(available_equipment=equipment_list)
    filtered = filter_engine.apply_all_filters(exercises, fitness_level=fitness_level)
    
    # Apply safety filters
    profile = request.user.profile
    contraindication_engine = ContraindicationEngine(
        user_injuries=injuries or profile.injuries,
        medical_conditions=profile.medical_conditions,
        pain_areas=profile.pain_areas
    )
    safe_exercises = contraindication_engine.filter_exercises(filtered)
    
    # Limit to top recommendations
    recommended = safe_exercises[:20]
    
    serializer = ExerciseSerializer(recommended, many=True)
    
    return Response({
        'count': len(recommended),
        'fitness_level': fitness_level,
        'exercises': serializer.data
    })
