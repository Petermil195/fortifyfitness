from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer, 
    UpdateProfileSerializer,
    UserProfileSerializer
)


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user and return JWT tokens.

    POST /api/auth/register/
    Body: {
        "email": "user@example.com",
        "password": "secure_password",
        "password2": "secure_password",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    import traceback

    print(f"DEBUG: Request method: {request.method}")
    print(f"DEBUG: Request data: {request.data}")
    print(f"DEBUG: Request content-type: {request.content_type}")

    serializer = UserRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        try:
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"REGISTRATION EXCEPTION: {type(e).__name__}: {e}")
            print(f"TRACEBACK:\n{traceback.format_exc()}")
            return Response(
                {'error': f'{type(e).__name__}: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    print(f"DEBUG: Serializer errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """
    Get current user profile with all information.
    
    GET /api/auth/profile/
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Update current user profile.
    
    PUT/PATCH /api/auth/profile/update/
    """
    serializer = UpdateProfileSerializer(
        request.user, 
        data=request.data, 
        partial=request.method == 'PATCH'
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(request.user).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile_details(request):
    """
    Get detailed user profile information (intake form data).
    
    GET /api/auth/profile/details/
    """
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_details(request):
    """
    Update detailed user profile information (intake form data).
    
    PUT/PATCH /api/auth/profile/details/update/
    """
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(
            profile,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile details updated successfully',
                'profile': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
