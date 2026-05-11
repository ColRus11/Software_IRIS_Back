from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import TranscriptionSession, GroupTranscriptionSession
from .serializers import TranscriptionSerializer, GroupTranscriptionSessionSerializer


class TranscriptionViewSet(viewsets.ModelViewSet):
    serializer_class   = TranscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TranscriptionSession.objects.filter(teacher=self.request.user)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class GroupTranscriptionViewSet(viewsets.ModelViewSet):
    serializer_class   = GroupTranscriptionSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GroupTranscriptionSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
