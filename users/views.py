from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import UserProfile
from .serializers import UserProfileSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()

    def get_queryset(self):
        uid = self.request.query_params.get('firebase_uid')
        if uid:
            return self.queryset.filter(firebase_uid=uid)
        return self.queryset

    @action(detail=False, methods=['get','post'], url_path='profile')
    def profile(self, request):
        """GET|POST /api/users/profile/?firebase_uid=XXX"""
        uid = request.query_params.get('firebase_uid') or request.data.get('firebase_uid')
        if not uid:
            return Response({'error': 'firebase_uid requerido'}, status=400)

        if request.method == 'GET':
            try:
                profile = UserProfile.objects.get(firebase_uid=uid)
                return Response(UserProfileSerializer(profile).data)
            except UserProfile.DoesNotExist:
                return Response({'error': 'Perfil no encontrado'}, status=404)

        # POST — crear o actualizar
        profile, _ = UserProfile.objects.get_or_create(firebase_uid=uid)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
