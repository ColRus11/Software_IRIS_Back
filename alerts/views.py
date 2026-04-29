from rest_framework import viewsets
from .models import EmergencyAlert
from .serializers import AlertSerializer

class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    queryset = EmergencyAlert.objects.filter(is_active=True)

    def perform_create(self, serializer):
        uid = self.request.META.get('HTTP_X_FIREBASE_UID', '')
        serializer.save(created_by=uid)
