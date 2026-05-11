from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView

from alerts.views import AlertViewSet
from transcriptions.views import TranscriptionViewSet, GroupTranscriptionViewSet

router = DefaultRouter()
router.register(r'alerts',               AlertViewSet,             basename='alerts')
router.register(r'transcriptions',       TranscriptionViewSet,     basename='transcriptions')
router.register(r'group-transcriptions', GroupTranscriptionViewSet, basename='group-transcriptions')


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'proyecto': 'Un Mundo en Silencio / IRIS',
        'version':  '3.0.0',
        'auth': {
            'register': '/api/auth/register/',
            'login':    '/api/auth/login/',
            'refresh':  '/api/auth/refresh/',
            'profile':  '/api/auth/me/',
        },
        'endpoints': {
            'preguntas':              '/api/questions/',
            'alertas':                '/api/alerts/',
            'transcripciones':        '/api/transcriptions/',
            'transcripciones_grupo':  '/api/group-transcriptions/',
        }
    })


urlpatterns = [
    path('admin/',         admin.site.urls),
    path('api/auth/',      include('users.urls')),
    path('api/',           include('questions.urls')),
    path('api/',           include(router.urls)),
    path('',               api_root, name='api-root'),
]
