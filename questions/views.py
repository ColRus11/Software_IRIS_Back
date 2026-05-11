from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Question
from .serializers import QuestionSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        qs = Question.objects.filter(user=self.request.user)
        session = self.request.query_params.get('session')
        if session:
            qs = qs.filter(session_name=session)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def mark_spoken(self, request, pk=None):
        question = self.get_object()
        question.was_spoken = True
        question.save()
        return Response(self.get_serializer(question).data)
