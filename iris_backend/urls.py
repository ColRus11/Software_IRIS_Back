from django.contrib import admin
from django.urls import path, include
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
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('questions.urls')),
    path('', api_root, name='api-root'),
]
