from rest_framework import serializers
from .models import TranscriptionSession, GroupTranscriptionSession, GroupTranscriptionEntry


class TranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TranscriptionSession
        fields = ['id', 'session_name', 'transcript', 'created_at']
        read_only_fields = ['id', 'created_at']


class GroupTranscriptionEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model  = GroupTranscriptionEntry
        fields = ['id', 'speaker_index', 'speaker_label', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']


class GroupTranscriptionSessionSerializer(serializers.ModelSerializer):
    entries = GroupTranscriptionEntrySerializer(many=True)

    class Meta:
        model  = GroupTranscriptionSession
        fields = ['id', 'session_name', 'created_at', 'entries']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        entries_data = validated_data.pop('entries', [])
        session = GroupTranscriptionSession.objects.create(**validated_data)
        for entry in entries_data:
            GroupTranscriptionEntry.objects.create(session=session, **entry)
        return session
