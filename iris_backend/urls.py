from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.views import UserProfileViewSet
from alerts.views import AlertViewSet
from transcriptions.views import TranscriptionViewSet

router = DefaultRouter()
router.register(r'users',          UserProfileViewSet,  basename='users')
router.register(r'alerts',         AlertViewSet,        basename='alerts')
router.register(r'transcriptions', TranscriptionViewSet, basename='transcriptions')


@api_view(['GET'])
def api_root(request):
    return Response({
        'proyecto': 'Un Mundo en Silencio / IRIS',
        'version': '2.0.0',
        'endpoints': {
            'preguntas':       '/api/questions/',
            'alertas':         '/api/alerts/',
            'transcripciones': '/api/transcriptions/',
            'perfil_usuario':  '/api/users/profile/',
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('questions.urls')),
    path('api/', include(router.urls)),
    path('', api_root, name='api-root'),
]
