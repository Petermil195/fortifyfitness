from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import AssessmentSerializer, AssessmentResultSerializer
from .models import Assessment
from .scoring_engine import ScoringEngine
from .fortify_scoring_criteria import FORTIFY_7_EXERCISES, get_all_exercises
from .email_service import send_assessment_summary_email


@api_view(['GET'])
def get_exercise_scoring_criteria(request):
    """
    Get the complete Fortify 7 exercise scoring criteria.
    No authentication required - this is public reference data.
    
    GET /api/assessment/exercises/
    """
    exercises = get_all_exercises()
    
    response_data = {
        'total_exercises': len(exercises),
        'max_total_score': 21,
        'exercises': [
            {
                'id': exercise_id,
                'name': exercise['name'],
                'order': exercise['order'],
                'max_score': exercise['max_score'],
                'notes': exercise['notes'],
                'scoring_levels': [
                    {
                        'score': score,
                        'description': description
                    }
                    for score, description in exercise['scoring_criteria'].items()
                ]
            }
            for exercise_id, exercise in FORTIFY_7_EXERCISES.items()
        ]
    }
    
    # Sort by order
    response_data['exercises'].sort(key=lambda x: x['order'])
    
    return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_assessment(request):
    """
    Submit comprehensive fitness assessment with all domains.
    Calculates competency level, composite score, and identifies injury flags.
    Automatically generates personalized workout program.
    
    POST /api/assessment/submit/
    """
    print(f"DEBUG: Assessment data received: {request.data}")
    serializer = AssessmentSerializer(data=request.data)
    
    if serializer.is_valid():
        # Save assessment (scoring is handled in serializer.create via ScoringEngine)
        assessment = serializer.save(user=request.user)
        
        # Get detailed scoring results
        scoring_engine = ScoringEngine(assessment)
        results = scoring_engine.process()
        
        # AUTO-GENERATE PROGRAM based on assessment
        try:
            from apps.programs.program_generator import ProgramGenerator
            
            program_gen = ProgramGenerator(request.user, assessment)
            program = program_gen.generate_program()
            
            program_data = {
                'id': program.id,
                'name': program.name,
                'template_name': program.template_name,
                'frequency': program.frequency,
                'competency_level': program.competency_level,
                'days': [
                    {
                        'day_number': day.day_number,
                        'focus': day.focus,
                        'num_exercises': day.exercises.count(),
                        'exercises': [
                            {
                                'id': ex.exercise.id,
                                'name': ex.exercise.name,
                                'sets': ex.sets,
                                'reps': ex.reps,
                                'rest_seconds': ex.rest_seconds,
                            }
                            for ex in day.exercises.all()
                        ]
                    }
                    for day in program.days.all()
                ]
            }
        except Exception as e:
            print(f"ERROR generating program: {str(e)}")
            program_data = {'error': f'Program generation failed: {str(e)}'}
        
        # Prepare response
        response_data = {
            'message': 'Assessment submitted successfully',
            'assessment': AssessmentSerializer(assessment).data,
            'results': {
                'assessment_score': results['assessment_score'],
                'assessment_percent': results['assessment_percent'],
                'questionnaire_score': results['questionnaire_score'],
                'questionnaire_percent': results['questionnaire_percent'],
                'recovery_score': results['recovery_score'],
                'recovery_percent': results['recovery_percent'],
                'composite_score': results['composite_score'],
                'competency_level': results['competency_level'],
                'competency_label': results['competency_label'],
                'injury_flags': results['injury_flags'],
                'flag_count': results['flag_count'],
                'safety_mode_count': results['safety_mode_count'],
                'recommendations': results['recommendations'],
            },
            'program': program_data,
        }

        # Send assessment summary email to user and cc internal recipient.
        try:
            send_assessment_summary_email(request.user, response_data['results'])
            response_data['email_sent'] = True
        except Exception as e:
            print(f"ERROR sending assessment summary email: {str(e)}")
            response_data['email_sent'] = False
            response_data['email_error'] = 'Assessment saved, but email delivery failed.'
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    print(f"DEBUG: Serializer errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assessments(request):
    """
    Get all assessments for the current user.
    
    GET /api/assessment/list/
    """
    assessments = Assessment.objects.filter(user=request.user)
    serializer = AssessmentSerializer(assessments, many=True)
    
    return Response({
        'count': assessments.count(),
        'assessments': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_assessment(request):
    """
    Get the latest assessment for the current user with detailed results.
    
    GET /api/assessment/latest/
    """
    try:
        assessment = Assessment.objects.filter(user=request.user).latest('created_at')
        
        # Get fresh scoring results
        scoring_engine = ScoringEngine(assessment)
        results = scoring_engine.process()
        
        response_data = {
            'assessment': AssessmentSerializer(assessment).data,
            'results': {
                'assessment_score': results['assessment_score'],
                'assessment_percent': results['assessment_percent'],
                'questionnaire_score': results['questionnaire_score'],
                'questionnaire_percent': results['questionnaire_percent'],
                'recovery_score': results['recovery_score'],
                'recovery_percent': results['recovery_percent'],
                'composite_score': results['composite_score'],
                'competency_level': results['competency_level'],
                'competency_label': results['competency_label'],
                'injury_flags': results['injury_flags'],
                'flag_count': results['flag_count'],
                'safety_mode_count': results['safety_mode_count'],
                'recommendations': results['recommendations'],
            }
        }
        
        return Response(response_data)
    
    except Assessment.DoesNotExist:
        return Response(
            {'message': 'No assessment found for this user'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assessment_by_id(request, assessment_id):
    """
    Get a specific assessment by ID with detailed results.
    
    GET /api/assessment/<id>/
    """
    try:
        assessment = Assessment.objects.get(id=assessment_id, user=request.user)
        
        # Get fresh scoring results
        scoring_engine = ScoringEngine(assessment)
        results = scoring_engine.process()
        
        response_data = {
            'assessment': AssessmentSerializer(assessment).data,
            'results': {
                'assessment_score': results['assessment_score'],
                'assessment_percent': results['assessment_percent'],
                'questionnaire_score': results['questionnaire_score'],
                'questionnaire_percent': results['questionnaire_percent'],
                'recovery_score': results['recovery_score'],
                'recovery_percent': results['recovery_percent'],
                'composite_score': results['composite_score'],
                'competency_level': results['competency_level'],
                'competency_label': results['competency_label'],
                'injury_flags': results['injury_flags'],
                'flag_count': results['flag_count'],
                'safety_mode_count': results['safety_mode_count'],
                'recommendations': results['recommendations'],
            }
        }
        
        return Response(response_data)
    
    except Assessment.DoesNotExist:
        return Response(
            {'error': 'Assessment not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_contraindications(request):
    """
    Get injury contraindications from latest assessment.
    
    GET /api/assessment/contraindications/
    """
    try:
        latest_assessment = Assessment.objects.filter(user=request.user).latest('created_at')
        injury_flags = latest_assessment.get_injury_flags()
        
        return Response({
            'injury_flags': injury_flags,
            'flag_count': latest_assessment.flag_count,
            'safety_mode_count': latest_assessment.safety_mode_count,
            'note': 'These injury flags will be considered when designing your workout program.'
        })
    
    except Assessment.DoesNotExist:
        return Response(
            {'message': 'No assessment found for this user'},
            status=status.HTTP_404_NOT_FOUND
        )
        
        # Generate contraindications
        engine = ContraindicationEngine(
            user_injuries=injuries,
            medical_conditions=profile.medical_conditions,
            pain_areas=profile.pain_areas
        )
        
        safety_report = engine.get_safety_report()
        
        return Response(safety_report)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
