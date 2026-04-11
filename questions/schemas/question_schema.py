from rest_framework import serializers
from questions.entities.question_entity import Question


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Question.

    Responsabilidad única: Define la forma de los datos
    en la API (DTO de entrada/salida).
    """

    class Meta:
        model = Question
        fields = [
            'id',
            'firebase_uid',
            'text',
            'session_name',
            'was_spoken',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
