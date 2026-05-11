from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile
from .serializers import UserProfileSerializer


def _token_response(user, profile):
    """Genera la respuesta JWT estándar con datos de perfil."""
    refresh = RefreshToken.for_user(user)
    return {
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id':          user.id,
            'email':       user.email,
            'name':        profile.display_name if profile else user.get_full_name(),
            'role':        profile.role if profile else 'Student',
            'university':  profile.university if profile else '',
        }
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """POST /api/auth/register/"""
    email      = request.data.get('email', '').strip().lower()
    password   = request.data.get('password', '')
    name       = request.data.get('name', '').strip()
    role       = request.data.get('role', 'Student')
    university = request.data.get('university', '').strip()

    if not email or not password or not name:
        return Response({'error': 'Nombre, correo y contraseña son requeridos.'}, status=400)

    if len(password) < 6:
        return Response({'error': 'La contraseña debe tener al menos 6 caracteres.'}, status=400)

    if role not in ('Student', 'Teacher', 'Admin'):
        return Response({'error': 'Rol inválido.'}, status=400)

    if User.objects.filter(username=email).exists():
        return Response({'error': 'Este correo ya está registrado.'}, status=400)

    parts = name.split(maxsplit=1)
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=parts[0],
        last_name=parts[1] if len(parts) > 1 else '',
    )

    profile = UserProfile.objects.create(
        user=user,
        display_name=name,
        role=role,
        university=university,
    )

    return Response(_token_response(user, profile), status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """POST /api/auth/login/"""
    email    = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    if not email or not password:
        return Response({'error': 'Correo y contraseña son requeridos.'}, status=400)

    user = authenticate(username=email, password=password)
    if not user:
        return Response({'error': 'Credenciales inválidas.'}, status=401)

    profile = getattr(user, 'userprofile', None)
    return Response(_token_response(user, profile))


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me(request):
    """GET|PATCH /api/auth/me/"""
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'display_name': request.user.get_full_name(), 'role': 'Student'}
    )
    if request.method == 'GET':
        return Response(UserProfileSerializer(profile).data)

    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)
