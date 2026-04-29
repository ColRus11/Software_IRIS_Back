from rest_framework import viewsets
from .models import TranscriptionSession
from .serializers import TranscriptionSerializer

class TranscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = TranscriptionSerializer
    queryset = TranscriptionSession.objects.all()

    def get_queryset(self):
        uid = self.request.query_params.get('teacher_uid')
        if uid:
            return self.queryset.filter(teacher_uid=uid)
        return self.queryset
