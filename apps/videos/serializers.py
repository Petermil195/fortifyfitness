from rest_framework import serializers
from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for Video model"""
    
    class Meta:
        model = Video
        fields = '__all__'
        read_only_fields = ['id', 'user', 'uploaded_at']
