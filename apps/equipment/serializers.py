from rest_framework import serializers
from .models import Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for Equipment model"""
    
    class Meta:
        model = Equipment
        fields = '__all__'
        read_only_fields = ['id']
