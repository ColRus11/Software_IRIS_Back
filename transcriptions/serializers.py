from rest_framework import serializers
from .models import TranscriptionSession

class TranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranscriptionSession
        fields = '__all__'
        read_only_fields = ['created_at']
