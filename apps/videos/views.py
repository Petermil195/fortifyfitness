from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import VideoSerializer
from .models import Video


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_video(request):
    """
    Upload assessment video
    
    POST /api/videos/upload/
    """
    # TODO: Implement video upload with local storage
    # For now, just accept the data
    
    serializer = VideoSerializer(data=request.data)
    
    if serializer.is_valid():
        video = serializer.save(user=request.user)
        
        return Response({
            'message': 'Video uploaded successfully',
            'video': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
