"""Vistas de Video — Endpoints HTTP.

Responsabilidad única: Manejar HTTP requests/responses.
Delega toda la lógica al servicio.

SCRUM-38: Subir videos y generar subtítulos automáticos.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from django.http import HttpResponse

from questions.schemas.video_schema import (
    VideoSerializer,
    VideoListSerializer,
    VideoUploadSerializer,
    SubtitleSerializer,
    SubtitleEditSerializer,
)
from questions.services import video_service


class VideoViewSet(viewsets.ViewSet):
    """API ViewSet para gestionar videos y subtítulos.

    Endpoints:
        POST   /api/videos/                           - Subir video (SCRUM-39)
        GET    /api/videos/                           - Listar videos
        GET    /api/videos/{id}/                       - Detalle de video
        DELETE /api/videos/{id}/                       - Eliminar video
        POST   /api/videos/{id}/generate_subtitles/    - Generar subtítulos (SCRUM-41)
        GET    /api/videos/{id}/subtitles/             - Listar subtítulos
        GET    /api/videos/{id}/download_srt/          - Descargar .srt (SCRUM-45)
        PATCH  /api/videos/{id}/publish/               - Publicar video (SCRUM-45)
    """
    parser_classes = [MultiPartParser, FormParser]

    def list(self, request):
        """GET /api/videos/ — Listar videos del docente."""
        firebase_uid = request.query_params.get('firebase_uid')
        videos = video_service.listar_videos(firebase_uid=firebase_uid)
        serializer = VideoListSerializer(videos, many=True)
        return Response(serializer.data)

    def create(self, request):
        """POST /api/videos/ — Subir un video (SCRUM-39)."""
        serializer = VideoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        firebase_uid = request.headers.get('X-Firebase-UID', '')
        if not firebase_uid:
            firebase_uid = request.data.get('firebase_uid', '')

        video = video_service.subir_video(
            video_file=serializer.validated_data['video_file'],
            title=serializer.validated_data['title'],
            firebase_uid=firebase_uid,
            language=serializer.validated_data.get('language', 'es'),
        )

        result = VideoSerializer(video)
        return Response(result.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """GET /api/videos/{id}/ — Detalle de video con subtítulos."""
        video = video_service.obtener_video(pk)
        serializer = VideoSerializer(video)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """DELETE /api/videos/{id}/ — Eliminar video."""
        video_service.eliminar_video(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def generate_subtitles(self, request, pk=None):
        """POST /api/videos/{id}/generate_subtitles/ — Generar subtítulos (SCRUM-41)."""
        subtitles = video_service.generar_subtitulos(pk)
        serializer = SubtitleSerializer(subtitles, many=True)
        return Response({
            'message': 'Subtítulos generados exitosamente.',
            'count': len(subtitles),
            'subtitles': serializer.data,
        })

    @action(detail=True, methods=['get'])
    def subtitles(self, request, pk=None):
        """GET /api/videos/{id}/subtitles/ — Listar subtítulos."""
        video = video_service.obtener_video(pk)
        from questions.repositories import video_repository
        subs = video_repository.obtener_subtitulos(pk)
        serializer = SubtitleSerializer(subs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def download_srt(self, request, pk=None):
        """GET /api/videos/{id}/download_srt/ — Descargar archivo .srt (SCRUM-45)."""
        filename, srt_content = video_service.exportar_srt(pk)

        response = HttpResponse(srt_content, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(detail=True, methods=['patch'])
    def publish(self, request, pk=None):
        """PATCH /api/videos/{id}/publish/ — Publicar video (SCRUM-45)."""
        video = video_service.publicar_video(pk)
        serializer = VideoSerializer(video)
        return Response({
            'message': 'Video publicado exitosamente.',
            'video': serializer.data,
        })


class SubtitleViewSet(viewsets.ViewSet):
    """API ViewSet para editar subtítulos individuales.

    Endpoints:
        PATCH /api/subtitles/{id}/ — Editar subtítulo (SCRUM-43)
    """

    def partial_update(self, request, pk=None):
        """PATCH /api/subtitles/{id}/ — Editar texto de un subtítulo (SCRUM-43)."""
        serializer = SubtitleEditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subtitle = video_service.editar_subtitulo(
            subtitle_id=pk,
            nuevo_texto=serializer.validated_data['text'],
        )

        result = SubtitleSerializer(subtitle)
        return Response(result.data)
