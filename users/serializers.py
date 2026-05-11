from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model  = UserProfile
        fields = ['id', 'email', 'display_name', 'role', 'university', 'created_at']
        read_only_fields = ['id', 'email', 'created_at']
