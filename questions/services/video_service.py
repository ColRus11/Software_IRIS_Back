"""Servicio de videos — Lógica de negocio.

Responsabilidad única: Orquesta las operaciones de video
entre el repositorio y el servicio de transcripción.

SCRUM-38: Subir videos y generar subtítulos automáticos.
"""

from rest_framework.exceptions import NotFound, ValidationError

from questions.repositories import video_repository
from questions.services import transcription_service


# Extensiones de video permitidas para upload
ALLOWED_EXTENSIONS = {'.mp4', '.webm', '.mov', '.avi', '.mkv', '.m4a', '.mp3', '.wav', '.ogg'}

# Tamaño máximo de upload (en bytes): 25 MB (límite de Groq)
MAX_UPLOAD_SIZE = 25 * 1024 * 1024


def subir_video(video_file, title, firebase_uid, language='es'):
    """Sube un video y lo registra en la base de datos.

    SCRUM-39: Subir video.

    Args:
        video_file: Archivo subido (InMemoryUploadedFile).
        title: Título del video.
        firebase_uid: UID del docente.
        language: Idioma del audio.

    Returns:
        Instancia de Video creada.

    Raises:
        ValidationError: Si el archivo no es válido.
    """
    # Validar que se proporcionó un archivo
    if not video_file:
        raise ValidationError("No se proporcionó ningún archivo.")

    # Validar extensión
    import os
    ext = os.path.splitext(video_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Formato no soportado: {ext}. "
            f"Formatos permitidos: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Validar tamaño
    if video_file.size > MAX_UPLOAD_SIZE:
        size_mb = video_file.size / (1024 * 1024)
        raise ValidationError(
            f"El archivo es demasiado grande ({size_mb:.1f} MB). "
            f"Máximo permitido: {MAX_UPLOAD_SIZE // (1024 * 1024)} MB."
        )

    # Validar título
    if not title or not title.strip():
        raise ValidationError("El título es requerido.")

    # Crear registro en BD
    video = video_repository.crear_video(
        firebase_uid=firebase_uid,
        title=title.strip(),
        video_file=video_file,
        language=language,
    )

    return video


def generar_subtitulos(video_id):
    """Genera subtítulos automáticos para un video.

    SCRUM-41: Generar subtítulos.

    Flujo:
        1. Obtiene el video de la BD
        2. Cambia status a 'processing'
        3. Envía a Groq API para transcripción
        4. Guarda los segmentos como Subtitle en BD
        5. Cambia status a 'completed'

    Args:
        video_id: ID del video.

    Returns:
        Lista de instancias Subtitle creadas.

    Raises:
        NotFound: Si el video no existe.
        ValidationError: Si el video ya fue procesado.
    """
    video = video_repository.obtener_por_id(video_id)
    if not video:
        raise NotFound("El video no existe.")

    if video.status == 'processing':
        raise ValidationError("El video ya está siendo procesado.")

    # Marcar como procesando
    video_repository.actualizar_status(video_id, 'processing')

    try:
        # Obtener ruta del archivo
        file_path = video.video_file.path

        # Transcribir con Groq API
        segments = transcription_service.transcribir_archivo(
            file_path=file_path,
            language=video.language,
        )

        if not segments:
            video_repository.actualizar_status(
                video_id, 'error',
                error_message="No se detectó audio o el archivo está vacío."
            )
            raise ValidationError("No se pudo generar subtítulos. Verifica que el video tenga audio.")

        # Guardar subtítulos en BD
        subtitles = video_repository.crear_subtitulos_bulk(video_id, segments)

        # Marcar como completado
        video_repository.actualizar_status(video_id, 'completed')

        return subtitles

    except (ValueError, RuntimeError) as e:
        # Error en la transcripción
        video_repository.actualizar_status(
            video_id, 'error',
            error_message=str(e),
        )
        raise ValidationError(f"Error al generar subtítulos: {str(e)}")


def editar_subtitulo(subtitle_id, nuevo_texto):
    """Edita el texto de un subtítulo.

    SCRUM-43: Editar subtítulos.

    Args:
        subtitle_id: ID del subtítulo.
        nuevo_texto: Nuevo texto corregido.

    Returns:
        Instancia de Subtitle actualizada.

    Raises:
        NotFound: Si el subtítulo no existe.
        ValidationError: Si el texto está vacío.
    """
    if not nuevo_texto or not nuevo_texto.strip():
        raise ValidationError("El texto del subtítulo no puede estar vacío.")

    subtitle = video_repository.actualizar_subtitulo(subtitle_id, nuevo_texto.strip())
    if not subtitle:
        raise NotFound("El subtítulo no existe.")

    return subtitle


def obtener_video(video_id):
    """Obtiene un video con sus subtítulos.

    SCRUM-45: Publicar contenido.

    Args:
        video_id: ID del video.

    Returns:
        Instancia de Video.

    Raises:
        NotFound: Si el video no existe.
    """
    video = video_repository.obtener_por_id(video_id)
    if not video:
        raise NotFound("El video no existe.")
    return video


def listar_videos(firebase_uid=None):
    """Lista videos, opcionalmente filtrados por docente.

    Args:
        firebase_uid: UID del docente (opcional).

    Returns:
        QuerySet de videos.
    """
    if firebase_uid:
        return video_repository.listar_por_docente(firebase_uid)
    return video_repository.listar_todos()


def eliminar_video(video_id):
    """Elimina un video y todos sus subtítulos.

    Args:
        video_id: ID del video.

    Raises:
        NotFound: Si el video no existe.
    """
    eliminado = video_repository.eliminar(video_id)
    if not eliminado:
        raise NotFound("El video no existe.")


def exportar_srt(video_id):
    """Genera el contenido de un archivo SRT para un video.

    SCRUM-45: Publicar contenido.

    Args:
        video_id: ID del video.

    Returns:
        Tuple (filename, srt_content).

    Raises:
        NotFound: Si el video no existe.
        ValidationError: Si no hay subtítulos.
    """
    video = video_repository.obtener_por_id(video_id)
    if not video:
        raise NotFound("El video no existe.")

    subtitles = video_repository.obtener_subtitulos(video_id)
    if not subtitles.exists():
        raise ValidationError("El video no tiene subtítulos generados.")

    # Convertir subtítulos a formato de segmentos
    segments = [
        {
            'index': sub.index,
            'start_time': sub.start_time,
            'end_time': sub.end_time,
            'text': sub.text,
        }
        for sub in subtitles
    ]

    srt_content = transcription_service.generar_srt(segments)
    filename = f"{video.title.replace(' ', '_')}.srt"

    return filename, srt_content


def publicar_video(video_id):
    """Marca un video como publicado.

    SCRUM-45: Publicar contenido.

    Args:
        video_id: ID del video.

    Returns:
        Instancia de Video actualizada.

    Raises:
        NotFound: Si el video no existe.
        ValidationError: Si el video no tiene subtítulos.
    """
    video = video_repository.obtener_por_id(video_id)
    if not video:
        raise NotFound("El video no existe.")

    if video.status not in ('completed', 'published'):
        raise ValidationError(
            "El video debe tener subtítulos generados antes de publicarse."
        )

    return video_repository.actualizar_status(video_id, 'published')
