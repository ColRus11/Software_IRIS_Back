from rest_framework import serializers
from .models import EmergencyAlert


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EmergencyAlert
        fields = ['id', 'title', 'message', 'severity', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
