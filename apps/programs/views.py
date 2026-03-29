from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProgramSerializer
from .models import Program


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_program(request):
    """
    Get user's current active program
    
    GET /api/program/current/
    """
    try:
        program = Program.objects.filter(
            user=request.user,
            is_active=True
        ).latest('created_at')
        
        serializer = ProgramSerializer(program)
        return Response(serializer.data)
    
    except Program.DoesNotExist:
        return Response({
            'message': 'No active program found. Please complete an assessment first.'
        }, status=status.HTTP_404_NOT_FOUND)
