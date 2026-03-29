from rest_framework import serializers
from .models import Program, ProgramExercise


class ProgramExerciseSerializer(serializers.ModelSerializer):
    """Serializer for ProgramExercise model"""
    
    class Meta:
        model = ProgramExercise
        fields = '__all__'


class ProgramSerializer(serializers.ModelSerializer):
    """Serializer for Program model"""
    exercises = ProgramExerciseSerializer(many=True, read_only=True)
    
    class Meta:
        model = Program
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at']
