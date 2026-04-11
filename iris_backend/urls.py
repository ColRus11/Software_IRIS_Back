from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def api_root(request):
    """Endpoint raíz de la API IRIS."""
    return Response({
        'proyecto': 'IRIS - Inclusión en Red e Integración Social',
        'version': '1.0.0',
        'endpoints': {
            'preguntas': '/api/questions/',
            'videos': '/api/videos/',
            'subtitulos': '/api/subtitles/',
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('questions.urls')),
    path('', api_root, name='api-root'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
