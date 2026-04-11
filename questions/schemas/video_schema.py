from rest_framework import serializers
from questions.entities.video_entity import Video, Subtitle


class SubtitleSerializer(serializers.ModelSerializer):
    """Serializer para segmentos de subtítulo.

    Responsabilidad única: Define la forma de los datos
    de subtítulo en la API.
    """

    class Meta:
        model = Subtitle
        fields = [
            'id',
            'index',
            'start_time',
            'end_time',
            'text',
            'is_edited',
        ]
        read_only_fields = ['id', 'index', 'start_time', 'end_time']


class SubtitleEditSerializer(serializers.ModelSerializer):
    """Serializer para editar un subtítulo (SCRUM-43)."""

    class Meta:
        model = Subtitle
        fields = ['text']


class VideoUploadSerializer(serializers.ModelSerializer):
    """Serializer para subir un video (SCRUM-39).

    Solo recibe title, video_file, y language.
    firebase_uid se inyecta desde el header.
    """

    class Meta:
        model = Video
        fields = [
            'title',
            'video_file',
            'language',
        ]


class VideoSerializer(serializers.ModelSerializer):
    """Serializer para listar/detalle de videos.

    Incluye conteo de subtítulos y la lista completa
    de subtítulos cuando se accede al detalle.
    """
    subtitles_count = serializers.SerializerMethodField()
    subtitles = SubtitleSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = [
            'id',
            'firebase_uid',
            'title',
            'video_file',
            'duration',
            'status',
            'language',
            'error_message',
            'subtitles_count',
            'subtitles',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'firebase_uid', 'duration', 'status',
            'error_message', 'created_at', 'updated_at',
        ]

    def get_subtitles_count(self, obj):
        return obj.subtitles.count()


class VideoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar videos (sin subtítulos).

    Optimizado para no cargar todos los subtítulos en la lista.
    """
    subtitles_count = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id',
            'firebase_uid',
            'title',
            'video_file',
            'duration',
            'status',
            'language',
            'subtitles_count',
            'created_at',
        ]

    def get_subtitles_count(self, obj):
        return obj.subtitles.count()
