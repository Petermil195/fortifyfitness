from rest_framework import serializers
from .models import Exercise


class ExerciseSerializer(serializers.ModelSerializer):
    """Serializer for Exercise model"""
    
    class Meta:
        model = Exercise
        fields = '__all__'
        read_only_fields = ['id']
