from rest_framework import serializers
from .models import EmergencyAlert

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyAlert
        fields = '__all__'
        read_only_fields = ['created_at']
