from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Question
from .serializers import QuestionSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    """
    API ViewSet para gestionar preguntas de estudiantes.

    Endpoints:
        GET    /api/questions/                  - Listar preguntas
        POST   /api/questions/                  - Crear pregunta
        GET    /api/questions/{id}/              - Detalle de pregunta
        PUT    /api/questions/{id}/              - Actualizar pregunta
        DELETE /api/questions/{id}/              - Eliminar pregunta
        PATCH  /api/questions/{id}/mark_spoken/  - Marcar como reproducida
    """
    serializer_class = QuestionSerializer

    def get_queryset(self):
        """Filtra preguntas por firebase_uid si se proporciona."""
        queryset = Question.objects.all()
        firebase_uid = self.request.query_params.get('firebase_uid')
        session_name = self.request.query_params.get('session')

        if firebase_uid:
            queryset = queryset.filter(firebase_uid=firebase_uid)
        if session_name:
            queryset = queryset.filter(session_name=session_name)

        return queryset

    @action(detail=True, methods=['patch'])
    def mark_spoken(self, request, pk=None):
        """Marca una pregunta como reproducida con voz sintética."""
        question = self.get_object()
        question.was_spoken = True
        question.save()
        serializer = self.get_serializer(question)
        return Response(serializer.data)
