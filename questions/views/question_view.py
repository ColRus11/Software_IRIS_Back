from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from questions.schemas.question_schema import QuestionSerializer
from questions.services import question_service


class QuestionViewSet(viewsets.ModelViewSet):
    """API ViewSet para gestionar preguntas de estudiantes.

    Responsabilidad única: Manejar HTTP requests/responses.
    Delega toda la lógica de negocio al servicio y el acceso
    a datos al repositorio.

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
        """Delega el filtrado al servicio."""
        firebase_uid = self.request.query_params.get('firebase_uid')
        session_name = self.request.query_params.get('session')

        return question_service.listar_preguntas(
            firebase_uid=firebase_uid,
            session=session_name,
        )

    @action(detail=True, methods=['patch'])
    def mark_spoken(self, request, pk=None):
        """Marca una pregunta como reproducida con voz sintética."""
        question = question_service.marcar_como_hablada(pk)
        serializer = self.get_serializer(question)
        return Response(serializer.data)
